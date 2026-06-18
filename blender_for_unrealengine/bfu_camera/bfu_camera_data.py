# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import math
import mathutils
from typing import Dict, Any, List, Tuple, TYPE_CHECKING
from . import bfu_camera_unreal_utils
from . import bfu_camera_utils
from .. import bpl
from .. import bbpl
from .. import bfu_utils
from .. import bfu_addon_prefs


def set_current_frame(new_frame: int) -> None:
    scene = bpy.context.scene
    if scene is None:
        return
    scene.frame_set(new_frame)


def getCameraFocusDistance(Camera: bpy.types.Object, Target: bpy.types.Object) -> float:
    global_loc_obj1 = Camera.matrix_world.translation
    global_loc_obj2 = Target.matrix_world.translation
    diff = global_loc_obj2 - global_loc_obj1
    return diff.length

def getAllCamDistKeys(Camera: bpy.types.Object, Target: bpy.types.Object, frame_start: int, frame_end: int) -> List[Tuple[int, float]]:
    scene = bpy.context.scene
    if scene is None:
        return []
    saveFrame = scene.frame_current  # Save current frame
    keys: List[Tuple[int, float]] = []
    for frame in range(frame_start, frame_end):
        set_current_frame(frame)
        v = getCameraFocusDistance(Camera, Target)
        keys.append((frame, v))
    set_current_frame(saveFrame)  # Resets previous start frame
    return keys

def getAllKeysByMatrix(obj: bpy.types.Object, frame_start: int, frame_end: int) -> List[Tuple[int, Any]]:
    scene = bpy.context.scene
    if scene is None:
        return []

    saveFrame = scene.frame_current  # Save current frame
    keys: List[Tuple[int, Any]] = []
    for frame in range(frame_start, frame_end):
        set_current_frame(frame)
        v = obj.matrix_world*1
        keys.append((frame, v))
    set_current_frame(saveFrame)  # Resets previous start frame
    return keys

class BFU_CameraTracks():

    def __init__(self, camera: bpy.types.Object):
        # Context stats
        scene = bpy.context.scene
        if scene is None:
            return
        if not isinstance(camera.data, bpy.types.Camera):
            print("Error: The provided object is not a camera.")
            return

        render = scene.render
        if render:
            self.resolution_x: int = render.resolution_x
            self.resolution_y: int = render.resolution_y
            self.pixel_aspect_x: float = render.pixel_aspect_x
            self.pixel_aspect_y: float = render.pixel_aspect_y
        else:
            # Use default values if render is not available
            self.resolution_x = 1920
            self.resolution_y = 1080
            self.pixel_aspect_x = 1.0
            self.pixel_aspect_y = 1.0

        self.camera_name: str = camera.name
        self.camera_type: str = camera.bfu_desired_camera_type  # type: ignore
        self.projection_mode: str = camera.data.type
        self.ortho_scale: float = camera.data.ortho_scale

        self.ue_projection_mode: str = bfu_camera_unreal_utils.get_camera_unreal_projection(camera)
        self.ue_camera_actor: str = bfu_camera_unreal_utils.get_camera_unreal_actor(camera)

        # Blender Camera Data
        self.transform_track: Dict[int, Any] = {}
        self.near_clipping_plane: Dict[int, Any] = {}
        self.far_clipping_plane: Dict[int, Any] = {}
        self.field_of_view: Dict[int, Any] = {}
        self.angle: Dict[int, Any] = {}
        self.lens: Dict[int, Any] = {}
        self.sensor_width: Dict[int, Any] = {}
        self.sensor_height: Dict[int, Any] = {}
        self.projection_shift: Dict[int, Any] = {}
        self.focus_distance: Dict[int, Any] = {}
        self.aperture_fstop: Dict[int, Any] = {}
        self.hide_viewport: Dict[int, Any] = {}

        # Formated data for Unreal Engine
        self.ue_transform_track: Dict[int, Any] = {}
        self.ue_sensor_horizontal_offset: Dict[int, Any] = {}
        self.ue_sensor_vertical_offset: Dict[int, Any] = {}
        self.ue_sensor_width: Dict[int, Any] = {}
        self.ue_sensor_height: Dict[int, Any] = {}
        self.ue_lens_min_fstop: float = 1.2  # Default value in Unreal Engine
        self.ue_lens_max_fstop: float = 22.0  # Default value in Unreal Engine

        # Formated data for ArchVis Tools in Unreal Engine
        self.arch_projection_shift: Dict[int, Any] = {}


    def get_animated_values_as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        # Static data
        data["camera_name"] = self.camera_name
        data["camera_type"] = self.camera_type
        data["camera_actor"] = self.ue_camera_actor
        data["resolution"] = {"x": self.resolution_x, "y": self.resolution_y}
        data["desired_screen_ratio"] = self.resolution_x / self.resolution_y
        data["projection_mode"] = self.projection_mode
        data["ue_projection_mode"] = self.ue_projection_mode
        data["ortho_scale"] = self.ortho_scale
        data['ue_lens_minfstop'] = self.ue_lens_min_fstop
        data['ue_lens_maxfstop'] = self.ue_lens_max_fstop

        # Animated Tracks
        data['camera_transform'] = self.transform_track
        data['ue_camera_transform'] = self.ue_transform_track
        data["camera_near_clipping_plane"] = self.near_clipping_plane
        data["camera_far_clipping_plane"] = self.far_clipping_plane
        data["camera_field_of_view"] = self.field_of_view
        data["camera_focal_angle"] = self.angle
        data['camera_focal_length'] = self.lens
        data['camera_sensor_width'] = self.sensor_width
        data['camera_sensor_height'] = self.sensor_height
        data['camera_shift'] = self.projection_shift
        data['ue_sensor_horizontal_offset'] = self.ue_sensor_horizontal_offset
        data['ue_sensor_vertical_offset'] = self.ue_sensor_vertical_offset
        data['archvis_camera_shift'] = self.arch_projection_shift
        data['ue_camera_sensor_width'] = self.ue_sensor_width
        data['ue_camera_sensor_height'] = self.ue_sensor_height
        data['camera_focus_distance'] = self.focus_distance
        data['camera_aperture'] = self.aperture_fstop
        data['camera_spawned'] = self.hide_viewport
        return data
    


    def fix_transform_axis_flippings(self, camera: bpy.types.Object, array_rotation: List[float], frame: int, target_use: str):

        # Define constants for target use
        TRANSFORM_TRACKS = {
            "Blender": self.transform_track,
            "UnrealEngine": self.ue_transform_track,
        }

        # Get the correct transform track
        transform_track = TRANSFORM_TRACKS.get(target_use)
        if transform_track is None:
            raise ValueError(f"Invalid target_use: {target_use}. Must be 'Blender' or 'UnrealEngine'.")
           
        # convert warp_target to degrees        
        if TYPE_CHECKING:
            fix_axis_flippings_warp_target: mathutils.Vector = mathutils.Vector((0.0, 0.0, 0.0))
        else:
            fix_axis_flippings_warp_target = camera.bfu_fix_axis_flippings_warp_target
        warp_target_degrees = [round(math.degrees(v), 1) for v in fix_axis_flippings_warp_target]

        # Create a copy of the current rotation array
        new_array_rotation = array_rotation.copy()

        # Check if a previous frame exists in the transform track
        if frame - 1 in transform_track:
            previous_rotation = transform_track[frame - 1]
            
            # Calculate new rotations for each axis (X, Y, Z)
            for i, axis in enumerate(["rotation_x", "rotation_y", "rotation_z"]):
                previous_value = previous_rotation[axis]
                # Compute the difference based on the warp target
                diff = round((array_rotation[i] - previous_value) / warp_target_degrees[i]) * warp_target_degrees[i]
                # Adjust the current rotation to eliminate flipping
                new_array_rotation[i] = array_rotation[i] - diff
        return new_array_rotation

    def evaluate_camera_transform(self, camera: bpy.types.Object, frame: int, target_use: str):
        transform: Dict[str, float] = {}


        if target_use == "UnrealEngine":
            camera_transform: Tuple[mathutils.Vector, List[float], mathutils.Vector]
            camera_transform = bfu_utils.evaluate_camera_position_for_unreal(camera)
            array_location: mathutils.Vector = camera_transform[0]
            array_rotation: List[float] = camera_transform[1]
            array_scale: mathutils.Vector = camera_transform[2]

            # Fix axis flippings
            if TYPE_CHECKING:
                fix_axis_flippings: bool = True
            else:
                fix_axis_flippings = camera.bfu_fix_axis_flippings
            if fix_axis_flippings:
                array_rotation = self.fix_transform_axis_flippings(camera, array_rotation, frame, target_use)

            transform: Dict[str, float] = {}
            transform["location_x"] = round(array_location.x, 8)
            transform["location_y"] = round(array_location.y, 8)
            transform["location_z"] = round(array_location.z, 8)
            transform["rotation_x"] = round(array_rotation[0], 8)
            transform["rotation_y"] = round(array_rotation[1], 8)
            transform["rotation_z"] = round(array_rotation[2], 8)
            transform["scale_x"] = round(array_scale.x, 4)
            transform["scale_y"] = round(array_scale.y, 4)
            transform["scale_z"] = round(array_scale.z, 4)
            return transform

        else:
            camera_transform = bfu_utils.evaluate_camera_position(camera)
            transform: Dict[str, float] = {}
            transform["location_x"] = round(camera.location.x, 8)
            transform["location_y"] = round(camera.location.y, 8)
            transform["location_z"] = round(camera.location.z, 8)
            transform["rotation_x"] = round(camera.rotation_euler.x, 8)
            transform["rotation_y"] = round(camera.rotation_euler.y, 8)
            transform["rotation_z"] = round(camera.rotation_euler.z, 8)
            transform["scale_x"] = round(camera.scale.x, 4)
            transform["scale_y"] = round(camera.scale.y, 4)
            transform["scale_z"] = round(camera.scale.z, 4)
            return transform
        

    def get_ue_crop_sensor_height(self, sensor_width: float, sensor_height: float):
        res_ratio = self.resolution_x / self.resolution_y
        pixel_ratio = self.pixel_aspect_x / self.pixel_aspect_y
        crop_sensor_height = (sensor_width / (res_ratio * pixel_ratio))
        return crop_sensor_height

    def evaluate_track_at_frame(self, camera: bpy.types.Object, frame: int):
        scene = bpy.context.scene
        if scene is None:
            return
        if not isinstance(camera.data, bpy.types.Camera):
            print("Error: The provided object is not a camera.")
            return

        addon_prefs = bfu_addon_prefs.get_addon_preferences()
        unit_scale = bfu_utils.get_scene_unit_scale()
        set_current_frame(frame)

        self.transform_track[frame] = self.evaluate_camera_transform(camera, frame, "Blender")
        self.ue_transform_track[frame] = self.evaluate_camera_transform(camera, frame, "UnrealEngine")

        # Get FOV FocalLength SensorWidth SensorHeight
        self.angle[frame] = bfu_camera_utils.get_one_keys_by_fcurves(camera, "angle", camera.data.angle, frame)
        self.lens[frame] = bfu_camera_utils.get_one_keys_by_fcurves(camera, "lens", camera.data.lens, frame)

        sensor_width = bfu_camera_utils.get_one_keys_by_fcurves(camera, "sensor_width", camera.data.sensor_width, frame)
        sensor_height = bfu_camera_utils.get_one_keys_by_fcurves(camera, "sensor_height", camera.data.sensor_height, frame)

        self.sensor_width[frame] = sensor_width 
        self.sensor_height[frame] = sensor_height
        self.ue_sensor_width[frame] = sensor_width 
        self.ue_sensor_height[frame] = self.get_ue_crop_sensor_height(sensor_width, sensor_height)

        # Camera shift
        shift_x = bfu_camera_utils.get_one_keys_by_fcurves(camera, "shift_x", camera.data.shift_x, frame)
        shift_y = bfu_camera_utils.get_one_keys_by_fcurves(camera, "shift_y", camera.data.shift_y, frame)
        self.projection_shift[frame] = {"x": shift_x, "y": shift_y}

        # Unreal shift with Arch Camera plugin
        arch_shift_x = shift_x * 2 # x2
        arch_shift_y = shift_y * 2 * (self.resolution_x / self.resolution_y) # Use screen ratio.
        self.arch_projection_shift[frame] = {"x": arch_shift_x, "y": arch_shift_y}

        # Unreal shift native Unreal Engine 5.5 cameras sensor offset
        self.ue_sensor_horizontal_offset[frame] = shift_x * self.ue_sensor_width[frame]
        self.ue_sensor_vertical_offset[frame] = shift_y * self.ue_sensor_height[frame] * (self.resolution_x / self.resolution_y)

        #FOV
        self.field_of_view[frame] = round(math.degrees(self.angle[frame]), 8)

        # Get Clip
        self.near_clipping_plane[frame] = bfu_camera_utils.get_one_keys_by_fcurves(camera, "clip_start", camera.data.clip_start, frame) * 100 * unit_scale
        self.far_clipping_plane[frame] = bfu_camera_utils.get_one_keys_by_fcurves(camera, "clip_end", camera.data.clip_end, frame) * 100 * unit_scale

        # Get FocusDistance
        if camera.data.dof and camera.data.dof.use_dof:
            if camera.data.dof.focus_object is not None:
                key = getCameraFocusDistance(camera, camera.data.dof.focus_object)

            else:
                key = bfu_camera_utils.get_one_keys_by_fcurves(camera, "dof.focus_distance", camera.data.dof.focus_distance, frame)

            if addon_prefs.scale_camera_focus_distance_with_unit_scale:
                self.focus_distance[frame] = key * 100 * unit_scale
            else:
                self.focus_distance[frame] = key * 100

        else:
            self.focus_distance[frame] = 100000  # 100000 is default value in Unreal Engine

        def get_aperture_fstop(in_camera: bpy.types.Object) -> float:
            if not isinstance(in_camera.data, bpy.types.Camera):
                return 2.8

            # Write Aperture (Depth of Field) keys
            render = scene.render
            if render:
                dof = in_camera.data.dof
                if dof and render.engine in ["BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"]:
                    key = bfu_camera_utils.get_one_keys_by_fcurves(in_camera, "dof.aperture_fstop", dof.aperture_fstop, frame)
                    key = round(key, 8) # Avoid microscopic offsets.
                    if addon_prefs.scale_camera_fstop_with_unit_scale:
                        return key / unit_scale
                    else:
                        return key
            return 2.8  # 2.8 is default value in Unreal Engine

        self.aperture_fstop[frame] = get_aperture_fstop(camera)

        #Update min and max lens FStop
        self.ue_lens_min_fstop = min(self.ue_lens_min_fstop, self.aperture_fstop[frame])
        self.ue_lens_max_fstop = max(self.ue_lens_max_fstop, self.aperture_fstop[frame])

        boolKey = bfu_camera_utils.get_one_keys_by_fcurves(camera, "hide_viewport", camera.hide_viewport, frame, False)
        self.hide_viewport[frame] = (boolKey < 1)  # Inversed for convert hide to spawn

    def evaluate_all_tracks(self, camera: bpy.types.Object, start_frame: float, end_frame: float):

        scene = bpy.context.scene
        if scene is None:
            return

        addon_prefs = bfu_addon_prefs.get_addon_preferences()

        #print(f"Start evaluate camera {camera.name} Frames:({str(frame_start)}-{str(frame_end)})")
        counter = bpl.utils.CounterTimer()
        
        slms = bfu_utils.TimelineMarkerSequence()
        
        # Save scene data
        save_current_frame = scene.frame_current

        int_frame_start: int = min(int(start_frame) - 1, 0) # -1 for secure range
        int_frame_end: int = int(end_frame) + 1 # +1 for secure range

        for frame in range(int_frame_start, int_frame_end):
            if len(slms.marker_sequences) > 0 and addon_prefs.bake_only_key_visible_in_cut:
                # Bake only frames visible in cut
                marker_sequence = slms.get_marker_sequence_at_frame(frame)
                if marker_sequence and marker_sequence.marker:
                    if marker_sequence.marker.camera == camera:
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
        self.cameras_to_evaluate: List[bpy.types.Object] = []
        self.frame_start: int = 0
        self.frame_end: int = 1
        self.evaluate_cameras: Dict[str, BFU_CameraTracks] = {}

    def add_camera_to_evaluate(self, obj: bpy.types.Object):
        self.cameras_to_evaluate.append(obj)

    def set_start_end_frames(self, frame_start: int, frame_end: int):
        self.frame_start = frame_start
        self.frame_end = frame_end

    def evaluate_all_cameras(self, ignore_marker_sequences: bool = False, preview: bool = False, print_counter: bool = False):
        # Evalutate all cameras at same time will avoid frames switch

        scene = bpy.context.scene
        if scene is None:
            return

        def optimizated_evaluate_track_at_frame(evaluate: BFU_CameraTracks):
            marker_sequence = slms.get_marker_sequence_at_frame(frame)
            if marker_sequence:
                marker = marker_sequence.marker
                if marker and marker.camera == camera:
                    evaluate.evaluate_track_at_frame(camera, frame)



        frame_start = self.frame_start
        frame_end = self.frame_end
        addon_prefs = bfu_addon_prefs.get_addon_preferences()

        counter = bpl.utils.CounterTimer()
        slms = bfu_utils.TimelineMarkerSequence()
        save_simplfy = bbpl.utils.SaveUserRenderSimplify()

        # Save scene data
        save_current_frame = scene.frame_current
        if not preview:
            save_simplfy.save_scene()
            save_simplfy.simplify_scene()

        for camera in self.cameras_to_evaluate:
            self.evaluate_cameras[camera.name] = BFU_CameraTracks(camera)

        #print(f"Start evaluate {str(len(self.cameras_to_evaluate))} camera(s). Frames:({str(frame_start)}-{str(frame_end)})")
        for frame in range(frame_start, frame_end):
            for camera in self.cameras_to_evaluate:
                evaluate = self.evaluate_cameras[camera.name]
                
                if len(slms.marker_sequences) > 0 and addon_prefs.bake_only_key_visible_in_cut and ignore_marker_sequences is False:
                    # Bake only frames visible in cuts
                    optimizated_evaluate_track_at_frame(evaluate)

                else:
                    # Bake all frames
                    evaluate.evaluate_track_at_frame(camera, frame)

        if not preview:
            save_simplfy.reset_scene()
        scene.frame_current = save_current_frame

        if print_counter:
            print("Evaluate all cameras finished in " + counter.get_str_time())
            print("-----")

    def get_evaluate_camera_data(self, obj: bpy.types.Object):
        return self.evaluate_cameras[obj.name]
    
    def get_evaluate_camera_data_as_dict(self, obj: bpy.types.Object) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        data.update(self.evaluate_cameras[obj.name].get_animated_values_as_dict())
        data.update(self.evaluate_cameras[obj.name].get_animated_values_as_dict())
        return data