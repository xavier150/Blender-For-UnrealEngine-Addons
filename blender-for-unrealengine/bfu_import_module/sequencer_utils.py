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

try:
    import unreal
except ImportError:
    import unreal_engine as unreal
from . import import_module_utils
from . import import_module_unreal_utils

from typing import Dict, Any

def get_section_all_channel(section: unreal.MovieSceneSection): 
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,0):
        return section.get_all_channels()
    else:
        return section.get_channels()

def AddSequencerSectionTransformKeysByIniFile(section: unreal.MovieSceneSection, track_dict: Dict[str, Any]):
    for key in track_dict.keys():
        value = track_dict[key]  # (x,y,z x,y,z x,y,z)
        frame = unreal.FrameNumber(int(key))

        get_section_all_channel(section)[0].add_key(frame, value["location_x"])
        get_section_all_channel(section)[1].add_key(frame, value["location_y"])
        get_section_all_channel(section)[2].add_key(frame, value["location_z"])
        get_section_all_channel(section)[3].add_key(frame, value["rotation_x"])
        get_section_all_channel(section)[4].add_key(frame, value["rotation_y"])
        get_section_all_channel(section)[5].add_key(frame, value["rotation_z"])
        get_section_all_channel(section)[6].add_key(frame, value["scale_x"])
        get_section_all_channel(section)[7].add_key(frame, value["scale_y"])
        get_section_all_channel(section)[8].add_key(frame, value["scale_z"])


def AddSequencerSectionDoubleVectorKeysByIniFile(section, track_dict: Dict[str, Any]):
    for key in track_dict.keys():
        value = track_dict[key]  # (x,y,z x,y,z x,y,z)
        frame = unreal.FrameNumber(int(key))

        get_section_all_channel(section)[0].add_key(frame, value["x"])
        get_section_all_channel(section)[1].add_key(frame, value["y"])

def AddSequencerSectionFloatKeysByIniFile(section, track_dict: Dict[str, Any]):
    for key in track_dict.keys():
        frame = unreal.FrameNumber(int(key))
        value = track_dict[key]

        get_section_all_channel(section)[0].add_key(frame, value)


def AddSequencerSectionBoolKeysByIniFile(section, track_dict: Dict[str, Any]):
    for key in track_dict.keys():
        frame = unreal.FrameNumber(int(key))
        value = track_dict[key]

        get_section_all_channel(section)[0].add_key(frame, value)


def create_new_sequence():
    factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = asset_tools.create_asset_with_dialog('MySequence', '/Game', None, factory)
    if seq is None:
        return 'ERROR: level sequencer factory_create fail'
    return seq

def Sequencer_add_new_camera(seq: unreal.LevelSequence, camera_target_class = unreal.CineCameraActor, camera_name = "MyCamera", is_spawnable_camera = False) -> unreal.MovieSceneBindingProxy:



    #Create bindings
    if is_spawnable_camera:
        # Create spawnable camera
        camera_binding = seq.add_spawnable_from_class(camera_target_class)
        camera_binding.get_object_template().set_actor_label(camera_name)

        '''
        @TODO Je ne suis pas sûr que ce soit la meilleure méthode… 
        Depuis camera_binding si j'utilise add_spawnable_from_class() pour ajouter mon spawnable il est impossible de récupérer le camera component.
        Et donc impossible de cree ma track camera_component_binding via add_possessable().
        Du coup je crée une caméra temporaire me permettant de crée ma track camera_component_binding,
        Ensuite je supprime ma caméra temporaire et reparent la track sur le spawnable…
        '''
        temp_camera_actor = unreal.EditorLevelLibrary().spawn_actor_from_class(camera_target_class, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))



        temp_camera_binding = seq.add_possessable(temp_camera_actor)
        camera_component_binding = seq.add_possessable(temp_camera_actor.get_cine_camera_component())
        camera_component_binding.set_parent(camera_binding)
        temp_camera_binding.remove()
        temp_camera_actor.destroy_actor()

    else:
        # Create possessable camera
        camera_actor = unreal.EditorLevelLibrary().spawn_actor_from_class(camera_target_class, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        camera_actor.set_actor_label(camera_name)
        camera_binding = seq.add_possessable(camera_actor)
        camera_component_binding = seq.add_possessable(camera_actor.get_cine_camera_component())

    if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,26):
        camera_binding.set_display_name(camera_name)
    else:
        pass

    return camera_binding, camera_component_binding



def update_sequencer_camera_tracks(seq: unreal.LevelSequence, camera_binding: unreal.MovieSceneBindingProxy, camera_component_binding: unreal.MovieSceneBindingProxy, camera_tracks:  Dict[str, Any]):


    # Transform
    transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_end_frame_bounded(False)
    transform_section.set_start_frame_bounded(False)
    AddSequencerSectionTransformKeysByIniFile(transform_section, camera_tracks['ue_camera_transform'])

    # Focal Length
    TrackFocalLength = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    TrackFocalLength.set_property_name_and_path('Current Focal Length', 'CurrentFocalLength')
    sectionFocalLength = TrackFocalLength.add_section()
    sectionFocalLength.set_end_frame_bounded(False)
    sectionFocalLength.set_start_frame_bounded(False)
    AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, camera_tracks['camera_focal_length'])

    # Sensor Width
    TrackSensorWidth = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    TrackSensorWidth.set_property_name_and_path('Sensor Width (Filmback)', 'Filmback.SensorWidth')
    sectionSensorWidth = TrackSensorWidth.add_section()
    sectionSensorWidth.set_end_frame_bounded(False)
    sectionSensorWidth.set_start_frame_bounded(False)
    AddSequencerSectionFloatKeysByIniFile(sectionSensorWidth, camera_tracks['ue_camera_sensor_width'])

    # Sensor Height
    TrackSensorHeight = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    TrackSensorHeight.set_property_name_and_path('Sensor Height (Filmback)', 'Filmback.SensorHeight')
    sectionSensorHeight = TrackSensorHeight.add_section()
    sectionSensorHeight.set_end_frame_bounded(False)
    sectionSensorHeight.set_start_frame_bounded(False)
    AddSequencerSectionFloatKeysByIniFile(sectionSensorHeight, camera_tracks['ue_camera_sensor_height'])

    # Focus Distance
    TrackFocusDistance = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,24):
        TrackFocusDistance.set_property_name_and_path('Manual Focus Distance (Focus Settings)', 'FocusSettings.ManualFocusDistance')
    else:
        TrackFocusDistance.set_property_name_and_path('Current Focus Distance', 'ManualFocusDistance')
    sectionFocusDistance = TrackFocusDistance.add_section()
    sectionFocusDistance.set_end_frame_bounded(False)
    sectionFocusDistance.set_start_frame_bounded(False)
    AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, camera_tracks['camera_focus_distance'])

    # Current Aperture
    TracknAperture = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
    TracknAperture.set_property_name_and_path('Current Aperture', 'CurrentAperture')
    sectionAperture = TracknAperture.add_section()
    sectionAperture.set_end_frame_bounded(False)
    sectionAperture.set_start_frame_bounded(False)
    AddSequencerSectionFloatKeysByIniFile(sectionAperture, camera_tracks['camera_aperture'])

    if camera_tracks['camera_type'] == "ARCHVIS":
        # Camera Shift X/Y
        TrackArchVisShift = camera_component_binding.add_track(unreal.MovieSceneDoubleVectorTrack)
        TrackArchVisShift.set_property_name_and_path('Manual Correction (Shift)', 'ProjectionOffset')
        TrackArchVisShift.set_num_channels_used(2)
        SectionArchVisShift = TrackArchVisShift.add_section()
        SectionArchVisShift.set_end_frame_bounded(False)
        SectionArchVisShift.set_start_frame_bounded(False)
        AddSequencerSectionDoubleVectorKeysByIniFile(SectionArchVisShift, camera_tracks['archvis_camera_shift'])

        # Disable auto correct perspective
        TrackArchVisCorrectPersp = camera_component_binding.add_track(unreal.MovieSceneBoolTrack)
        TrackArchVisCorrectPersp.set_property_name_and_path('Correct Perspective (Auto)', 'bCorrectPerspective')
        SectionArchVisCorrectPersp = TrackArchVisCorrectPersp.add_section()
        start_frame = unreal.FrameNumber(int(camera_tracks['frame_start']))
        get_section_all_channel(SectionArchVisCorrectPersp)[0].add_key(start_frame, False)

                

    # Spawned
    tracksSpawned = camera_binding.find_tracks_by_exact_type(unreal.MovieSceneSpawnTrack)
    if len(tracksSpawned) > 0:
        sectionSpawned = tracksSpawned[0].get_sections()[0]
        AddSequencerSectionBoolKeysByIniFile(sectionSpawned, camera_tracks['camera_spawned'])

    # @TODO Need found a way to set this values...
    #camera_component.set_editor_property('aspect_ratio', camera_tracks['desired_screen_ratio'])
    #camera_component.lens_settings.set_editor_property('min_f_stop', camera_tracks['ue_lens_minfstop'])
    #camera_component.lens_settings.set_editor_property('max_f_stop', camera_tracks['ue_lens_maxfstop'])
