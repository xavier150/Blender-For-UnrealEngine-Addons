import bpy

from . import bfu_camera_data
from .. import languages
from .. import bfu_write_utils

def WriteOneFrameCameraAnimationTracks(obj, target_frame=None, pre_bake_camera: bfu_camera_data.BFU_CameraTracks = None):
    return WriteCameraAnimationTracks(obj, target_frame, target_frame+1, pre_bake_camera)

def WriteCameraAnimationTracks(obj, target_frame_start=None, target_frame_end=None, pre_bake_camera: bfu_camera_data.BFU_CameraTracks = None):
    # Write as data camera animation tracks

    scene = bpy.context.scene
    if target_frame_start is None:
        target_frame_start = scene.frame_start
    if target_frame_end is None:
        target_frame_end = scene.frame_end+1


    scene = bpy.context.scene
    data = {}
    data['comment'] = {
        '1/3': languages.ti('write_text_additional_track_start'),
        '2/3': languages.ti('write_text_additional_track_camera'),
        '3/3': languages.ti('write_text_additional_track_end'),
    }

    bfu_write_utils.add_generated_json_meta_data(data)

    data["resolution_x"] = scene.render.resolution_x
    data["resolution_y"] = scene.render.resolution_y
    data["desired_screen_ratio"] = scene.render.resolution_x / scene.render.resolution_y
    data["frame_start"] = target_frame_start
    data["frame_end"] = target_frame_end

    # Frames is old, need to update and remove.
    data['Frames'] = []
    data['Frames'].append({
        'frame_start': target_frame_start,
        'frame_end': target_frame_end,
    })

 
    if pre_bake_camera:
        camera_tracks = pre_bake_camera
    else:
        multi_camera_tracks = bfu_camera_data.BFU_MultiCameraTracks()
        multi_camera_tracks.add_camera_to_evaluate(obj)
        multi_camera_tracks.set_start_end_frames(target_frame_start, target_frame_end)
        multi_camera_tracks.evaluate_all_cameras(True)
        camera_tracks = multi_camera_tracks.get_evaluate_camera_data(obj)

    data['Camera transform'] = camera_tracks.transform_track
    print(data['Camera transform'])
    data["Camera NearClippingPlane"] = camera_tracks.near_clipping_plane
    data["Camera FarClippingPlane"] = camera_tracks.far_clipping_plane
    data["Camera FieldOfView"] = camera_tracks.fov
    data["Camera FocalAngle"] = camera_tracks.angle
    data['Camera FocalLength'] = camera_tracks.lens
    data['Camera SensorWidth'] = camera_tracks.sensor_width
    data['Camera SensorHeight'] = camera_tracks.sensor_height
    data['Camera FocusDistance'] = camera_tracks.focus_distance
    data['Camera Aperture'] = camera_tracks.aperture_fstop
    data['Camera Spawned'] = camera_tracks.hide_viewport

    return data

