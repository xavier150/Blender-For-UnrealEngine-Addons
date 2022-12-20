# This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose
# The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python
# Use this command in Unreal cmd consol: py "[ScriptLocation]\ImportSequencerScript.py"

import sys
import os.path
import json

try:  # TO DO: Found a better way to check that.
    import unreal
except ImportError:
    import unreal_engine as unreal


def CheckTasks():

    if GetUnrealVersion() >= 4.20:  # TO DO: EditorAssetLibrary was added in witch version exactly?
        if not hasattr(unreal, 'EditorAssetLibrary'):
            print('--------------------------------------------------')
            print('WARNING: Editor Scripting Utilities should be activated.')
            print('Edit > Plugin > Scripting > Editor Scripting Utilities.')
            return False
    if not hasattr(unreal.MovieSceneSequence, 'set_display_rate'):
        print('--------------------------------------------------')
        print('WARNING: Editor Scripting Utilities should be activated.')
        print('Edit > Plugin > Scripting > Sequencer Scripting.')
        return False
    return True


def JsonLoad(json_file):
    # Changed in Python 3.9: The keyword argument encoding has been removed.
    if sys.version_info >= (3, 9):
        return json.load(json_file)
    else:
        return json.load(json_file, encoding="utf8")


def JsonLoadFile(json_file_path):
    if sys.version_info[0] < 3:
        with open(json_file_path, "r") as json_file:
            return JsonLoad(json_file)
    else:
        with open(json_file_path, "r", encoding="utf8") as json_file:
            return JsonLoad(json_file)


def GetUnrealVersion():
    version = unreal.SystemLibrary.get_engine_version().split(".")
    float_version = int(version[0]) + float(float(version[1])/100)
    return float_version


def CreateSequencer():

    # Prepare process import
    json_data_file = 'ImportSequencerData.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))

    sequence_data = JsonLoadFile(os.path.join(dir_path, json_data_file))

    spawnable_camera = sequence_data['spawnable_camera']
    startFrame = sequence_data['startFrame']
    endFrame = sequence_data['endFrame']+1
    render_resolution_x = sequence_data['render_resolution_x']
    render_resolution_y = sequence_data['render_resolution_y']
    frameRateDenominator = sequence_data['frameRateDenominator']
    frameRateNumerator = sequence_data['frameRateNumerator']
    secureCrop = sequence_data['secureCrop']  # add end crop for avoid section overlay
    unreal_import_location = sequence_data['unreal_import_location']
    ImportedCamera = []  # (CameraName, CameraGuid)

    def AddSequencerSectionTransformKeysByIniFile(sequencer_section, track_dict):
        for key in track_dict.keys():
            value = track_dict[key]  # (x,y,z x,y,z x,y,z)
            frame = unreal.FrameNumber(int(key))

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
            sequencer_section.get_channels()[0].add_key(frame, value)

    def AddSequencerSectionBoolKeysByIniFile(sequencer_section, track_dict):
        for key in track_dict.keys():
            frame = unreal.FrameNumber(int(key))
            value = track_dict[key]
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
    camera_cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_track.set_editor_property('display_name', 'Imported Camera Cuts')
    if GetUnrealVersion() >= 4.26:
        camera_cut_track.set_color_tint(unreal.Color(b=200, g=0, r=0, a=0))
    else:
        pass

    for x, camera_data in enumerate(sequence_data["cameras"]):
        # import camera
        print("Start camera import " + str(x+1) + "/" + str(len(sequence_data["cameras"])) + " :" + camera_data["name"])
        # Import camera tracks transform
        camera_tracks = JsonLoadFile(camera_data["additional_tracks_path"])

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
        AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, camera_tracks['Camera FocalLength'])

        TrackSensorWidth = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TrackSensorWidth.set_property_name_and_path('Filmback.SensorWidth', 'Filmback.SensorWidth')
        TrackSensorWidth.set_editor_property('display_name', 'Sensor Width (Filmback)')
        sectionSensorWidth = TrackSensorWidth.add_section()
        sectionSensorWidth.set_end_frame_bounded(False)
        sectionSensorWidth.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionSensorWidth, camera_tracks['Camera SensorWidth'])

        TrackSensorHeight = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TrackSensorHeight.set_property_name_and_path('Filmback.SensorHeight', 'Filmback.SensorHeight')
        TrackSensorHeight.set_editor_property('display_name', 'Sensor Height (Filmback)')
        sectionSensorHeight = TrackSensorHeight.add_section()
        sectionSensorHeight.set_end_frame_bounded(False)
        sectionSensorHeight.set_start_frame_bounded(False)

        crop_camera_sensor_height = {}
        for key in camera_tracks['Camera SensorHeight'].keys():
            original_width = float(camera_tracks['Camera SensorWidth'][key])
            original_height = float(camera_tracks['Camera SensorHeight'][key])
            res_x = float(sequence_data['render_resolution_x'])
            res_y = float(sequence_data['render_resolution_y'])
            pixel_x = float(sequence_data['pixel_aspect_x'])
            pixel_y = float(sequence_data['pixel_aspect_y'])
            res_ratio = res_x / res_y
            pixel_ratio = pixel_x / pixel_y

            crop_camera_sensor_height[key] = (original_width / (res_ratio * pixel_ratio))

        AddSequencerSectionFloatKeysByIniFile(sectionSensorHeight, crop_camera_sensor_height)

        TrackFocusDistance = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)

        if GetUnrealVersion() >= 4.24:
            TrackFocusDistance.set_property_name_and_path('FocusSettings.ManualFocusDistance', 'FocusSettings.ManualFocusDistance')
            TrackFocusDistance.set_editor_property('display_name', 'Manual Focus Distance (Focus Settings)')
        else:
            print(GetUnrealVersion())
            TrackFocusDistance.set_property_name_and_path('ManualFocusDistance', 'ManualFocusDistance')
            TrackFocusDistance.set_editor_property('display_name', 'Current Focus Distance')

        sectionFocusDistance = TrackFocusDistance.add_section()
        sectionFocusDistance.set_end_frame_bounded(False)
        sectionFocusDistance.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, camera_tracks['Camera FocusDistance'])

        TracknAperture = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        TracknAperture.set_property_name_and_path('CurrentAperture', 'CurrentAperture')
        TracknAperture.set_editor_property('display_name', 'Current Aperture')
        sectionAperture = TracknAperture.add_section()
        sectionAperture.set_end_frame_bounded(False)
        sectionAperture.set_start_frame_bounded(False)
        AddSequencerSectionFloatKeysByIniFile(sectionAperture, camera_tracks['Camera Aperture'])

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
        AddSequencerSectionTransformKeysByIniFile(transform_section, camera_tracks['Camera transform'])

        # Set property binding
        if spawnable_camera:
            current_camera_binding = camera_spawnable
        else:
            current_camera_binding = camera_binding

        if GetUnrealVersion() >= 4.26:
            current_camera_binding.set_display_name(camera_data["name"])
        else:
            pass
        tracksSpawned = current_camera_binding.find_tracks_by_exact_type(unreal.MovieSceneSpawnTrack)
        if len(tracksSpawned) > 0:
            sectionSpawned = tracksSpawned[0].get_sections()[0]
            AddSequencerSectionBoolKeysByIniFile(sectionSpawned, camera_tracks['Camera Spawned'])

        # Set property actor
        if spawnable_camera:
            current_cine_camera_actor = camera_spawnable.get_object_template()
        else:
            current_cine_camera_actor = cine_camera_actor

        current_cine_camera_actor.set_actor_label(camera_data["name"])
        camera_component = cine_camera_actor.camera_component
        camera_component.aspect_ratio = render_resolution_x/render_resolution_y
        camera_component.lens_settings.min_f_stop = 0
        camera_component.lens_settings.max_f_stop = 1000

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
                    if GetUnrealVersion() >= 4.26:
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
    if GetUnrealVersion() >= 4.26:
        unreal.AssetEditorSubsystem.open_editor_for_assets(unreal.AssetEditorSubsystem(), [unreal.load_asset(seq.get_path_name())])
    else:
        unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets([unreal.load_asset(seq.get_path_name())])

    unreal.EditorAssetLibrary.sync_browser_to_objects([seq.get_path_name()])
    return 'Sequencer created with success !'


print("Start importing sequencer.")

if CheckTasks():
    print(CreateSequencer())

print("Importing sequencer finished.")
