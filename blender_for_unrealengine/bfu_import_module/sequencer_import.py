# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import Dict, Any, List, Tuple
import unreal
from . import bpl
from . import import_module_utils
from . import import_module_unreal_utils
from . import sequencer_utils


def ready_for_sequence_import():
    if not import_module_unreal_utils.editor_scripting_utilities_active():
        message = 'WARNING: Editor Scripting Utilities Plugin should be activated.' + "\n"
        message += 'Edit > Plugin > Scripting > Editor Scripting Utilities.'
        import_module_unreal_utils.show_warning_message("Editor Scripting Utilities not activated.", message)
        return False
    
    if not import_module_unreal_utils.sequencer_scripting_active():
        message = 'WARNING: Sequencer Scripting Plugin should be activated.' + "\n"
        message += 'Edit > Plugin > Scripting > Sequencer Scripting.'
        import_module_unreal_utils.show_warning_message("Sequencer Scripting not activated.", message)
        return False
    return True

def create_sequencer(sequence_data: Dict[str, Any], show_finished_popup: bool = True):

    is_spawnable_camera = sequence_data['spawnable_camera']
    sequencer_frame_start = sequence_data['sequencer_frame_start']
    sequencer_frame_end = sequence_data['sequencer_frame_end']+1
    render_resolution_x = sequence_data['render_resolution_x']
    render_resolution_y = sequence_data['render_resolution_y']
    sequencer_frame_rate_denominator = sequence_data['sequencer_frame_rate_denominator']
    sequencer_frame_rate_numerator = sequence_data['sequencer_frame_rate_numerator']
    secure_crop = sequence_data['secure_crop']  # add end crop for avoid section overlay
    imported_cameras: List[Tuple[str, unreal.MovieSceneObjectBindingID]] = []  # (CameraName, CameraGuid)

    seq = sequencer_utils.create_new_sequence()
    print("Sequencer reference created", seq)

    # Process import
    bpl.advprint.print_simple_title("Import started !")

    # Set frame rate
    myFFrameRate = sequencer_utils.get_sequencer_framerate(
        denominator = sequencer_frame_rate_denominator, 
        numerator = sequencer_frame_rate_numerator
        )
    seq.set_display_rate(myFFrameRate)

    # Set playback range
    seq.set_playback_end_seconds((sequencer_frame_end-secure_crop)/float(sequencer_frame_rate_numerator))
    seq.set_playback_start_seconds(sequencer_frame_start/float(sequencer_frame_rate_numerator))  # set_playback_end_seconds
    if import_module_unreal_utils.get_unreal_version() > (5,2,0):
        camera_cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    else:
        camera_cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)

    camera_cut_track.set_editor_property('display_name', 'Imported Camera Cuts')
    if import_module_unreal_utils.get_unreal_version() >= (4,26,0):
        camera_cut_track.set_color_tint(unreal.Color(b=200, g=0, r=0, a=0))
    else:
        pass

    for x, camera_data in enumerate(sequence_data["cameras"]):
        # import camera
        print("Start camera import " + str(x+1) + "/" + str(len(sequence_data["cameras"])) + " :" + camera_data["asset_name"])
        # Import camera tracks transform
        imported_cameras.append(import_camera_asset(seq, camera_data, is_spawnable_camera))



    # Import camera cut section
    for section in sequence_data['marker_sections']:
        camera_cut_section = camera_cut_track.add_section()
        if section["has_camera"] is not None:
            for camera in imported_cameras:
                if camera[0] == section["camera_name"]:
                    camera_binding_id = unreal.MovieSceneObjectBindingID()
                    if import_module_unreal_utils.get_unreal_version() >= (5,3,0):
                        camera_binding_id = seq.get_binding_id(camera[1])
                    elif import_module_unreal_utils.get_unreal_version() >= (4,27,0):
                        camera_binding_id = seq.get_portable_binding_id(seq, camera[1])
                    elif import_module_unreal_utils.get_unreal_version() >= (4,26,0):
                        camera_binding_id = seq.make_binding_id(camera[1], unreal.MovieSceneObjectBindingSpace.LOCAL)
                    else:
                        camera_binding_id = seq.make_binding_id(camera[1])
                    camera_cut_section.set_camera_binding_id(camera_binding_id)

        camera_cut_section.set_end_frame_seconds((section["end_time"]-secure_crop)/float(sequencer_frame_rate_numerator))
        camera_cut_section.set_start_frame_seconds(section["start_time"]/float(sequencer_frame_rate_numerator))
    # Import result

    bpl.advprint.print_simple_title("Imports completed !")
    ImportedCameraStr = []
    for cam in imported_cameras:
        ImportedCameraStr.append(cam[0])
        print(ImportedCameraStr)
        bpl.advprint.print_separator()

    # Select and open seq in content browser
    if import_module_unreal_utils.get_unreal_version() >= (5,0,0):
        pass #TO DO make crate the engine
        #unreal.AssetEditorSubsystem.open_editor_for_assets(unreal.AssetEditorSubsystem(), [unreal.load_asset(seq.get_path_name())])
    elif import_module_unreal_utils.get_unreal_version() >= (4,26,0):
        unreal.AssetEditorSubsystem.open_editor_for_assets(unreal.AssetEditorSubsystem(), [unreal.load_asset(seq.get_path_name())])
    else:
        unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets([unreal.load_asset(seq.get_path_name())])

    unreal.EditorAssetLibrary.sync_browser_to_objects([seq.get_path_name()])
    return 'Sequencer created with success !'

def import_camera_asset(seq: unreal.LevelSequence, camera_data: Dict[str, Any], is_spawnable_camera: bool) -> Tuple[str, unreal.MovieSceneObjectBindingID]:

    def found_additional_data() -> Dict[str, Any]:
        files: List[Dict[str, Any]] = camera_data["files"]
        for file in files:
            if file["content_type"] == "ADDITIONAL_DATA":
                return import_module_utils.json_load_file(Path(file["file_path"]))
        return {}

    camera_additional_data = found_additional_data()
    camera_name: str = camera_additional_data["camera_name"]
    camera_target_class_ref: str = camera_additional_data["camera_actor"]

    camera_target_class = unreal.load_class(None, camera_target_class_ref)
    if camera_target_class is None:
        message = f'WARNING: The camera class {camera_target_class_ref} was not found!' + "\n"
        message += 'Verify that the class exists or that you have activated the necessary plugins.'
        import_module_unreal_utils.show_warning_message("Failed to find camera class.", message)
        camera_target_class = unreal.CineCameraActor

    camera_binding, camera_component_binding = sequencer_utils.Sequencer_add_new_camera(seq, camera_target_class, camera_name, is_spawnable_camera)
    sequencer_utils.update_sequencer_camera_tracks(seq, camera_binding, camera_component_binding, camera_additional_data)
    return (camera_name, camera_binding)