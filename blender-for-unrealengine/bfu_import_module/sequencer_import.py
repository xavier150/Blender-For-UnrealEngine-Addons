# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

import os.path
try:
    import unreal
except ImportError:
    import unreal_engine as unreal
from . import bps
from . import import_module_utils
from . import import_module_unreal_utils
from . import sequencer_utils







def ready_for_sequence_import():
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,20):  # TO DO: EditorAssetLibrary was added in witch version exactly?
        if not hasattr(unreal, 'EditorAssetLibrary'):
            message = 'WARNING: Editor Scripting Utilities should be activated.' + "\n"
            message += 'Edit > Plugin > Scripting > Editor Scripting Utilities.'
            import_module_unreal_utils.show_warning_message("Editor Scripting Utilities not activated.", message)
            return False
    if not hasattr(unreal.MovieSceneSequence, 'set_display_rate'):
        message = 'WARNING: Editor Scripting Utilities should be activated.' + "\n"
        message += 'Edit > Plugin > Scripting > Sequencer Scripting.'
        import_module_unreal_utils.show_warning_message("Editor Scripting Utilities not activated.", message)
        return False
    return True

def CreateSequencer(sequence_data, show_finished_popup=True):

    
    is_spawnable_camera = sequence_data['spawnable_camera']
    sequencer_frame_start = sequence_data['sequencer_frame_start']
    sequencer_frame_end = sequence_data['sequencer_frame_end']+1
    render_resolution_x = sequence_data['render_resolution_x']
    render_resolution_y = sequence_data['render_resolution_y']
    sequencer_frame_rate_denominator = sequence_data['sequencer_frame_rate_denominator']
    sequencer_frame_rate_numerator = sequence_data['sequencer_frame_rate_numerator']
    secureCrop = sequence_data['secureCrop']  # add end crop for avoid section overlay
    bfu_unreal_import_location = sequence_data['bfu_unreal_import_location']
    ImportedCamera = []  # (CameraName, CameraGuid)

    seq = sequencer_utils.create_new_sequence()

    print("Sequencer reference created", seq)

    # Process import
    print("========================= Import started ! =========================")

    # Set frame rate
    myFFrameRate = sequencer_utils.get_sequencer_framerate(
        denominator = sequencer_frame_rate_denominator, 
        numerator = sequencer_frame_rate_numerator
        )
    seq.set_display_rate(myFFrameRate)

    # Set playback range
    seq.set_playback_end_seconds((sequencer_frame_end-secureCrop)/float(sequencer_frame_rate_numerator))
    seq.set_playback_start_seconds(sequencer_frame_start/float(sequencer_frame_rate_numerator))  # set_playback_end_seconds
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,2):
        camera_cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    else:
        camera_cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)

    camera_cut_track.set_editor_property('display_name', 'Imported Camera Cuts')
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,26):
        camera_cut_track.set_color_tint(unreal.Color(b=200, g=0, r=0, a=0))
    else:
        pass

    for x, camera_data in enumerate(sequence_data["cameras"]):
        # import camera
        print("Start camera import " + str(x+1) + "/" + str(len(sequence_data["cameras"])) + " :" + camera_data["name"])
        # Import camera tracks transform
        camera_tracks = import_module_utils.JsonLoadFile(camera_data["additional_tracks_path"])


        camera_name = camera_data["name"]
        camera_target_class_ref = camera_tracks["camera_actor"]
        
        camera_target_class = unreal.load_class(None, camera_target_class_ref)
        if camera_target_class is None:
            message = f'WARNING: The camera class {camera_target_class_ref} was not found!' + "\n"
            message += 'Verify that the class exists or that you have activated the necessary plugins.'
            import_module_unreal_utils.show_warning_message("Failed to find camera class.", message)

        camera_binding, camera_component_binding = sequencer_utils.Sequencer_add_new_camera(seq, camera_target_class, camera_name, is_spawnable_camera)
        sequencer_utils.update_sequencer_camera_tracks(seq, camera_binding, camera_component_binding, camera_tracks)
        ImportedCamera.append((camera_name, camera_binding))


    # Import camera cut section
    for section in sequence_data['marker_sections']:
        camera_cut_section = camera_cut_track.add_section()
        if section["has_camera"] is not None:
            for camera in ImportedCamera:
                if camera[0] == section["camera_name"]:
                    camera_binding_id = unreal.MovieSceneObjectBindingID()
                    if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,3):
                        camera_binding_id = seq.get_binding_id(camera[1])
                    elif import_module_unreal_utils.is_unreal_version_greater_or_equal(4,27):
                        camera_binding_id = seq.get_portable_binding_id(seq, camera[1])
                    elif import_module_unreal_utils.is_unreal_version_greater_or_equal(4,26):
                        camera_binding_id = seq.make_binding_id(camera[1], unreal.MovieSceneObjectBindingSpace.LOCAL)
                    else:
                        camera_binding_id = seq.make_binding_id(camera[1])
                    camera_cut_section.set_camera_binding_id(camera_binding_id)

        camera_cut_section.set_end_frame_seconds((section["end_time"]-secureCrop)/float(sequencer_frame_rate_numerator))
        camera_cut_section.set_start_frame_seconds(section["start_time"]/float(sequencer_frame_rate_numerator))
    # Import result

    print('========================= Imports completed ! =========================')
    ImportedCameraStr = []
    for cam in ImportedCamera:
        ImportedCameraStr.append(cam[0])
        print(ImportedCameraStr)
        print('=========================')

    # Select and open seq in content browser
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,0):
        pass #TO DO make crate the engine
        #unreal.AssetEditorSubsystem.open_editor_for_assets(unreal.AssetEditorSubsystem(), [unreal.load_asset(seq.get_path_name())])
    elif import_module_unreal_utils.is_unreal_version_greater_or_equal(4,26):
        unreal.AssetEditorSubsystem.open_editor_for_assets(unreal.AssetEditorSubsystem(), [unreal.load_asset(seq.get_path_name())])
    else:
        unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets([unreal.load_asset(seq.get_path_name())])

    unreal.EditorAssetLibrary.sync_browser_to_objects([seq.get_path_name()])
    return 'Sequencer created with success !'

