# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
import bmesh
import string
import fnmatch
import mathutils
import math
import os
import math
import addon_utils
from typing import List
from . import bbpl
from . import bps
from . import bfu_basics

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
    def __init__(self, marker):
        scene = bpy.context.scene
        self.marker = marker
        self.start = 0
        self.end = scene.frame_end

        if marker is not None:
            self.start = marker.frame


class TimelineMarkerSequence():

    def __init__(self):
        scene = bpy.context.scene
        timeline = scene.timeline_markers
        self.marker_sequences: List[MarkerSequence] = self.GetMarkerSequences(timeline)

    def GetMarkerSequences(self, timeline_markers):
        if len(timeline_markers) == 0:
            print("Scene has no timeline_markers.")
            return []

        def GetFisrtMarket(marker_list):
            if len(marker_list) == 0:
                return None

            best_marker = ""
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

        marker_list = []
        for marker in timeline_markers:
            marker_list.append(marker)

        order_marker_list = []
        while len(marker_list) != 0:
            first_marker = GetFisrtMarket(marker_list)
            order_marker_list.append(first_marker)
            marker_list.remove(first_marker)

        marker_sequences = []

        for marker in order_marker_list:
            marker_sequence = MarkerSequence(marker)

            if len(marker_sequences) > 0:
                previous_marker_sequence = marker_sequences[-1]
                previous_marker_sequence.end = marker.frame - 1

            marker_sequences.append(marker_sequence)

        return marker_sequences

    def GetMarkerSequenceAtFrame(self, frame):
        if self.marker_sequences:
            for marker_sequence in self.marker_sequences:
                # print(marker_sequence.start, marker_sequence.end, frame)
                if frame >= marker_sequence.start and frame <= marker_sequence.end:
                    return marker_sequence
        return None

def UpdateProgress(job_title, progress, time=None):

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


def RemoveUselessSpecificData(name, data_type):
    if data_type == "MESH":
        if name in bpy.data.meshes:
            oldData = bpy.data.meshes[name]
            if oldData.users == 0:
                bpy.data.meshes.remove(oldData)

    if data_type == "ARMATURE":
        if name in bpy.data.armatures:
            oldData = bpy.data.armatures[name]
            if oldData.users == 0:
                bpy.data.armatures.remove(oldData)


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
        RemoveUselessSpecificData(data[0], data[1])

    return removed_objects


def CleanDeleteObjects(objs):

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
            RemoveUselessSpecificData(oldDataToRemove, oldDataTypeToRemove)

    return removed_objects


def GetAllobjectsByExportType(exportType):
    # Find all objects with a specific bfu_export_type property
    targetObj = []
    for obj in bpy.context.scene.objects:
        prop = obj.bfu_export_type
        if prop == exportType:
            targetObj.append(obj)
    return (targetObj)


def GetAllCollisionAndSocketsObj(objs_list=None):
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


def GetExportDesiredChilds(obj):
    # Get only all child objects that must be exported with parent object

    DesiredObj = []
    for child in bfu_basics.GetRecursiveChilds(obj):
        if child.bfu_export_type != "dont_export":
            if child.name in bpy.context.window.view_layer.objects:
                DesiredObj.append(child)

    return DesiredObj


def GetSocketDesiredChild(targetObj):
    sockets = []
    for obj in GetExportDesiredChilds(targetObj):
        if IsASocket(obj):
            sockets.append(obj)

    return sockets


def GetSkeletalMeshSockets(obj):
    if obj is None:
        return
    if obj.type != "ARMATURE":
        return

    addon_prefs = bfu_basics.GetAddonPrefs()
    data = {}
    sockets = []

    for socket in GetSocketDesiredChild(obj):
        sockets.append(socket)

    if GetAssetType(obj) != "SkeletalMesh":
        return

    data['Sockets'] = []
    # config.set('Sockets', '; SocketName, BoneName, Location, Rotation, Scale')

    for socket in sockets:
        if IsASocket(socket):
            SocketName = socket.name[7:]

        if socket.parent is None:
            print("Socket ", socket.name, " parent is None!")
            break
        if socket.parent.type != "ARMATURE":
            print("Socket parent", socket.parent.name, " parent is not and Armature!")
            break

        if socket.parent.bfu_export_deform_only:
            b = bfu_basics.getFirstDeformBoneParent(socket.parent.data.bones[socket.parent_bone])
        else:
            b = socket.parent.data.bones[socket.parent_bone]

        bbpl.anim_utils.reset_armature_pose(socket.parent)
        # GetRelativePostion
        bml = b.matrix_local  # Bone
        am = socket.parent.matrix_world  # Armature
        em = socket.matrix_world  # Socket
        RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
        t = RelativeMatrix.to_translation()
        r = RelativeMatrix.to_euler()
        s = socket.scale*addon_prefs.skeletalSocketsImportedSize

        # Convet to array for Json and convert value for Unreal
        if obj.bfu_skeleton_export_procedure == 'ue-standard':
            array_location = [t[0], t[1]*-1, t[2]]
            array_rotation = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]
            array_scale = [s[0], s[1], s[2]]
        else:
            array_location = [t[0], t[1]*-1, t[2]]
            array_rotation = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]
            array_scale = [s[0], s[1], s[2]]

        MySocket = {}
        MySocket["SocketName"] = SocketName
        MySocket["BoneName"] = b.name.replace('.', '_')
        MySocket["Location"] = array_location
        MySocket["Rotation"] = array_rotation
        MySocket["Scale"] = array_scale
        data['Sockets'].append(MySocket)

    return data['Sockets']


def GetSubObjectDesiredChild(targetObj):
    sub_objects = []
    for obj in GetExportDesiredChilds(targetObj):
        if IsASubObject(obj):
            sub_objects.append(obj)

    return sub_objects


def RemoveAllConsraints(obj):
    for b in obj.pose.bones:
        for c in b.constraints:
            b.constraints.remove(c)


class RigConsraintScale():

    def __init__(self, armature, rescale_rig_factor):
        self.armature = armature
        self.rescale_rig_factor = rescale_rig_factor  # rigRescaleFactor
        self.consraint_proxys = []

        class ProxyRigConsraint():
            def __init__(self, constraint):
                self.constraint = constraint
                # STRETCH_TO
                if constraint.type == "STRETCH_TO":
                    self.rest_length = constraint.rest_length  # Can be bigger than 10?... wtf

                # LIMIT_LOCATION
                if constraint.type == "LIMIT_LOCATION":
                    self.min_x = constraint.min_x
                    self.min_y = constraint.min_y
                    self.min_z = constraint.min_z
                    self.max_x = constraint.max_x
                    self.max_y = constraint.max_y
                    self.max_z = constraint.max_z

                # LIMIT_DISTANCE
                if constraint.type == "LIMIT_DISTANCE":
                    self.distance = constraint.distance

        for bone in armature.pose.bones:
            for constraint in bone.constraints:
                self.consraint_proxys.append(ProxyRigConsraint(constraint))

    def RescaleRigConsraintForUnrealEngine(self):
        scale = self.rescale_rig_factor
        for consraint_proxy in self.consraint_proxys:
            c = consraint_proxy.constraint
            # STRETCH_TO
            if c.type == "STRETCH_TO":
                c.rest_length *= scale  # Can be bigger than 10?... wtf

            # LIMIT_LOCATION
            if c.type == "LIMIT_LOCATION":
                c.min_x *= scale
                c.min_y *= scale
                c.min_z *= scale
                c.max_x *= scale
                c.max_y *= scale
                c.max_z *= scale

            # LIMIT_DISTANCE
            if c.type == "LIMIT_DISTANCE":
                c.distance *= scale

    def ResetScaleAfterExport(self):
        for consraint_proxy in self.consraint_proxys:
            c = consraint_proxy.constraint
            # STRETCH_TO
            if c.type == "STRETCH_TO":
                c.rest_length = consraint_proxy.rest_length  # Can be bigger than 10?... wtf

            # LIMIT_LOCATION
            if c.type == "LIMIT_LOCATION":
                c.min_x = consraint_proxy.min_x
                c.min_y = consraint_proxy.min_y
                c.min_z = consraint_proxy.min_z
                c.max_x = consraint_proxy.max_x
                c.max_y = consraint_proxy.max_y
                c.max_z = consraint_proxy.max_z

            # LIMIT_DISTANCE
            if c.type == "LIMIT_DISTANCE":
                c.distance = consraint_proxy.distance


class ShapeKeysCurveScale():

    def __init__(self, rescale_rig_factor, is_a_proxy=False):
        self.export_as_proxy = is_a_proxy
        self.rescale_rig_factor = rescale_rig_factor  # rigRescaleFactor
        self.default_unit_length = get_scene_unit_scale()
        self.proxy_drivers = self.ShapeKeysDriverRefs()  # Save driver data as proxy

    class DriverProxyData():
        def __init__(self, driver):
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

    def ResacleForUnrealEngine(self):
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

    def ResetScaleAfterExport(self):
        for proxy_driver in self.proxy_drivers:
            for x, key in enumerate(proxy_driver.driver.keyframe_points):
                key.co[1] = proxy_driver.keyframe_points[x].co
                key.handle_left[1] = proxy_driver.keyframe_points[x].handle_left
                key.handle_right[1] = proxy_driver.keyframe_points[x].handle_right

            for x, mod in enumerate(proxy_driver.driver.modifiers):
                if mod.type == "GENERATOR":
                    mod.coefficients[0] = proxy_driver.modifiers[x].scale  # coef: +
                    mod.coefficients[1] = proxy_driver.modifiers[x].scale  # coef: x

    def ShapeKeysDriverRefs(self):
        drivers = []
        if self.export_as_proxy is False:
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    if obj.data.shape_keys is not None:
                        if obj.data.shape_keys.animation_data is not None:
                            if obj.data.shape_keys.animation_data.drivers is not None:
                                for driver in obj.data.shape_keys.animation_data.drivers:
                                    drivers.append(self.DriverProxyData(driver))
        return drivers


def GetAllCollisionObj():
    # Get any object that can be understood
    # as a collision or a socket by unreal

    colObjs = [obj for obj in bpy.context.scene.objects if (
        fnmatch.fnmatchcase(obj.name, "UBX*") or
        fnmatch.fnmatchcase(obj.name, "UCP*") or
        fnmatch.fnmatchcase(obj.name, "USP*") or
        fnmatch.fnmatchcase(obj.name, "UCX*"))]
    return colObjs

def EvaluateCameraPosition(camera):
    # Get Transfrom
    loc = camera.matrix_world.to_translation()
    r = camera.matrix_world.to_euler("XYZ")
    s = camera.matrix_world.to_scale()
    array_transform = [loc, r, s]
    return array_transform

def EvaluateCameraPositionForUnreal(camera, previous_euler=mathutils.Euler()):
    # Get Transfrom
    unit_scale = get_scene_unit_scale()
    matrix_y = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Y')
    matrix_x = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
    matrix = camera.matrix_world @ matrix_y @ matrix_x
    loc = matrix.to_translation() * 100 * unit_scale
    loc += camera.bfu_additional_location_for_export
    r = matrix.to_euler("XYZ", previous_euler)
    s = matrix.to_scale() * unit_scale

    loc *= mathutils.Vector([1, -1, 1])
    array_rotation = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]  # Roll Pith Yaw XYZ
    array_transform = [loc, array_rotation, s]

    return array_transform


def EvaluateCameraRotationForBlender(transform):
    x = transform["rotation_x"]
    y = transform["rotation_y"]*-1
    z = transform["rotation_z"]*-1
    euler = mathutils.Euler([x, y, z], "XYZ")
    return euler


def GetDesiredActionStartEndTime(obj, action):
    # Returns desired action or camera anim start/end time
    # Return start with index 0 and end with index 1
    # EndTime should be a less one frame bigger than StartTime

    scene = bpy.context.scene
    if obj.type == "CAMERA":
        startTime = scene.frame_start
        endTime = scene.frame_end
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif obj.bfu_anim_action_start_end_time_enum == "with_keyframes":
        # GetFirstActionFrame + Offset
        startTime = int(action.frame_range.x) + obj.bfu_anim_action_start_frame_offset
        # GetLastActionFrame + Offset
        endTime = int(action.frame_range.y) + obj.bfu_anim_action_end_frame_offset
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif obj.bfu_anim_action_start_end_time_enum == "with_sceneframes":
        startTime = scene.frame_start + obj.bfu_anim_action_start_frame_offset
        endTime = scene.frame_end + obj.bfu_anim_action_end_frame_offset
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif obj.bfu_anim_action_start_end_time_enum == "with_customframes":
        startTime = obj.bfu_anim_action_custom_start_frame
        endTime = obj.bfu_anim_action_custom_end_frame
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)


def GetDesiredNLAStartEndTime(obj):
    # Returns desired nla anim start/end time
    # Return start with index 0 and end with index 1
    # EndTime should be a less one frame bigger than StartTime

    scene = bpy.context.scene

    if obj.bfu_anim_nla_start_end_time_enum == "with_sceneframes":
        startTime = scene.frame_start + obj.bfu_anim_nla_start_frame_offset
        endTime = scene.frame_end + obj.bfu_anim_nla_end_frame_offset
        if endTime <= startTime:
            endTime = startTime+1

        return (startTime, endTime)

    elif obj.bfu_anim_nla_start_end_time_enum == "with_customframes":
        startTime = obj.bfu_anim_nla_custom_start_frame
        endTime = obj.bfu_anim_nla_custom_end_frame
        if endTime <= startTime:
            endTime = startTime+1

        return (startTime, endTime)


def GetUseCustomLightMapResolution(obj):
    if obj.bfu_static_mesh_light_map_mode == "Default":
        return False
    return True


def GetExportRealSurfaceArea(obj):

    local_view_areas = bbpl.scene_utils.move_to_global_view()
    bbpl.utils.safe_mode_set('OBJECT')

    SavedSelect = bbpl.utils.UserSelectSave()
    SavedSelect.save_current_select()
    SelectParentAndDesiredChilds(obj)

    bpy.ops.object.duplicate()
    bpy.ops.object.duplicates_make_real(
        use_base_parent=True,
        use_hierarchy=True
        )

    ApplyNeededModifierToSelect()
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for selectObj in bpy.context.selected_objects:
        # Remove unable to convert mesh
        if selectObj.type == "EMPTY" or selectObj.type == "CURVE":
            CleanDeleteObjects([selectObj])

    for selectObj in bpy.context.selected_objects:
        # Remove collision box
        if CheckIsCollision(selectObj):
            CleanDeleteObjects([selectObj])

    if bpy.context.view_layer.objects.active is None:
        # When the active id a empty
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')

    active = bpy.context.view_layer.objects.active

    CleanJoinSelect()
    active = bpy.context.view_layer.objects.active
    area = bfu_basics.GetSurfaceArea(active)
    CleanDeleteObjects(bpy.context.selected_objects)
    SavedSelect.reset_select_by_ref()
    bbpl.scene_utils.move_to_local_view(local_view_areas)
    return area


def GetCompuntedLightMap(obj):
    if obj.bfu_static_mesh_light_map_mode == "Default":
        return -1

    if obj.bfu_static_mesh_light_map_mode == "CustomMap":
        return obj.bfu_static_mesh_custom_light_map_res

    if obj.bfu_static_mesh_light_map_mode == "SurfaceArea":
        # Get the area
        area = obj.computedStaticMeshLightMapRes
        area **= 0.5  # Adapte for light map

        if obj.bfu_use_static_mesh_light_map_world_scale:
            # Turn area at world scale
            x = max(obj.scale.x, obj.scale.x*-1)
            y = max(obj.scale.y, obj.scale.y*-1)
            z = max(obj.scale.z, obj.scale.z*-1)
            objScale = (x + y + z)/3
            area *= objScale

        # Computed light map equal light map scale for a plane vvv
        area *= get_scene_unit_scale()
        area *= obj.bfu_static_mesh_light_map_surface_scale/2
        if obj.bfu_static_mesh_light_map_round_power_of_two:

            return bps.math.nearest_power_of_two(int(round(area)))
        return int(round(area))


def GetActionType(action):
    # return action type

    if action.frame_range.y - action.frame_range.x == 1:
        return "Pose"
    return "Action"


def GetCollectionType(collection):
    # return collection type
    if(collection):
        return "Collection StaticMesh"


def GetIsAnimation(animation_type):
    # return True if type(string) is a animation
    if (animation_type == "NlAnim" or animation_type == "Action" or animation_type == "Pose"):
        return True
    return False


def GetAssetType(obj):
    # Return asset type of a object

    if obj.type == "CAMERA":
        return "Camera"

    if obj.bfu_export_as_alembic:
        return "Alembic"

    if obj.type == "ARMATURE" and not obj.bfu_export_skeletal_mesh_as_static_mesh:
        return "SkeletalMesh"
    
    if obj.type == "CURVE" and not obj.bfu_export_spline_as_static_mesh:
        return "Spline"

    return "StaticMesh"


def CheckIsCollision(target):
    # Return true if obj is a collision
    for obj in GetAllCollisionObj():
        if obj == target:
            return True
    return False


def SelectCollectionObjects(collection):
    # Selects only all objects that must be exported in a collection
    selectedObjs = []
    bpy.ops.object.select_all(action='DESELECT')
    for selectObj in collection.all_objects:
        if selectObj.bfu_export_type != "dont_export":
            if selectObj.name in bpy.context.view_layer.objects:
                selectObj.select_set(True)
                selectedObjs.append(selectObj)

    if len(selectedObjs) > 0:
        if selectedObjs[0].name in bpy.context.view_layer.objects:
            bpy.context.view_layer.objects.active = selectedObjs[0]

    return selectedObjs


def GetExportAsProxy(obj):
    if GetObjProxyChild(obj):
        return True

    if obj.data:
        if obj.data.library:
            return True
    return False


def GetExportProxyChild(obj):

    if GetObjProxyChild(obj):
        return GetObjProxyChild(obj)

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


def SelectParentAndDesiredChilds(obj):
    # Selects only auto desired child objects that must be exported with parent object
    selectedObjs = []
    bpy.ops.object.select_all(action='DESELECT')
    for selectObj in GetExportDesiredChilds(obj):
        if selectObj.name in bpy.context.view_layer.objects:
            if GetAssetType(obj) == "SkeletalMesh":
                # With skeletal mesh the socket must be not exported,
                # ue4 read it like a bone
                if not fnmatch.fnmatchcase(selectObj.name, "SOCKET*"):
                    selectObj.select_set(True)
                    selectedObjs.append(selectObj)
            else:
                selectObj.select_set(True)
                selectedObjs.append(selectObj)

    if obj.name in bpy.context.view_layer.objects:
        obj.select_set(True)

    if GetExportAsProxy(obj):
        proxy_child = GetExportProxyChild(obj)
        if proxy_child is not None:
            proxy_child.select_set(True)

    selectedObjs.append(obj)
    if obj.name in bpy.context.view_layer.objects:
        bpy.context.view_layer.objects.active = obj
    return selectedObjs


def SelectParentAndSpecificChilds(active, objects):
    # Selects specific child objects that must be exported with parent object
    selectedObjs = []
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        if obj.name in bpy.context.view_layer.objects:
            if GetAssetType(active) == "SkeletalMesh":
                # With skeletal mesh the socket must be not exported,
                # ue4 read it like a bone
                if not fnmatch.fnmatchcase(obj.name, "SOCKET*"):
                    obj.select_set(True)
                    selectedObjs.append(obj)
            else:
                obj.select_set(True)
                selectedObjs.append(obj)

    if active.name in bpy.context.view_layer.objects:
        active.select_set(True)

    if GetExportAsProxy(active):
        proxy_child = GetExportProxyChild(active)
        if proxy_child is not None:
            proxy_child.select_set(True)

    selectedObjs.append(active)
    if active.name in bpy.context.view_layer.objects:
        bpy.context.view_layer.objects.active = active
    return selectedObjs


def RemoveSocketFromSelectForProxyArmature():
    select = bbpl.utils.UserSelectSave()
    select.save_current_select()
    # With skeletal mesh the socket must be not exported,
    # ue4 read it like a bone
    sockets = []
    for obj in bpy.context.selected_objects:
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            sockets.append(obj)
    CleanDeleteObjects(sockets)
    select.reset_select_by_name()


def GoToMeshEditMode():
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            bbpl.utils.safe_mode_set('EDIT')

            return True
    return False


def ApplyNeededModifierToSelect():

    SavedSelect = bbpl.utils.UserSelectSave()
    SavedSelect.save_current_select()
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            bbpl.utils.select_specific_object(obj)
            for mod in [m for m in obj.modifiers if m.type != 'ARMATURE']:
                if obj.data.shape_keys is None:
                    if obj.data.users > 1:
                        obj.data = obj.data.copy()
                    if bpy.ops.object.modifier_apply.poll():
                        try:
                            bpy.ops.object.modifier_apply(modifier=mod.name)
                        except RuntimeError as ex:
                            # print the error incase its important... but continue
                            print(ex)

    SavedSelect.reset_select_by_ref()


def CorrectExtremeUV(stepScale=2):

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

    def MoveItlandToCenter(faces, uv_lay, minDistance):
        loop = faces[-1].loops[-1]

        x = round(loop[uv_lay].uv[0]/minDistance, 0)*minDistance
        y = round(loop[uv_lay].uv[1]/minDistance, 0)*minDistance

        for face in faces:
            for loop in face.loops:
                loop[uv_lay].uv[0] -= x
                loop[uv_lay].uv[1] -= y

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
                MoveItlandToCenter(faces, uv_lay, stepScale)

            obj.data.update()


def ApplyExportTransform(obj, use_type="Object"):

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
        for child in bfu_basics.GetChilds(armature):
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

    def ApplySkeletalExportScale(self, rescale, target_animation_data=None, is_a_proxy=False):
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

        if is_a_proxy:
            SavedSelect = bbpl.utils.UserSelectSave()
            SavedSelect.save_current_select()
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)

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
        if is_a_proxy:
            SavedSelect.reset_select_by_ref()

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


def RescaleSelectCurveHook(scale):

    def GetRescaledMatrix(matrix, scale):
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
                    mod.matrix_inverse = GetRescaledMatrix(
                        mod.matrix_inverse,
                        scale_factor
                        )
            for spline in obj.data.splines:
                for bezier_point in spline.bezier_points:
                    bezier_point.radius *= scale


class ActionCurveScale():

    def __init__(self, rescale_factor):
        self.rescale_factor = rescale_factor  # rigRescaleFactor
        self.default_unit_length = get_scene_unit_scale()

    def ResacleForUnrealEngine(self):
        rf = self.rescale_factor
        length = self.default_unit_length

        self.RescaleAllActionCurve(rf, length/0.01)

    def ResetScaleAfterExport(self):
        rf = self.rescale_factor
        length = self.default_unit_length

        self.RescaleAllActionCurve(1/(rf), 0.01/length)

    def RescaleAllActionCurve(self, bone_scale, scene_scale=1):
        for action in bpy.data.actions:
            # print(action.name)
            for fcurve in action.fcurves:
                if fcurve.data_path == "location":
                    # Curve
                    for key in fcurve.keyframe_points:
                        key.co[1] *= scene_scale
                        key.handle_left[1] *= scene_scale
                        key.handle_right[1] *= scene_scale

                    # Modifier
                    for mod in fcurve.modifiers:
                        if mod.type == "NOISE":
                            mod.strength *= scene_scale

                elif fcurve.data_path.split(".")[-1] == "location":

                    # Curve
                    for key in fcurve.keyframe_points:
                        key.co[1] *= bone_scale
                        key.handle_left[1] *= bone_scale
                        key.handle_right[1] *= bone_scale

                    # Modifier
                    for mod in fcurve.modifiers:
                        if mod.type == "NOISE":
                            mod.strength *= bone_scale



def ValidFilenameForUnreal(filename):
    # valid file name for unreal assets
    extension = os.path.splitext(filename)[1]
    newfilename = bfu_basics.ValidFilename(os.path.splitext(filename)[0])
    return (''.join(c for c in newfilename if c != ".")+extension)


def ValidUnrealAssetsName(filename):
    # Normalizes string, removes non-alpha characters
    # Asset name in Unreal use

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename


def GetCollectionExportDir(col, abspath=False):
    # Generate assset folder path
    scene = bpy.context.scene

    dirpath = os.path.join(
        scene.bfu_export_static_file_path,
        col.bfu_export_folder_name)

    if abspath:
        return bpy.path.abspath(dirpath)
    else:
        return dirpath


def GetObjExportName(obj):
    # Return Proxy Name for Proxy and Object Name for other
    if GetAssetType(obj) == "SkeletalMesh":
        if GetExportAsProxy(obj):
            proxy_child = GetExportProxyChild(obj)
            if proxy_child is not None:
                return proxy_child.name
    return bfu_basics.ValidFilename(obj.name)


def GetObjExportDir(obj, abspath=False):
    # Generate assset folder path
    folder_name = bfu_basics.ValidDirName(obj.bfu_export_folder_name)
    obj_name = bfu_basics.ValidDirName(obj.name)  # Fix obj name

    scene = bpy.context.scene
    if GetAssetType(obj) == "SkeletalMesh":
        dirpath = os.path.join(
            scene.bfu_export_skeletal_file_path,
            folder_name,
            GetObjExportName(obj))
    if GetAssetType(obj) == "Alembic":
        dirpath = os.path.join(
            scene.bfu_export_alembic_file_path,
            folder_name,
            obj_name)
    if GetAssetType(obj) == "StaticMesh":
        dirpath = os.path.join(
            scene.bfu_export_static_file_path,
            folder_name)
    if GetAssetType(obj) == "Camera":
        dirpath = os.path.join(
            scene.bfu_export_camera_file_path,
            folder_name)
    if GetAssetType(obj) == "Spline":
        dirpath = os.path.join(
            scene.bfu_export_spline_file_path,
            folder_name)
    if abspath:
        return bpy.path.abspath(dirpath)

    else:
        return dirpath


def GetImportAssetScriptCommand():
    scene = bpy.context.scene
    fileName = scene.bfu_file_import_asset_script_name
    absdirpath = bpy.path.abspath(scene.bfu_export_other_file_path)
    fullpath = os.path.join(absdirpath, fileName)
    return 'py "'+fullpath+'"'




def GetImportSkeletalMeshSocketScriptCommand(obj):

    if obj:
        if obj.type == "ARMATURE":
            sockets = GetSkeletalMeshSockets(obj)
            t = "SocketCopyPasteBuffer" + "\n"
            t += "NumSockets=" + str(len(sockets)) + "\n"
            t += "IsOnSkeleton=1" + "\n"
            for socket in sockets:
                t += "Begin Object Class=/Script/Engine.SkeletalMeshSocket" + "\n"
                t += "\t" + 'SocketName="' + socket["SocketName"] + '"' + "\n"
                t += "\t" + 'BoneName="' + socket["BoneName"] + '"' + "\n"
                loc = socket["Location"]
                r = socket["Rotation"]
                s = socket["Scale"]
                t += "\t" + 'RelativeLocation=' + "(X="+str(loc[0])+",Y="+str(loc[1])+",Z="+str(loc[2])+")" + "\n"
                t += "\t" + 'RelativeRotation=' + "(Pitch="+str(r[1])+",Yaw="+str(r[2])+",Roll="+str(r[0])+")" + "\n"
                t += "\t" + 'RelativeScale=' + "(X="+str(s[0])+",Y="+str(s[1])+",Z="+str(s[2])+")" + "\n"
                t += "End Object" + "\n"
            return t
    return "Please select an armature."


def GetImportSequencerScriptCommand():
    scene = bpy.context.scene
    fileName = scene.bfu_file_import_sequencer_script_name
    absdirpath = bpy.path.abspath(scene.bfu_export_other_file_path)
    fullpath = os.path.join(absdirpath, fileName)

    return 'py "'+fullpath+'"'  # Vania


def GetAnimSample(obj):
    # return obj sample animation
    return obj.bfu_sample_anim_for_export


def GetArmatureRootBones(obj):
    rootBones = []
    if GetAssetType(obj) == "SkeletalMesh":

        if not obj.bfu_export_deform_only:
            for bone in obj.data.bones:
                if bone.parent is None:
                    rootBones.append(bone)

        if obj.bfu_export_deform_only:
            for bone in obj.data.bones:
                if bone.use_deform:
                    rootBone = bfu_basics.getRootBoneParent(bone)
                    if rootBone not in rootBones:
                        rootBones.append(rootBone)
    return rootBones


def GetDesiredExportArmatureName(obj):
    addon_prefs = bfu_basics.GetAddonPrefs()
    single_root = len(GetArmatureRootBones(obj)) == 1
    if addon_prefs.add_skeleton_root_bone or single_root != 1:
        return addon_prefs.skeleton_root_bone_name
    return "Armature"


def GetObjExportScale(obj):
    return obj.bfu_export_global_scale


def GenerateUe4Name(name):
    # Generate a new name with suffix number

    def IsValidName(testedName):
        # Checks if objet end with number suffix

        if (testedName.split("_")[-1]).isnumeric():
            number = int(testedName.split("_")[-1])
        else:
            # Last suffix is not a number
            return False

        # Checks if an object uses this name. (If not is a valid name)
        for obj in bpy.context.scene.objects:
            if testedName == obj.name:
                return False

        return True

    newName = ""
    if IsValidName(name):
        return name
    else:
        for num in range(0, 1000):
            newName = name+"_"+str('%02d' % num)  # Min two pad
            if IsValidName(newName):
                return newName

    return name


def CreateCollisionMaterial():
    addon_prefs = bfu_basics.GetAddonPrefs()

    mat = bpy.data.materials.get("UE4Collision")
    if mat is None:
        mat = bpy.data.materials.new(name="UE4Collision")

    mat.diffuse_color = addon_prefs.collisionColor
    mat.use_nodes = False
    if bpy.context.scene.render.engine == 'CYCLES':
        # sets up the nodes to create a transparent material
        # with GLSL mat in Cycle
        mat.use_nodes = True
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (0, 0)
        mix = nodes.new('ShaderNodeMixShader')
        mix.location = (-200, 000)
        mix.inputs[0].default_value = (0.95)
        diff = nodes.new('ShaderNodeBsdfDiffuse')
        diff.location = (-400, 100)
        diff.inputs[0].default_value = (0, 0.6, 0, 1)
        trans = nodes.new('ShaderNodeBsdfTransparent')
        trans.location = (-400, -100)
        trans.inputs[0].default_value = (0, 0.6, 0, 1)
        node_tree.links.new(diff.outputs['BSDF'], mix.inputs[1])
        node_tree.links.new(trans.outputs['BSDF'], mix.inputs[2])
        node_tree.links.new(mix.outputs['Shader'], out.inputs[0])
    return mat


def Ue4SubObj_set(SubType):
    # Convect obj to ue4 sub objects
    # (Collisions Shapes or Socket)

    def DeselectAllWithoutActive():
        for obj in bpy.context.selected_objects:
            if obj != bpy.context.active_object:
                obj.select_set(False)

    ownerObj = bpy.context.active_object
    objList = bpy.context.selected_objects
    if ownerObj is None:
        return []

    ConvertedObjs = []

    for obj in objList:
        DeselectAllWithoutActive()
        obj.select_set(True)
        if obj != ownerObj:

            # SkeletalMesh Colider
            if obj.type == 'MESH':
                bfu_basics.ConvertToConvexHull(obj)
                obj.modifiers.clear()
                obj.data.materials.clear()
                obj.active_material_index = 0
                obj.data.materials.append(CreateCollisionMaterial())

                # Set the name of the Prefix depending on the
                # type of collision in agreement with unreal FBX Pipeline
                if SubType == "Box":
                    prefixName = "UBX_"
                elif SubType == "Capsule":
                    prefixName = "UCP_"
                elif SubType == "Sphere":
                    prefixName = "USP_"
                elif SubType == "Convex":
                    prefixName = "UCX_"

                obj.name = GenerateUe4Name(prefixName+ownerObj.name)
                obj.show_wire = True
                obj.show_transparent = True
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                ConvertedObjs.append(obj)

            # StaticMesh Socket
            if obj.type == 'EMPTY' and SubType == "ST_Socket":
                if ownerObj.type == 'MESH':
                    if IsASocket(obj):
                        obj.name = GenerateUe4Name(obj.name)
                    else:
                        obj.name = GenerateUe4Name("SOCKET_"+obj.name)
                    bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)
                    ConvertedObjs.append(obj)

            # SkeletalMesh Socket
            if obj.type == 'EMPTY' and SubType == "SKM_Socket":
                if ownerObj.type == 'ARMATURE':

                    if IsASocket(obj):
                        obj.name = GenerateUe4Name(obj.name)
                    else:
                        obj.name = GenerateUe4Name("SOCKET_"+obj.name)
                    bpy.ops.object.parent_set(type='BONE',keep_transform=True)
                    ConvertedObjs.append(obj)

    DeselectAllWithoutActive()
    for obj in objList:
        obj.select_set(True)  # Resets previous selected object
    return ConvertedObjs


def UpdateUe4Name(SubType, objList):
    # Convect obj to ue4 sub objects (Collisions Shapes or Socket)

    for obj in objList:
        ownerObj = obj.parent

        if ownerObj is not None:
            if obj != ownerObj:

                # SkeletalMesh Colider
                if obj.type == 'MESH':

                    # Set the name of the Prefix depending
                    # on the type of collision in agreement
                    # with unreal FBX Pipeline

                    if SubType == "Box":
                        prefixName = "UBX_"
                    elif SubType == "Capsule":
                        prefixName = "UCP_"
                    elif SubType == "Sphere":
                        prefixName = "USP_"
                    elif SubType == "Convex":
                        prefixName = "UCX_"

                    obj.name = GenerateUe4Name(prefixName+ownerObj.name)

                # StaticMesh Socket
                if obj.type == 'EMPTY' and SubType == "ST_Socket":
                    if ownerObj.type == 'MESH':
                        if not IsASocket(obj):
                            obj.name = GenerateUe4Name("SOCKET_"+obj.name)

                # SkeletalMesh Socket
                if obj.type == 'EMPTY' and SubType == "SKM_Socket":
                    if ownerObj.type == 'ARMATURE':
                        if not IsASocket(obj):
                            obj.name = GenerateUe4Name("SOCKET_"+obj.name)


def IsASocket(obj):
    '''
    Retrun True is object is an Socket.
    https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/FBX/StaticMeshes/#sockets
    '''
    if obj.type == "EMPTY":
        cap_name = obj.name.upper()
        if cap_name.startswith("SOCKET_"):
            return True

    return False


def IsACollision(obj):
    '''
    Retrun True is object is an Collision.
    https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/FBX/StaticMeshes/#collision
    '''
    if obj.type == "MESH":
        cap_name = obj.name.upper()
        if cap_name.startswith("UBX_"):
            return True
        elif cap_name.startswith("UCP_"):
            return True
        elif cap_name.startswith("USP_"):
            return True
        elif cap_name.startswith("UCX_"):
            return True

    return False


def IsASubObject(obj):
    '''
    Retrun True is object is an Socket or and Collision.
    '''
    if IsASocket(obj) or IsACollision(obj):
        return True
    return False


def UpdateAreaLightMapList(objects_to_update=None):
    # Updates area LightMap

    if objects_to_update is not None:
        objs = objects_to_update
    else:
        objs = []
        exportObjs = GetAllobjectsByExportType("export_recursive")
        for exportObj in exportObjs:
            if GetAssetType(exportObj) == "StaticMesh":
                objs.append(exportObj)

    UpdatedRes = 0

    counter = bps.utils.CounterTimer()
    for obj in objs:
        obj.computedStaticMeshLightMapRes = GetExportRealSurfaceArea(obj)
        UpdatedRes += 1
        UpdateProgress(
            "Update LightMap",
            (UpdatedRes/len(objs)),
            counter.get_time())
    return UpdatedRes


def AddFrontEachLine(ImportScript, text="\t"):

    NewImportScript = ""
    text_splited = ImportScript.split('\n')
    for line in text_splited:
        NewImportScript += text + line + "\n"

    return NewImportScript


# Custom property


def SetVarOnObject(obj, VarName, Value):
    obj[VarName] = Value


def GetVarOnObject(obj, VarName):
    return obj[VarName]


def HasVarOnObject(obj, VarName):
    return VarName in obj


def ClearVarOnObject(obj, VarName):
    if VarName in obj:
        del obj[VarName]


def SaveObjCurrentName(obj):
    # Save object current name as Custom property
    SetVarOnObject(obj, "BFU_OriginName", obj.name)


def GetObjOriginName(obj):
    return GetVarOnObject(obj, "BFU_OriginName")


def ClearObjOriginNameVar(obj):
    ClearVarOnObject(obj, "BFU_OriginName")


def SetObjProxyData(obj):
    # Save object proxy info as Custom property
    SetVarOnObject(obj, "BFU_ExportAsProxy", GetExportAsProxy(obj))
    SetVarOnObject(obj, "BFU_ExportProxyChild", GetExportProxyChild(obj))


def GetObjProxyChild(obj):
    if (not HasVarOnObject(obj, "BFU_ExportAsProxy")):
        return False

    if (not HasVarOnObject(obj, "BFU_ExportProxyChild")):
        return False

    if GetVarOnObject(obj, "BFU_ExportAsProxy"):
        return GetVarOnObject(obj, "BFU_ExportProxyChild")
    return None


def ClearObjProxyDataVars(obj):
    ClearVarOnObject(obj, "BFU_ExportAsProxy")
    ClearVarOnObject(obj, "BFU_ExportProxyChild")


def ClearAllBFUTempVars(obj):
    ClearVarOnObject(obj, "BFU_OriginName")
    ClearVarOnObject(obj, "BFU_ExportAsProxy")
    ClearVarOnObject(obj, "BFU_ExportProxyChild")

def get_scene_unit_scale():
    #Have to round for avoid microscopic offsets.
    scene = bpy.context.scene
    return round(scene.unit_settings.scale_length, 8)

def get_scene_unit_scale_is_close(value: float):
    #Check if value is close to scene unit class.
    scene = bpy.context.scene
    unit_scale = round(scene.unit_settings.scale_length, 8)
    return math.isclose(unit_scale, value, rel_tol=1e-5)