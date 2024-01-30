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
from . import bps
from . import import_module_utils
from . import import_module_unreal_utils

try:
    import unreal
except ImportError:
    import unreal_engine as unreal





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

    spawnable_camera = sequence_data['spawnable_camera']
    startFrame = sequence_data['startFrame']
    endFrame = sequence_data['endFrame']+1
    render_resolution_x = sequence_data['render_resolution_x']
    render_resolution_y = sequence_data['render_resolution_y']
    frameRateDenominator = sequence_data['frameRateDenominator']
    frameRateNumerator = sequence_data['frameRateNumerator']
    secureCrop = sequence_data['secureCrop']  # add end crop for avoid section overlay
    bfu_unreal_import_location = sequence_data['bfu_unreal_import_location']
    ImportedCamera = []  # (CameraName, CameraGuid)

    def AddSequencerSectionTransformKeysByIniFile(sequencer_section, track_dict):
        for key in track_dict.keys():
            value = track_dict[key]  # (x,y,z x,y,z x,y,z)
            frame = unreal.FrameNumber(int(key))

            if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,0):
                sequencer_section.get_all_channels()[0].add_key(frame, value["location_x"])
                sequencer_section.get_all_channels()[1].add_key(frame, value["location_y"])
                sequencer_section.get_all_channels()[2].add_key(frame, value["location_z"])
                sequencer_section.get_all_channels()[3].add_key(frame, value["rotation_x"])
                sequencer_section.get_all_channels()[4].add_key(frame, value["rotation_y"])
                sequencer_section.get_all_channels()[5].add_key(frame, value["rotation_z"])
                sequencer_section.get_all_channels()[6].add_key(frame, value["scale_x"])
                sequencer_section.get_all_channels()[7].add_key(frame, value["scale_y"])
                sequencer_section.get_all_channels()[8].add_key(frame, value["scale_z"])
            else:
                sequencer_section.get_channels()[0].add_key(frame, value["location_x"])
                sequencer_section.get_channels()[1].add_key(frame, value["location_y"])
                sequencer_section.get_channels()[2].add_key(frame, value["location_z"])
                sequencer_section.get_channels()[3].add_key(frame, value["rotation_x"])
                sequencer_section.get_channels()[4].add_key(frame, value["rotation_y"])
                sequencer_section.get_channels()[5].add_key(frame, value["rotation_z"])
                sequencer_section.get_channels()[6].add_key(frame, value["scale_x"])
                sequencer_section.get_channels()[7].add_key(frame, value["scale_y"])
                sequencer_section.get_channels()[8].add_key(frame, value["scale_z"])

    def AddSequencerSectionFloatKeysByIniFile(sequencer_section, track_dict):
        for key in track_dict.keys():
            frame = unreal.FrameNumber(int(key))
            value = track_dict[key]
            if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,0):
                sequencer_section.get_all_channels()[0].add_key(frame, value)
            else:
                sequencer_section.get_channels()[0].add_key(frame, value)

    def AddSequencerSectionBoolKeysByIniFile(sequencer_section, track_dict):
        for key in track_dict.keys():
            frame = unreal.FrameNumber(int(key))
            value = track_dict[key]
            if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,0):
                sequencer_section.get_all_channels()[0].add_key(frame, value)
            else:
                sequencer_section.get_channels()[0].add_key(frame, value)

    print("Warning this file already exists")  # ???
    factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = asset_tools.create_asset_with_dialog('MySequence', '/Game', None, factory)
    if seq is None:
        return 'ERROR: level sequencer factory_create fail'

    print("Sequencer reference created", seq)

    # Process import
    print("========================= Import started ! =========================")

    # Set frame rate
    myFFrameRate = unreal.FrameRate()
    myFFrameRate.denominator = frameRateDenominator
    myFFrameRate.numerator = frameRateNumerator
    seq.set_display_rate(myFFrameRate)

    # Set playback range
    seq.set_playback_end_seconds((endFrame-secureCrop)/float(frameRateNumerator))
    seq.set_playback_start_seconds(startFrame/float(frameRateNumerator))  # set_playback_end_seconds
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

        # Create spawnable camera and add camera in sequencer
        cine_camera_actor = unreal.EditorLevelLibrary().spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))

        # Import additional tracks (camera_component)
        camera_component_binding = seq.add_possessable(cine_camera_actor.get_cine_camera_component())
        # Get the last

        TrackFocalLength = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TrackFocalLength.set_property_name_and_path('CurrentFocalLength', 'CurrentFocalLength')
        TrackFocalLength.set_editor_property('display_name', 'Current Focal Length')
        sectionFocalLength = TrackFocalLength.add_section()
        sectionFocalLength.set_end_frame_bounded(False)
        sectionFocalLength.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, camera_tracks['camera_focal_length'])

        TrackSensorWidth = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TrackSensorWidth.set_property_name_and_path('Filmback.SensorWidth', 'Filmback.SensorWidth')
        TrackSensorWidth.set_editor_property('display_name', 'Sensor Width (Filmback)')
        sectionSensorWidth = TrackSensorWidth.add_section()
        sectionSensorWidth.set_end_frame_bounded(False)
        sectionSensorWidth.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionSensorWidth, camera_tracks['ue_camera_sensor_width'])

        TrackSensorHeight = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TrackSensorHeight.set_property_name_and_path('Filmback.SensorHeight', 'Filmback.SensorHeight')
        TrackSensorHeight.set_editor_property('display_name', 'Sensor Height (Filmback)')
        sectionSensorHeight = TrackSensorHeight.add_section()
        sectionSensorHeight.set_end_frame_bounded(False)
        sectionSensorHeight.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionSensorHeight, camera_tracks['ue_camera_sensor_height'])

        TrackFocusDistance = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)

        if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,24):
            TrackFocusDistance.set_property_name_and_path('FocusSettings.ManualFocusDistance', 'FocusSettings.ManualFocusDistance')
            TrackFocusDistance.set_editor_property('display_name', 'Manual Focus Distance (Focus Settings)')
        else:
            TrackFocusDistance.set_property_name_and_path('ManualFocusDistance', 'ManualFocusDistance')
            TrackFocusDistance.set_editor_property('display_name', 'Current Focus Distance')

        sectionFocusDistance = TrackFocusDistance.add_section()
        sectionFocusDistance.set_end_frame_bounded(False)
        sectionFocusDistance.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, camera_tracks['camera_focus_distance'])

        TracknAperture = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TracknAperture.set_property_name_and_path('CurrentAperture', 'CurrentAperture')
        TracknAperture.set_editor_property('display_name', 'Current Aperture')
        sectionAperture = TracknAperture.add_section()
        sectionAperture.set_end_frame_bounded(False)
        sectionAperture.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionAperture, camera_tracks['camera_aperture'])

        # add a binding for the camera
        camera_binding = seq.add_possessable(cine_camera_actor)

        if spawnable_camera:
            # Transfer to spawnable camera
            camera_spawnable = seq.add_spawnable_from_class(unreal.CineCameraActor)  # Add camera in sequencer
            camera_component_binding.set_parent(camera_spawnable)

        # Import transform tracks
        if spawnable_camera:
            transform_track = camera_spawnable.add_track(unreal.MovieScene3DTransformTrack)
        else:
            transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
        transform_section = transform_track.add_section()
        transform_section.set_end_frame_bounded(False)
        transform_section.set_start_frame_bounded(False)
        AddSequencerSectionTransformKeysByIniFile(transform_section, camera_tracks['ue_camera_transform'])

        # Set property binding
        if spawnable_camera:
            current_camera_binding = camera_spawnable
        else:
            current_camera_binding = camera_binding

        if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,26):
            current_camera_binding.set_display_name(camera_data["name"])
        else:
            pass
        tracksSpawned = current_camera_binding.find_tracks_by_exact_type(unreal.MovieSceneSpawnTrack)
        if len(tracksSpawned) > 0:
            sectionSpawned = tracksSpawned[0].get_sections()[0]
            AddSequencerSectionBoolKeysByIniFile(sectionSpawned, camera_tracks['camera_spawned'])

        # Set property actor
        if spawnable_camera:
            current_cine_camera_actor = camera_spawnable.get_object_template()
        else:
            current_cine_camera_actor = cine_camera_actor

        current_cine_camera_actor.set_actor_label(camera_data["name"])
        camera_component = cine_camera_actor.camera_component
        camera_component.aspect_ratio = render_resolution_x/render_resolution_y
        camera_component.lens_settings.min_f_stop = camera_tracks['ue_lens_minfstop']
        camera_component.lens_settings.max_f_stop = camera_tracks['ue_lens_maxfstop']

        # Clean the created assets
        if spawnable_camera:
            cine_camera_actor.destroy_actor()
            camera_binding.remove()

        if spawnable_camera:
            ImportedCamera.append((camera_data["name"], camera_spawnable))
        else:
            ImportedCamera.append((camera_data["name"], camera_binding))


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

        camera_cut_section.set_end_frame_seconds((section["end_time"]-secureCrop)/float(frameRateNumerator))
        camera_cut_section.set_start_frame_seconds(section["start_time"]/float(frameRateNumerator))
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

