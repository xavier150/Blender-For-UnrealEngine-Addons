import bpy
import math
from typing import Dict
from .. import bps
from .. import bbpl
from .. import languages
from .. import bfu_basics
from .. import bfu_utils

def set_current_frame(new_frame):
    scene = bpy.context.scene
    scene.frame_set(new_frame)


def getCameraFocusDistance(Camera, Target):
    transA = Camera.matrix_world.copy()
    transB = Target.matrix_world.copy()
    transA.invert()
    distance = (transA @ transB).translation.z  # Z is the Fosrward
    if distance < 0:
        distance *= -1
    return distance

def getAllCamDistKeys(Camera, Target, frame_start, frame_end):
    scene = bpy.context.scene
    saveFrame = scene.frame_current  # Save current frame
    keys = []
    for frame in range(frame_start, frame_end):
        set_current_frame(frame)
        v = getCameraFocusDistance(Camera, Target)
        keys.append((frame, v))
    set_current_frame(saveFrame)  # Resets previous start frame
    return keys

def getAllKeysByMatrix(obj, frame_start, frame_end):
    scene = bpy.context.scene
    saveFrame = scene.frame_current  # Save current frame
    keys = []
    for frame in range(frame_start, frame_end):
        set_current_frame(frame)
        v = obj.matrix_world*1
        keys.append((frame, v))
    set_current_frame(saveFrame)  # Resets previous start frame
    return keys

def getOneKeysByFcurves(obj, DataPath, DataValue, Frame, IsData=True):
    scene = bpy.context.scene
    if IsData:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                f = obj.data.animation_data.action.fcurves.find(DataPath)
                if f is not None:
                    return f.evaluate(Frame)
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                f = obj.animation_data.action.fcurves.find(DataPath)
                if f is not None:
                    return f.evaluate(Frame)
    return DataValue

def getAllKeysByFcurves(obj, DataPath, DataValue, frame_start, frame_end, IsData=True):
    scene = bpy.context.scene
    keys = []
    f = None
    if IsData:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                f = obj.data.animation_data.action.fcurves.find(DataPath)
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                f = obj.animation_data.action.fcurves.find(DataPath)

    if f is not None:
        for frame in range(frame_start, frame_end):
            v = f.evaluate(frame)
            keys.append((frame, v))
        return keys
    return[(frame_start, DataValue)]

class BFU_CameraTracks():

    def __init__(self):
        self.transform_track = {}
        self.near_clipping_plane = {}
        self.far_clipping_plane = {}
        self.fov = {}
        self.angle = {}
        self.lens = {}
        self.sensor_width = {}
        self.sensor_height = {}
        self.focus_distance = {}
        self.aperture_fstop = {}
        self.hide_viewport = {}

    def evaluate_track_at_frame(self, camera, frame):
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()
        unit_scale = bfu_utils.get_scene_unit_scale()
        set_current_frame(frame)

        array_transform = bfu_utils.EvaluateCameraPositionForUnreal(camera)
        array_location = array_transform[0]
        array_rotation = array_transform[1]
        array_scale = array_transform[2]

        # Fix axis flippings
        if camera.bfu_fix_axis_flippings:
            if frame-1 in self.transform_track:  # Previous frame
                previous_rotation_x = self.transform_track[frame-1]["rotation_x"]
                previous_rotation_y = self.transform_track[frame-1]["rotation_y"]
                previous_rotation_z = self.transform_track[frame-1]["rotation_z"]
                diff = round((array_rotation[0] - previous_rotation_x) / 180.0) * 180.0
                array_rotation[0] = array_rotation[0] - diff
                diff = round((array_rotation[1] - previous_rotation_y) / 180.0) * 180.0
                array_rotation[1] = array_rotation[1] - diff
                diff = round((array_rotation[2] - previous_rotation_z) / 180.0) * 180.0
                array_rotation[2] = array_rotation[2] - diff

        transform = {}
        transform["location_x"] = array_location.x
        transform["location_y"] = array_location.y
        transform["location_z"] = array_location.z
        transform["rotation_x"] = array_rotation[0]
        transform["rotation_y"] = array_rotation[1]
        transform["rotation_z"] = array_rotation[2]
        transform["scale_x"] = array_scale.x
        transform["scale_y"] = array_scale.y
        transform["scale_z"] = array_scale.z
        self.transform_track[frame] = transform

        # Get FOV FocalLength SensorWidth SensorHeight
        self.angle[frame] = getOneKeysByFcurves(camera, "angle", camera.data.angle, frame)
        self.lens[frame] = getOneKeysByFcurves(camera, "lens", camera.data.lens, frame)
        self.sensor_width[frame] = getOneKeysByFcurves(camera, "sensor_width", camera.data.sensor_width, frame)
        self.sensor_height[frame] = getOneKeysByFcurves(camera, "sensor_height", camera.data.sensor_height, frame)
        self.fov[frame] = math.degrees(self.angle[frame])

        # Get Clip
        self.near_clipping_plane[frame] = getOneKeysByFcurves(camera, "clip_start", camera.data.clip_start, frame) * 100 * unit_scale
        self.far_clipping_plane[frame] = getOneKeysByFcurves(camera, "clip_end", camera.data.clip_end, frame) * 100 * unit_scale

        # Get FocusDistance
        if camera.data.dof.focus_object is not None:
            key = getCameraFocusDistance(camera, camera.data.dof.focus_object)
            key = key * 100 * unit_scale

        else:
            key = getOneKeysByFcurves(camera, "dof.focus_distance", camera.data.dof.focus_distance, frame)
            key = key * 100 * unit_scale

        if key > 0:
            if addon_prefs.scale_camera_focus_distance_with_unit_scale:
                self.focus_distance[frame] = key / unit_scale
            else:
                self.aperture_fstop[frame] = key
        else:
            self.focus_distance[frame] = 100000  # 100000 is default value in Unreal Engine

        # Write Aperture (Depth of Field) keys
        render_engine = scene.render.engine
        if render_engine == "BLENDER_EEVEE" or render_engine == "CYCLES" or render_engine == "BLENDER_WORKBENCH":
            key = getOneKeysByFcurves(camera, "dof.aperture_fstop", camera.data.dof.aperture_fstop, frame)
            if addon_prefs.scale_camera_fstop_with_unit_scale:
                self.aperture_fstop[frame] = key / unit_scale
            else:
                self.aperture_fstop[frame] = key
        else:
            self.aperture_fstop[frame] = 2.8  # 2.8 is default value in Unreal Engine

        boolKey = getOneKeysByFcurves(camera, "hide_viewport", camera.hide_viewport, frame, False)
        self.hide_viewport[frame] = (boolKey < 1)  # Inversed for convert hide to spawn

    def evaluate_all_tracks(self, camera, frame_start, frame_end):
        
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        print("Start evaluate camera " + camera.name + "From " + str(frame_start) + " to " + str(frame_end))
        counter = bps.utils.CounterTimer()
        
        slms = bfu_utils.TimelineMarkerSequence()
        
        # Save scene data
        save_current_frame = scene.frame_current
        save_use_simplify = bpy.context.scene.render.use_simplify


        for frame in range(frame_start, frame_end+1):
            if len(slms.marker_sequences) > 0 and addon_prefs.bake_only_key_visible_in_cut:
                # Bake only frames visible in cut
                marker_sequence = slms.GetMarkerSequenceAtFrame(frame)
                if marker_sequence:
                    marker = marker_sequence.marker
                    if marker.camera == camera:
                        self.evaluate_track_at_frame(camera, frame)
            else:
                # Bake all frames
                self.evaluate_track_at_frame(camera, frame)

        set_current_frame(save_current_frame)

        print("Evaluate " + camera.name + " finished in " + counter.get_str_time())
        print("-----")
        return

 
class BFU_MultiCameraTracks():

    def __init__(self):
        self.cameras_to_evaluate = []
        self.frame_start = 0
        self.frame_end = 1
        self.evaluate_cameras: Dict[str, BFU_CameraTracks] = {}

    def add_camera_to_evaluate(self, obj: bpy.types.Object):
        self.cameras_to_evaluate.append(obj)

    def set_start_end_frames(self, frame_start: int, frame_end: int):
        self.frame_start = frame_start
        self.frame_end = frame_end

    def evaluate_all_cameras(self, ignore_marker_sequences = False):
        # Evalutate all cameras at same time will avoid frames switch

        def optimizated_evaluate_track_at_frame(evaluate: BFU_CameraTracks):
            marker_sequence = slms.GetMarkerSequenceAtFrame(frame)
            if marker_sequence:
                marker = marker_sequence.marker
                if marker.camera == camera:
                    evaluate.evaluate_track_at_frame(camera, frame)



        frame_start = self.frame_start
        frame_end = self.frame_end
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        counter = bps.utils.CounterTimer()

        slms = bfu_utils.TimelineMarkerSequence()

        # Save scene data
        save_current_frame = scene.frame_current
        save_use_simplify = bpy.context.scene.render.use_simplify
        bpy.context.scene.render.use_simplify = True

        for camera in self.cameras_to_evaluate:
            camera_tracks = BFU_CameraTracks()
            self.evaluate_cameras[camera.name] = camera_tracks

        print("Start evaluate " + str(len(self.cameras_to_evaluate)) + " camera(s) " + str(frame_start) + " to " + str(frame_end))
        for frame in range(frame_start, frame_end):
            for camera in self.cameras_to_evaluate:
                evaluate = self.evaluate_cameras[camera.name]
                
                if len(slms.marker_sequences) > 0 and addon_prefs.bake_only_key_visible_in_cut and ignore_marker_sequences is False:
                    # Bake only frames visible in cuts
                    optimizated_evaluate_track_at_frame(evaluate)

                else:
                    # Bake all frames
                    evaluate.evaluate_track_at_frame(camera, frame)

        scene.frame_current = save_current_frame
        bpy.context.scene.render.use_simplify = save_use_simplify

    def get_evaluate_camera_data(self, obj: bpy.types.Object):
        return self.evaluate_cameras[obj.name]