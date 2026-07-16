# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------



import string
import fnmatch
import math
import os
from typing import List, Tuple, Optional, TYPE_CHECKING, Any
from pathlib import Path
import bpy
import bmesh
import mathutils
from . import bbpl
from . import bfu_basics
from . import bfu_export_control
from . import bfu_addon_prefs
from . import bpl


class SavedBones():

    def __init__(self, bone):
        if bone:
            self.name = bone.name
            self.select = bone.select
            self.hide = bone.hide


class SavedViewLayerChildren():

    def __init__(self, vlayer, childCol):
        if childCol:
            self.vlayer_name = vlayer.name
            self.name = childCol.name
            self.exclude = childCol.exclude
            self.hide_viewport = childCol.hide_viewport
            self.children = []

            for children in childCol.children:
                SavedViewLayerChildren(vlayer, children)


class MarkerSequence():
    def __init__(self, marker: Optional[bpy.types.TimelineMarker] = None):
        scene = bpy.context.scene
        if scene is None:
            return

        self.marker: Optional[bpy.types.TimelineMarker] = marker
        self.start: int = 0
        self.end: int = scene.frame_end

        if marker is not None:
            self.start = marker.frame


class TimelineMarkerSequence():

    def __init__(self):
        scene = bpy.context.scene
        if scene is None:
            return
        
        timeline: bpy.types.TimelineMarkers = scene.timeline_markers
        self.marker_sequences: List[MarkerSequence] = self.get_marker_sequences(timeline)

    def get_marker_sequences(self, timeline_markers: bpy.types.TimelineMarkers) -> List[MarkerSequence]:
        if len(timeline_markers) == 0:
            print("Scene has no timeline_markers.")
            return []

        def get_first_marker(marker_list: List[bpy.types.TimelineMarker]) -> bpy.types.TimelineMarker:
            best_marker: bpy.types.TimelineMarker
            best_marker_frame = 0
            init = False

            for marker in marker_list:

                if init:
                    if marker.frame < best_marker_frame:
                        best_marker = marker
                        best_marker_frame = marker.frame
                else:
                    best_marker = marker
                    best_marker_frame = marker.frame
                    init = True

            return best_marker

        marker_list: List[bpy.types.TimelineMarker] = []
        for marker in timeline_markers:
            marker_list.append(marker)

        order_marker_list: List[bpy.types.TimelineMarker] = []
        while len(marker_list) != 0:
            first_marker = get_first_marker(marker_list)
            order_marker_list.append(first_marker)
            marker_list.remove(first_marker)

        marker_sequences: List[MarkerSequence] = []

        for marker in order_marker_list:
            marker_sequence = MarkerSequence(marker)

            if len(marker_sequences) > 0:
                previous_marker_sequence = marker_sequences[-1]
                previous_marker_sequence.end = marker.frame - 1

            marker_sequences.append(marker_sequence)

        return marker_sequences

    def get_marker_sequence_at_frame(self, frame: int) -> Optional[MarkerSequence]:
        if self.marker_sequences:
            for marker_sequence in self.marker_sequences:
                # print(marker_sequence.start, marker_sequence.end, frame)
                if frame >= marker_sequence.start and frame <= marker_sequence.end:
                    return marker_sequence
        return None

def update_progress(job_title: str, progress: float, time: Optional[float] = None):

    length = 20  # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(
        job_title,
        "#"*block + "-"*(length-block),
        round(progress*100, 2))

    if progress >= 1:
        if time is not None:
            msg += " DONE IN " + str(round(time, 2)) + "s\r\n"
        else:
            msg += " DONE\r\n"


def remove_useless_specific_data(name: str, data_type: str):
    if data_type == "MESH":
        if name in bpy.data.meshes:
            oldData = bpy.data.meshes[name]
            if oldData.users == 0:
                bpy.data.meshes.remove(oldData)  # type: ignore

    if data_type == "ARMATURE":
        if name in bpy.data.armatures:
            oldData = bpy.data.armatures[name]
            if oldData.users == 0:
                bpy.data.armatures.remove(oldData)  # type: ignore


def CleanJoinSelect():
    view_layer = bpy.context.view_layer
    if len(bpy.context.selected_objects) > 1:
        if view_layer.objects.active is None:
            view_layer.objects.active = bpy.context.selected_objects[0]

        if bpy.ops.object.convert.poll():
            bpy.ops.object.join()


def CleanDeleteSelect():

    removed_objects = []
    oldDataToRemove = []
    for obj in bpy.context.selected_objects:
        removed_objects.append(obj.name)
        if obj.data is not None:
            oldDataToRemove.append([obj.data.name, obj.type])

    bpy.ops.object.delete()

    for data in oldDataToRemove:
        remove_useless_specific_data(data[0], data[1])

    return removed_objects


def clean_delete_objects(objs: List[bpy.types.Object]) -> List[str]:

    objs = list(dict.fromkeys(objs))

    removed_objects = []
    for obj in objs:

        souldRemoveData = False
        if obj.data is not None:
            oldDataToRemove = obj.data.name
            oldDataTypeToRemove = obj.type
            souldRemoveData = True

        removed_objects.append(obj.name)
        bpy.data.objects.remove(obj)

        if souldRemoveData:
            remove_useless_specific_data(oldDataToRemove, oldDataTypeToRemove)

    return removed_objects


def get_all_collision_and_sockets_obj(objs_list=None):
    # Get any object that can be understood
    # as a collision or a socket by unreal

    if objs_list is not None:
        objs = objs_list
    else:
        objs = bpy.context.scene.objects

    colObjs = [obj for obj in objs if (
        fnmatch.fnmatchcase(obj.name, "UBX*") or
        fnmatch.fnmatchcase(obj.name, "UCP*") or
        fnmatch.fnmatchcase(obj.name, "USP*") or
        fnmatch.fnmatchcase(obj.name, "UCX*") or
        fnmatch.fnmatchcase(obj.name, "SOCKET*")
        )]
    return colObjs


def get_export_desired_childs(obj: bpy.types.Object) -> List[bpy.types.Object]:
    # Get only all child objects that must be exported with parent object

    w = bpy.context.window
    if not w:
        raise RuntimeError("No window found in context.")

    desired_objs: List[bpy.types.Object] = []
    for child in bbpl.basics.get_recursive_obj_childs(obj):
        if bfu_export_control.bfu_export_control_utils.is_not_dont_export(child):
            if child.name in w.view_layer.objects:
                desired_objs.append(child)

    return desired_objs

class ProxyRigConsraint():
    def __init__(self, constraint: bpy.types.Constraint):
        self.constraint = constraint
        # STRETCH_TO
        if constraint.type == "STRETCH_TO":
            if isinstance(constraint, bpy.types.StretchToConstraint):
                self.rest_length = constraint.rest_length  # Can be bigger than 10?... wtf

        # LIMIT_LOCATION
        if constraint.type == "LIMIT_LOCATION":
            if isinstance(constraint, bpy.types.LimitLocationConstraint):
                self.min_x = constraint.min_x
                self.min_y = constraint.min_y
                self.min_z = constraint.min_z
                self.max_x = constraint.max_x
                self.max_y = constraint.max_y
                self.max_z = constraint.max_z

        # LIMIT_DISTANCE
        if constraint.type == "LIMIT_DISTANCE":
            if isinstance(constraint, bpy.types.LimitDistanceConstraint):
                self.distance = constraint.distance


class RigConsraintScale():

    def __init__(self, armature: bpy.types.Object, rescale_rig_factor: float):
        self.armature = armature
        if not isinstance(armature.data, bpy.types.Armature):
            raise TypeError(f"Object {armature.name} is not an armature")
        self.rescale_rig_factor: float = rescale_rig_factor  # rigRescaleFactor
        self.consraint_proxys: List[ProxyRigConsraint] = []

        if armature.pose:
            for bone in armature.pose.bones:
                for constraint in bone.constraints:
                    self.consraint_proxys.append(ProxyRigConsraint(constraint))

    def rescale_rig_consraint_for_unreal_engine(self):
        scale = self.rescale_rig_factor
        for consraint_proxy in self.consraint_proxys:
            constraint = consraint_proxy.constraint
            # STRETCH_TO
            if constraint.type == "STRETCH_TO":
                if isinstance(constraint, bpy.types.StretchToConstraint):
                    constraint.rest_length *= scale  # Can be bigger than 10?... wtf

            # LIMIT_LOCATION
            if constraint.type == "LIMIT_LOCATION":
                if isinstance(constraint, bpy.types.LimitLocationConstraint):
                    constraint.min_x *= scale
                    constraint.min_y *= scale
                    constraint.min_z *= scale
                    constraint.max_x *= scale
                    constraint.max_y *= scale
                    constraint.max_z *= scale

            # LIMIT_DISTANCE
            if constraint.type == "LIMIT_DISTANCE":
                if isinstance(constraint, bpy.types.LimitDistanceConstraint):
                    constraint.distance *= scale

    def reset_scale_after_export(self):
        for consraint_proxy in self.consraint_proxys:
            constraint = consraint_proxy.constraint
            # STRETCH_TO
            if constraint.type == "STRETCH_TO":
                if isinstance(constraint, bpy.types.StretchToConstraint):
                    constraint.rest_length = consraint_proxy.rest_length  # Can be bigger than 10?... wtf

            # LIMIT_LOCATION
            if constraint.type == "LIMIT_LOCATION":
                if isinstance(constraint, bpy.types.LimitLocationConstraint):
                    constraint.min_x = consraint_proxy.min_x
                    constraint.min_y = consraint_proxy.min_y
                    constraint.min_z = consraint_proxy.min_z
                    constraint.max_x = consraint_proxy.max_x
                    constraint.max_y = consraint_proxy.max_y
                    constraint.max_z = consraint_proxy.max_z

            # LIMIT_DISTANCE
            if constraint.type == "LIMIT_DISTANCE":
                if isinstance(constraint, bpy.types.LimitDistanceConstraint):
                    constraint.distance = consraint_proxy.distance


class ShapeKeysCurveScale():

    def __init__(self, rescale_rig_factor: float, is_a_proxy: bool = False):
        self.export_as_proxy = is_a_proxy
        self.rescale_rig_factor = rescale_rig_factor  # rigRescaleFactor
        self.default_unit_length = get_scene_unit_scale()
        self.proxy_drivers = self.shape_keys_driver_refs()  # Save driver data as proxy

    class DriverProxyData():
        def __init__(self, obj: bpy.types.Object, driver: bpy.types.FCurve):
            self.obj = obj
            self.driver = driver
            self.keyframe_points = []
            self.modifiers = []
            for key in self.driver.keyframe_points:
                self.keyframe_points.append(self.DriverKeyProxyData(key))

            for mod in self.driver.modifiers:
                self.modifiers.append(self.DriverModifierProxyData(mod))

        class DriverKeyProxyData():
            def __init__(self, key):
                self.co = key.co[1]
                self.handle_left = key.handle_left[1]
                self.handle_right = key.handle_right[1]

        class DriverModifierProxyData():
            def __init__(self, modifier):
                self.coefficients = modifier.coefficients

    def rescale_for_unreal_engine(self):
        scale = 1/self.rescale_rig_factor
        for proxy_driver in self.proxy_drivers:
            for key in proxy_driver.driver.keyframe_points:
                key.co[1] *= scale
                key.handle_left[1] *= scale
                key.handle_right[1] *= scale

            for mod in proxy_driver.driver.modifiers:
                if mod.type == "GENERATOR":
                    mod.coefficients[0] *= scale  # coef: +
                    mod.coefficients[1] *= scale  # coef: x

    def reset_scale_after_export(self):
        for proxy_driver in self.proxy_drivers:
            for x, key in enumerate(proxy_driver.driver.keyframe_points):
                key.co[1] = proxy_driver.keyframe_points[x].co
                key.handle_left[1] = proxy_driver.keyframe_points[x].handle_left
                key.handle_right[1] = proxy_driver.keyframe_points[x].handle_right

            for x, mod in enumerate(proxy_driver.driver.modifiers):
                if mod.type == "GENERATOR":
                    mod.coefficients[0] = proxy_driver.modifiers[x].scale  # coef: +
                    mod.coefficients[1] = proxy_driver.modifiers[x].scale  # coef: x

    def get_driver_key_block(self, proxy_drivers: DriverProxyData):
        pass
        #driver_split = driver.data_path.split('"')
        #if len(driver_split) >= 2:
        #    driver_name = driver_split[1]
        #    if driver_name in 
        #    bpy.context.selected_objects[0].data.shape_keys.key_blocks[1]

    def shape_keys_driver_refs(self):
        drivers: List[Any] = []
        obj_list = bpy.context.selected_objects

        if self.export_as_proxy is False:
            for obj in obj_list:
                if isinstance(obj.data, bpy.types.Mesh):
                    if obj.data.shape_keys is not None:
                        if obj.data.shape_keys.animation_data is not None:
                            for driver_curve in obj.data.shape_keys.animation_data.drivers:
                                # Check if has location context.
                                need_rescale_curve = False
                                driver = driver_curve.driver
                                if driver:
                                    for variable in driver.variables:
                                        if variable.type == "TRANSFORMS":
                                            for target in variable.targets:
                                                if "LOC" in target.transform_type:
                                                    need_rescale_curve = True
                                        elif variable.type == "LOC_DIFF":
                                            need_rescale_curve = True
                                    
                                    if need_rescale_curve:
                                        drivers.append(self.DriverProxyData(obj, driver_curve))
        return drivers


class ModifiersDataScale():

    def __init__(self, rescale_rig_factor, is_a_proxy=False):
        self.export_as_proxy = is_a_proxy
        self.rescale_rig_factor = rescale_rig_factor  # rigRescaleFactor
        self.modifiers = self.ModifiersRefs()  # Save driver data as proxy
        self.saved_data = {}


    def rescale_for_unreal_engine(self):
        for x, mod in enumerate(self.modifiers):
            if mod.type == "MIRROR":
                self.saved_data[x] = mod.merge_threshold
                mod.merge_threshold *= self.rescale_rig_factor


    def ResetScaleAfterExport(self):
        for x, mod in enumerate(self.modifiers):
            if mod.type == "MIRROR":
                mod.merge_threshold = self.saved_data[x]

    def ModifiersRefs(self):
        modifiers = []
        obj_list = bpy.context.selected_objects
        if self.export_as_proxy is False:
            for obj in obj_list:
                if obj.type == "MESH":
                    for mod in obj.modifiers:
                        modifiers.append(mod)
        return modifiers

def lerp_quaternion(q1: mathutils.Quaternion, q2: mathutils.Quaternion, alpha: float) -> mathutils.Quaternion:
    # Manual LERP because Blender lacks direct Quaternion.lerp()
    result = mathutils.Quaternion((
        (1 - alpha) * q1.w + alpha * q2.w,
        (1 - alpha) * q1.x + alpha * q2.x,
        (1 - alpha) * q1.y + alpha * q2.y,
        (1 - alpha) * q1.z + alpha * q2.z,
    ))
    result.normalize()
    return result

def evaluate_camera_position(camera: bpy.types.Object, previous_euler: mathutils.Euler = mathutils.Euler()) -> Tuple[mathutils.Vector, List[float], mathutils.Vector]:
    pass
    # TODO

def evaluate_camera_position_for_unreal(camera: bpy.types.Object, previous_euler: mathutils.Euler = mathutils.Euler()) -> Tuple[mathutils.Vector, List[float], mathutils.Vector]:
    # Get Transform
    if not isinstance(camera.data, bpy.types.Camera):
        raise TypeError(f"Object {camera.name} is not a camera")

    unit_scale = get_scene_unit_scale()
    display_size = camera.data.display_size

    matrix_y = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Y')
    matrix_x = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
    matrix: mathutils.Matrix = camera.matrix_world @ matrix_y @ matrix_x
    loc: mathutils.Vector = matrix.to_translation() * 100 * unit_scale
    if TYPE_CHECKING:
        additional_location_for_export: mathutils.Vector = mathutils.Vector((0, 0, 0))
    else:
        additional_location_for_export = camera.bfu_additional_location_for_export
    loc += additional_location_for_export
    rot: mathutils.Euler = matrix.to_euler("XYZ", previous_euler)
    scale: mathutils.Vector = matrix.to_scale() * unit_scale * display_size

    loc *= mathutils.Vector([1, -1, 1])
    array_rotation: List[float] = [math.degrees(rot[0]), math.degrees(rot[1])*-1, math.degrees(rot[2])*-1]  # Roll, Pitch, Yaw: XYZ
    array_transform: Tuple[mathutils.Vector, List[float], mathutils.Vector] = (loc, array_rotation, scale)

    return array_transform

def get_object_location_vector_for_unreal(obj: bpy.types.Object) -> mathutils.Vector:
    # Convert Blender location to Unreal Engine location (X, Y, Z) -> (X, -Y, Z) and scale to cm
    unit_scale = get_scene_unit_scale()
    unreal_location = obj.location * mathutils.Vector((1.0, -1.0, 1.0)) # Changes axis from Y to -Y
    unreal_location *= 100.0 * unit_scale # Convert to cm and apply unit scale
    return unreal_location

def get_object_euler_for_unreal(obj: bpy.types.Object) -> mathutils.Euler:
    # Convert Blender world rotation to Unreal-style components used by this addon:
    # Blender X -> Unreal Roll, Blender Y -> -Unreal Pitch, Blender Z -> -Unreal Yaw.
    blender_euler = obj.matrix_world.to_euler("XYZ", mathutils.Euler())
    return mathutils.Euler((-blender_euler.y, -blender_euler.z, blender_euler.x), "XYZ")

def get_object_scale_vector_for_unreal(obj: bpy.types.Object) -> mathutils.Vector:
    # Convert Blender scale to Unreal Engine scale (X, Y, Z) -> (X, Y, Z) and apply unit scale
    unit_scale = get_scene_unit_scale()
    unreal_scale = obj.scale * unit_scale
    return unreal_scale

def get_export_collection_objects(collection: bpy.types.Collection) -> List[bpy.types.Object]:
    # Found all objects that must be exported in a collection
    found_objs: List[bpy.types.Object] = []
    for select_obj in collection.all_objects:
        if bfu_export_control.bfu_export_control_utils.is_not_dont_export(select_obj):
            if select_obj.name in bpy.context.view_layer.objects:
                found_objs.append(select_obj)

    return found_objs

def draw_proxy_propertys(obj: bpy.types.Object):
    
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    # Debug option to alway show linked propertys
    if addon_prefs.show_hiden_linked_propertys:
        return True

    # Hide likned object propertys
    if GetExportAsProxy(obj):
        return False
    return True

# @TODO: @Deprecated
def GetExportAsProxy(obj: bpy.types.Object) -> bool:
    if get_obj_proxy_child(obj):
        return True

    if obj.data:
        if obj.data.library:
            return True
    return False

# @TODO: @Deprecated
def GetExportProxyChild(obj: bpy.types.Object) -> bpy.types.Object:

    if get_obj_proxy_child(obj):
        return get_obj_proxy_child(obj)

    scene = bpy.context.scene
    if obj.data:
        if obj.data.library:
            for child_obj in scene.objects:
                if child_obj != obj:
                    if child_obj.instance_collection:
                        if child_obj.instance_collection.library:
                            if child_obj.instance_collection.library == obj.data.library:
                                return child_obj
    return None

def SelectParentAndDesiredChilds(active: bpy.types.Object):
    # Selects only auto desired child objects that must be exported with parent object
    if active.name not in bpy.context.view_layer.objects:
        print(f"The active object {active.name} not found in bpy.context.view_layer.objects!")
        return

    new_select_list = []
    bpy.ops.object.select_all(action='DESELECT')
    for obj in get_export_desired_childs(active):
        if obj.name in bpy.context.view_layer.objects:
            new_select_list.append(obj)

    # Select active at end to move a list end
    new_select_list.append(active)

    # Select proxy at end to move a list end
    if GetExportAsProxy(active):
        proxy_child = GetExportProxyChild(active)
        if proxy_child is not None:
            new_select_list.append(proxy_child)

    return bbpl.utils.select_specific_object_list(active, new_select_list)


def SelectParentAndSpecificChilds(active: bpy.types.Object, objects: List[bpy.types.Object]):
    # Selects specific child objects that must be exported with parent object
    if active.name not in bpy.context.view_layer.objects:
        print(f"The active object {active.name} not found in bpy.context.view_layer.objects!")
        return

    new_select_list = []
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        if obj.name in bpy.context.view_layer.objects:
            new_select_list.append(obj)

    # Select active at end to move a list end
    new_select_list.append(active)

    if GetExportAsProxy(active):
        proxy_child = GetExportProxyChild(active)
        if proxy_child is not None:
            new_select_list.append(proxy_child)

    return bbpl.utils.select_specific_object_list(active, new_select_list)


def RemoveSocketFromSelectForProxyArmature():
    select = bbpl.save_data.select_save.UserSelectSave()
    select.save_current_select()
    # With skeletal mesh the socket must be not exported,
    # Unreal Engine read it like a bone
    sockets = []
    for obj in bpy.context.selected_objects:
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            sockets.append(obj)
    clean_delete_objects(sockets)
    select.reset_select(use_names = True)


def GoToMeshEditMode():
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            bbpl.utils.safe_mode_set('EDIT')

            return True
    return False


def CorrectExtremeUV(step_scale=2, move_to_absolute=False):
    
    def GetHaveConnectedLoop(faceTarget):
        # In bmesh faces
        for loop in faceTarget.loops:
            uv = loop[uv_lay].uv
            for face in bm.faces:
                if face.select:
                    if faceTarget != face:
                        for loop in face.loops:
                            if uv == loop[uv_lay].uv:
                                return True
        return False

    def SelectRecursiveUVLinked(uv_lay):

        AddedFaces = []
        for v in [v for v in bm.verts if v.select]:
            for f in v.link_faces:
                if not f.select:
                    if GetHaveConnectedLoop(f):
                        AddedFaces.append(f)
                        f.select = True

        if len(AddedFaces) == 0:
            return AddedFaces
        else:
            for addedFace in SelectRecursiveUVLinked(uv_lay):
                AddedFaces.append(addedFace)
            return AddedFaces

    def GetAllIsland(bm, uv_lay):
        ToCheakFace = []
        Islands = []
        for face in bm.faces:
            ToCheakFace.append(face)

        while len(ToCheakFace) > 0:
            for face in bm.faces:
                face.select = False

            ToCheakFace[-1].select = True
            SelectRecursiveUVLinked(uv_lay)

            Island = []
            for face in bm.faces:
                if face.select:
                    Island.append(face)
                    if face in ToCheakFace:
                        ToCheakFace.remove(face)
            Islands.append(Island)

        return Islands

    def MoveItlandToCenter(faces, uv_lay, min_distance, absolute):
        loop = faces[-1].loops[-1]

        delta_x = round(loop[uv_lay].uv[0]/min_distance, 0)*min_distance
        delta_y = round(loop[uv_lay].uv[1]/min_distance, 0)*min_distance

        for face in faces:
            for loop in face.loops:
                loop[uv_lay].uv[0] -= delta_x
                loop[uv_lay].uv[1] -= delta_y

        if(absolute == True):
            # Move Faces to make it alway positive
            for face in faces:
                for loop in face.loops:
                    loop[uv_lay].uv[0] = abs(loop[uv_lay].uv[0])
                    loop[uv_lay].uv[1] = abs(loop[uv_lay].uv[1])


    def IsValidForUvEdit(obj):
        if obj.type == "MESH":
            return True
        return False

    for obj in bpy.context.selected_objects:
        if IsValidForUvEdit(obj):
            # pylint: disable=E1128
            bm = bmesh.from_edit_mesh(obj.data)

            uv_lay = bm.loops.layers.uv.active
            if uv_lay is None:
                return

            for faces in GetAllIsland(bm, uv_lay):
                uv_lay = bm.loops.layers.uv.active
                MoveItlandToCenter(faces, uv_lay, step_scale, move_to_absolute)

            obj.data.update()



def apply_export_transform(obj: bpy.types.Object, use_type: str = "Object"):

    newMatrix = obj.matrix_world @ mathutils.Matrix.Translation((0, 0, 0))
    saveScale = obj.scale * 1

    # Ref
    # Moves object to the center of the scene for export
    if use_type == "Object":
        MoveToCenter = obj.bfu_move_to_center_for_export
        RotateToZero = obj.bfu_rotate_to_zero_for_export

    elif use_type == "Action":
        MoveToCenter = obj.bfu_move_action_to_center_for_export
        RotateToZero = obj.bfu_rotate_action_to_zero_for_export

    elif use_type == "NLA":
        MoveToCenter = obj.bfu_move_nla_to_center_for_export
        RotateToZero = obj.bfu_rotate_nla_to_zero_for_export

    else:
        return

    if MoveToCenter:
        mat_trans = mathutils.Matrix.Translation((0, 0, 0))
        mat_rot = newMatrix.to_quaternion().to_matrix()
        newMatrix = mat_trans @ mat_rot.to_4x4()

    obj.matrix_world = newMatrix
    # Turn object to the center of the scene for export
    if RotateToZero:
        mat_trans = mathutils.Matrix.Translation(newMatrix.to_translation())
        mat_rot = mathutils.Matrix.Rotation(0, 4, 'X')
        newMatrix = mat_trans @ mat_rot

    eul = obj.bfu_additional_rotation_for_export
    loc = obj.bfu_additional_location_for_export

    mat_rot = eul.to_matrix()
    mat_loc = mathutils.Matrix.Translation(loc)
    AddMat = mat_loc @ mat_rot.to_4x4()

    obj.matrix_world = newMatrix @ AddMat
    obj.scale = saveScale

# @TODO @Deprecated
class SceneUnitSettings():
    def __init__(self, scene):
        self.scene = scene
        self.default_scale_length = get_scene_unit_scale()

    def SetUnitForUnrealEngineExport(self):
        self.scene.unit_settings.scale_length = 0.01  # *= 1/rrf

    def ResetUnit(self):
        self.scene.unit_settings.scale_length = self.default_scale_length


class SkeletalExportScale():

    def __init__(self, armature):
        self.armature = armature
        self.default_armature_data = armature.data
        self.default_transform = armature.matrix_world.copy()

        # Save childs location
        self.childs = []
        for child in bbpl.basics.get_obj_childs(armature):
            self.childs.append(self.SkeletalChilds(child))

    class SkeletalChilds():
        def __init__(self, obj):
            self.obj = obj
            self.default_matrix_local = obj.matrix_local.copy()
            self.default_matrix_parent_inverse = obj.matrix_parent_inverse.copy()

        def ResetObjTransform(self):
            self.obj.matrix_local = self.default_matrix_local
            self.obj.matrix_parent_inverse = self.default_matrix_parent_inverse

    def ResetArmatureChildsTransform(self):
        for child in self.childs:
            child.ResetObjTransform()

    def apply_skeletal_export_scale(self, rescale: float, target_animation_data: bbpl.anim_utils.AnimationManagment=None):
        # This function will rescale the armature and applys the new scale

        armature = self.armature
        armature.scale = armature.scale*rescale

        # Save armature location
        old_location = armature.location.copy()

        if target_animation_data is None:
            armature_animation_data = bbpl.anim_utils.AnimationManagment()
            armature_animation_data.save_animation_data(armature)
            armature_animation_data.clear_animation_data(armature)
        else:
            armature_animation_data = bbpl.anim_utils.AnimationManagment()
            armature_animation_data.clear_animation_data(armature)

        # Need break multi users for apply scale.

        # armature.make_local()
        armature_data_copy_name = armature.data.name + "_copy"
        armature.data.make_local()
        armature.data.name = armature_data_copy_name

        bpy.ops.object.transform_apply(
            location=True,
            scale=True,
            rotation=True,
            properties=True
            )

        # Apply armature location
        armature.location = old_location*rescale

        if target_animation_data is None:
            armature_animation_data.set_animation_data(armature, True)
        else:
            target_animation_data.set_animation_data(armature, True)

    def ResetSkeletalExportScale(self):
        self.armature.data = self.default_armature_data
        self.armature.matrix_world = self.default_transform
        self.ResetArmatureChildsTransform()


def rescale_select_curve_hooks(scale: float):

    def get_rescaled_matrix(matrix: mathutils.Matrix, scale: float) -> mathutils.Matrix:
        newMatrix = matrix.copy()

        newMatrix[0][0] *= 1  # Fix
        newMatrix[0][1] *= 1
        newMatrix[0][2] *= 1
        newMatrix[0][3] *= scale
        # ---
        newMatrix[1][0] *= 1
        newMatrix[1][1] *= 1  # Fix
        newMatrix[1][2] *= 1  # Fix
        newMatrix[1][3] *= scale
        # ---
        newMatrix[2][0] *= 1
        newMatrix[2][1] *= 1  # Fix
        newMatrix[2][2] *= 1  # Fix
        newMatrix[2][3] *= scale
        # ---
        newMatrix[3][0] *= 1
        newMatrix[3][1] *= 1
        newMatrix[3][2] *= 1
        newMatrix[3][3] *= 1  # Fix

        return newMatrix

    for obj in bpy.context.selected_objects:
        if obj.type == "CURVE":
            for mod in obj.modifiers:
                if mod.type == "HOOK":
                    scale_factor = 100
                    mod.matrix_inverse = get_rescaled_matrix(
                        mod.matrix_inverse,
                        scale_factor
                        )
            for spline in obj.data.splines:
                for bezier_point in spline.bezier_points:
                    bezier_point.radius *= scale


class ActionCurveScale():

    def __init__(self, rescale_factor: float):
        self.rescale_factor = rescale_factor  # rigRescaleFactor
        self.default_unit_length = get_scene_unit_scale()
        self.print_debug = False  # Debug print

    def rescale_for_export(self):
        rf = self.rescale_factor
        length = self.default_unit_length
        self.rescale_all_action_curves(rf, length/0.01)

    def restore_scale_after_export(self):
        rf = self.rescale_factor
        length = self.default_unit_length

        self.rescale_all_action_curves(1/(rf), 0.01/length)


    def rescale_all_action_curves(self, bone_scale: float, scene_scale: float):

        if bpy.app.version >= (4, 4, 0):
            def rescale_all_action_curves_with_channelbag(bone_scale: float, scene_scale: float):

                def rescale_first_valid_channelbag(action: bpy.types.Action, slot: bpy.types.ActionSlot):
                    # Rescale the first valid channelbag in the slot
                    if not action.layers:
                        return False
                    
                    for layer in action.layers:
                        for strip in layer.strips:
                            channelbag = strip.channelbag(slot)
                            if channelbag:
                                rescale_location_fcurves(channelbag.fcurves)
                                return True

                for action in bpy.data.actions:
                    if self.print_debug:
                        print(f"Rescale: {action.name} bone_scale: {bone_scale} scene_scale: {scene_scale}")

                    for slot in action.slots:
                        rescale_first_valid_channelbag(action, slot)
            
            rescale_all_action_curves_with_channelbag(bone_scale, scene_scale)
        else:

            def rescale_all_action_curves_with_fcurves(bone_scale: float, scene_scale: float):

                def rescale_location_fcurves(fcurves: List[bpy.types.FCurve]):

                    def rescale_fcurve(fcurve: bpy.types.FCurve, scale: float):
                        # Rescale fcurve keyframe points
                        for key in fcurve.keyframe_points:
                            key.co[1] *= scale
                            key.handle_left[1] *= scale
                            key.handle_right[1] *= scale

                        # Rescale fcurve modifiers
                        for mod in fcurve.modifiers:
                            if mod.type == "NOISE":
                                mod.strength *= scale

                    for fcurve in fcurves:
                        # Rescale scene location curves
                        if fcurve.data_path == "location":
                            if self.print_debug:
                                    print(f"Rescale scene location: {fcurve.data_path}, scene_scale: {scene_scale}")
                            rescale_fcurve(fcurve, scene_scale)

                        # Rescale bone location curves
                        elif fcurve.data_path.split(".")[-1] == "location":
                            if self.print_debug:
                                print(f"Rescale bone location: {fcurve.data_path}, bone_scale: {bone_scale}")
                            rescale_fcurve(fcurve, bone_scale)

                for action in bpy.data.actions:
                    if self.print_debug:
                        print(f"Rescale: {action.name} bone_scale: {bone_scale} scene_scale: {scene_scale}")

                    rescale_location_fcurves(action.fcurves)

            rescale_all_action_curves_with_fcurves(bone_scale, scene_scale)



def ValidFilenameForUnreal(filename: str) -> str:
    # valid file name for unreal assets
    extension = os.path.splitext(filename)[1]
    newfilename = bfu_basics.valid_file_name(os.path.splitext(filename)[0])
    return (''.join(c for c in newfilename if c != ".")+extension)


def clean_filename_for_unreal(filename: str) -> str:
    # Normalizes string, removes non-alpha characters
    # Asset name in Unreal use

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename

def get_unreal_import_location():
    scene = bpy.context.scene

    dirpath = os.path.join(scene.bfu_unreal_import_module,scene.bfu_unreal_import_location)

    # Clean path
    dirpath = os.path.normpath(dirpath)
    return dirpath

def get_import_asset_script_command() -> str:
    scene = bpy.context.scene
    fileName = scene.bfu_file_import_asset_script_name
    absdirpath = Path(bpy.path.abspath(scene.bfu_export_other_file_path)).resolve()
    fullpath = absdirpath / fileName
    return 'py "'+str(fullpath)+'"'


def get_import_sequencer_script_command() -> str:
    scene = bpy.context.scene
    fileName = scene.bfu_file_import_sequencer_script_name
    absdirpath = Path(bpy.path.abspath(scene.bfu_export_other_file_path)).resolve()
    fullpath = absdirpath / fileName

    return 'py "'+str(fullpath)+'"'


def get_anim_sample(obj: bpy.types.Object) -> float:
    # return obj sample animation
    return obj.bfu_sample_anim_for_export


def get_armature_root_bones(armature: bpy.types.Object) -> List[bpy.types.Bone]:
    # DEPRECATED: Use bfu_skeletal_mesh.bfu_skeletal_mesh_utils.get_armature_root_bones()
    
    root_bones: List[bpy.types.Bone] = []
    if isinstance(armature.data, bpy.types.Armature):

        if armature.bfu_export_deform_only:
            for bone in armature.data.bones:
                if bone.use_deform:
                    rootBone = bfu_basics.get_root_bone_parent(bone)
                    if rootBone not in root_bones:
                        root_bones.append(rootBone)

        else:
            for bone in armature.data.bones:
                if bone.parent is None:
                    root_bones.append(bone)
    return root_bones


def get_desired_export_armature_name(obj: bpy.types.Object) -> str:
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    single_root = len(get_armature_root_bones(obj)) == 1
    if addon_prefs.add_skeleton_root_bone or single_root != 1:
        return addon_prefs.skeleton_root_bone_name
    return "Armature"


def GetObjExportScale(obj: bpy.types.Object) -> float:
    return obj.bfu_export_global_scale


def AddFrontEachLine(ImportScript: str, text: str = "\t") -> str:

    NewImportScript = ""
    text_splited = ImportScript.split('\n')
    for line in text_splited:
        NewImportScript += text + line + "\n"

    return NewImportScript


# Custom property


def set_var_on_object(obj, VarName, Value):
    obj[VarName] = Value


def get_var_on_object(obj, VarName):
    return obj[VarName]


def has_var_on_object(obj, VarName):
    return VarName in obj


def clear_var_on_object(obj, VarName):
    if VarName in obj:
        del obj[VarName]


def save_obj_current_name(obj: bpy.types.Object):
    # Save object current name as Custom property
    set_var_on_object(obj, "BFU_OriginName", obj.name)


def get_obj_origin_name(obj: bpy.types.Object) -> str:
    return get_var_on_object(obj, "BFU_OriginName")


def clear_obj_origin_name_var(obj: bpy.types.Object) -> None:
    clear_var_on_object(obj, "BFU_OriginName")


def set_obj_proxy_data(obj: bpy.types.Object):
    # Save object proxy info as Custom property
    set_var_on_object(obj, "BFU_ExportAsProxy", GetExportAsProxy(obj))
    set_var_on_object(obj, "BFU_ExportProxyChild", GetExportProxyChild(obj))


def get_obj_proxy_child(obj: bpy.types.Object) -> bool:
    if (not has_var_on_object(obj, "BFU_ExportAsProxy")):
        return False

    if (not has_var_on_object(obj, "BFU_ExportProxyChild")):
        return False

    if get_var_on_object(obj, "BFU_ExportAsProxy"):
        return get_var_on_object(obj, "BFU_ExportProxyChild")
    return None


def clear_obj_proxy_data_vars(obj: bpy.types.Object) -> None:
    clear_var_on_object(obj, "BFU_ExportAsProxy")
    clear_var_on_object(obj, "BFU_ExportProxyChild")


def clear_all_bfu_temp_vars(obj: bpy.types.Object) -> None:
    clear_var_on_object(obj, "BFU_OriginName")
    clear_var_on_object(obj, "BFU_ExportAsProxy")
    clear_var_on_object(obj, "BFU_ExportProxyChild")

def get_scene_unit_scale() -> float:
    #Have to round for avoid microscopic offsets.
    if bpy.context is None:
        return 1.0
    scene = bpy.context.scene
    return round(scene.unit_settings.scale_length, 8)

def get_scene_unit_scale_is_close(value: float) -> bool:
    #Check if value is close to scene unit class.
    scene = bpy.context.scene
    unit_scale = round(scene.unit_settings.scale_length, 8)
    return math.isclose(unit_scale, value, rel_tol=1e-5)

def check_path_valid(dirpath: Path) -> bool:
    """
    Check if the path is valid.
    If the path ends with a file extension, it will check the directory of that file.
    """
    absdirpath = dirpath.resolve()

    # If the path ends with an extension, it is assumed to be a file
    if absdirpath.suffix:
        absdirpath = absdirpath.parent

    try:
        if absdirpath.exists():
            # Path already exists so return True
            return True
    except Exception as e:
        # Path does a script fail so invalid.
        print(bpl.color_set.red(f"Invalid path: {absdirpath}"))
        error_text: str = f"An error occurred during makedirs: {str(e)}"
        print(error_text)
        return False

    return True

def check_and_make_export_path(dirpath: Path) -> bool:
    """
    Check if the directory exists, and create it if it doesn't.
    If the path ends with a file extension, it will create the directory of that file.
    """
    absdirpath = dirpath.resolve()

    # If the path ends with an extension, it is assumed to be a file
    if absdirpath.suffix:
        absdirpath = absdirpath.parent

    try:
        if absdirpath.exists():
            # Path already exists so return True
            return True
    except Exception as e:
        # Path does a script fail so invalid.
        print(bpl.color_set.red(f"Invalid path: {absdirpath}"))
        error_text: str = f"An error occurred during makedirs: {str(e)}"
        print(error_text)
        return False


    try:
        os.makedirs(absdirpath)
    except Exception as e:
        # Make dir does a script fail.
        print(bpl.color_set.red(f"Impossible to create path: {absdirpath}"))
        error_text: str = f"An error occurred during makedirs: {str(e)}"
        print(error_text)
        return False

    return True