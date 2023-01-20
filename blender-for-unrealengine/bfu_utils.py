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
import fnmatch
import mathutils
import math
import time
import sys
from . import bbpl

from math import degrees, radians, tan
from mathutils import Matrix

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)


from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *


class SavedObject():

    def __init__(self, obj):
        if obj:
            self.name = obj.name
            self.select = obj.select_get()
            self.hide = obj.hide_get()
            self.hide_select = obj.hide_select
            self.hide_viewport = obj.hide_viewport


class SavedBones():

    def __init__(self, bone):
        if bone:
            self.name = bone.name
            self.select = bone.select
            self.hide = bone.hide


class SavedCollection():

    def __init__(self, col):
        if col:
            self.name = col.name
            self.hide_select = col.hide_select
            self.hide_viewport = col.hide_viewport


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


class UserSelectSave():
    def __init__(self):

        # Select
        self.user_active = None
        self.user_active_name = ""
        self.user_selecteds = []
        self.user_selected_names = []

        # Stats
        self.user_mode = None

    def SaveCurrentSelect(self):
        # Save data (This can take time)

        c = bpy.context
        # Select
        self.user_active = c.active_object  # Save current active object
        if self.user_active:
            self.user_active_name = self.user_active.name

        self.user_selecteds = c.selected_objects  # Save current selected objects
        self.user_selected_names = []
        for obj in c.selected_objects:
            self.user_selected_names.append(obj.name)

    def ResetSelectByRef(self):
        self.SaveMode()
        bbpl.utils.SafeModeSet("OBJECT", bpy.ops.object)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:  # Resets previous selected object if still exist
            if obj in self.user_selecteds:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = self.user_active

        self.ResetModeAtSave()

    def ResetSelectByName(self):

        self.SaveMode()
        bbpl.utils.SafeModeSet("OBJECT", bpy.ops.object)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.name in self.user_selected_names:
                if obj.name in bpy.context.view_layer.objects:
                    bpy.data.objects[obj.name].select_set(True)  # Use the name because can be duplicated name

        if self.user_active_name != "":
            if self.user_active_name in bpy.data.objects:
                if self.user_active_name in bpy.context.view_layer.objects:
                    bpy.context.view_layer.objects.active = bpy.data.objects[self.user_active_name]

        self.ResetModeAtSave()

    def SaveMode(self):
        if self.user_active:
            if bpy.ops.object.mode_set.poll():
                self.user_mode = self.user_active.mode  # Save current mode

    def ResetModeAtSave(self):
        if self.user_mode:
            if bpy.ops.object:
                bbpl.utils.SafeModeSet(self.user_mode, bpy.ops.object)


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
        self.marker_sequences = self.GetMarkerSequences(timeline)

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


class CounterTimer():

    def __init__(self):
        self.start = time.perf_counter()

    def ResetTime(self):
        self.start = time.perf_counter()

    def GetTime(self):
        return time.perf_counter()-self.start


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


def RemoveUselessSpecificData(name, type):
    if type == "MESH":
        if name in bpy.data.meshes:
            oldData = bpy.data.meshes[name]
            if oldData.users == 0:
                bpy.data.meshes.remove(oldData)

    if type == "ARMATURE":
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
    # Find all objects with a specific ExportEnum property
    targetObj = []
    for obj in bpy.context.scene.objects:
        prop = obj.ExportEnum
        if prop == exportType:
            targetObj.append(obj)
    return(targetObj)


def GetAllCollisionAndSocketsObj(list=None):
    # Get any object that can be understood
    # as a collision or a socket by unreal

    if list is not None:
        objs = list
    else:
        objs = bpy.context.scene.objects

    colObjs = [obj for obj in objs if(
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
    for child in GetRecursiveChilds(obj):
        if child.ExportEnum != "dont_export":
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

    addon_prefs = GetAddonPrefs()
    data = {}
    sockets = []

    for socket in GetSocketDesiredChild(obj):
        sockets.append(socket)

    if GetAssetType(obj) != "SkeletalMesh":
        return

    data['Sockets'] = []
    # config.set('Sockets', '; SocketName, BoneName, Location, Rotation, Scale')

    for i, socket in enumerate(sockets):
        if IsASocket(socket):
            SocketName = socket.name[7:]
        else:
            socket.name

        if socket.parent.exportDeformOnly:
            b = getFirstDeformBoneParent(socket.parent.data.bones[socket.parent_bone])
        else:
            b = socket.parent.data.bones[socket.parent_bone]

        ResetArmaturePose(socket.parent)
        # GetRelativePostion
        bml = b.matrix_local  # Bone
        am = socket.parent.matrix_world  # Armature
        em = socket.matrix_world  # Socket
        RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
        t = RelativeMatrix.to_translation()
        r = RelativeMatrix.to_euler()
        s = socket.scale*addon_prefs.skeletalSocketsImportedSize

        # Convet to array for Json and convert value for Unreal
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


def RescaleRigConsraints(obj, scale):
    for b in obj.pose.bones:
        for c in b.constraints:
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


def RescaleShapeKeysCurve(obj, scale):
    if obj.data.shape_keys is None:  # Optimisation
        return
    if obj.data.shape_keys.animation_data is None:
        return
    if obj.data.shape_keys.animation_data.drivers is None:
        return

    for driver in obj.data.shape_keys.animation_data.drivers:
        for key in driver.keyframe_points:
            key.co[1] *= scale
            key.handle_left[1] *= scale
            key.handle_right[1] *= scale

        for mod in driver.modifiers:
            if mod.type == "GENERATOR":
                mod.coefficients[0] *= scale  # coef: +
                mod.coefficients[1] *= scale  # coef: x


def GetAllCollisionObj():
    # Get any object that can be understood
    # as a collision or a socket by unreal

    colObjs = [obj for obj in bpy.context.scene.objects if (
        fnmatch.fnmatchcase(obj.name, "UBX*") or
        fnmatch.fnmatchcase(obj.name, "UCP*") or
        fnmatch.fnmatchcase(obj.name, "USP*") or
        fnmatch.fnmatchcase(obj.name, "UCX*"))]
    return colObjs


def GetCollectionToExport(scene):
    colExport = []
    for col in scene.CollectionExportList:
        if col.use:
            if col.name in bpy.data.collections:
                collection = bpy.data.collections[col.name]
                colExport.append(collection)
    return colExport


class CachedAction():

    '''
    I can't use bpy.types.Scene or bpy.types.Object Property.
    "Writing to ID classes in this context is not allowed"
    So I use simple python var
    '''

    class ActionFromCache():
        # Info about actions from last cache.
        def __init__(self, action):
            self.total_action_fcurves_len = len(action.fcurves)

    def __init__(self):
        self.name = ""
        self.is_cached = False
        self.stored_actions = []
        self.total_actions = []
        self.total_rig_bone_len = 0

    def CheckCache(self, obj):
        # Check if the cache need update
        if self.name != obj.name:
            self.is_cached = False
        if len(bpy.data.actions) != len(self.total_actions):
            self.is_cached = False
        if len(obj.data.bones) != self.total_rig_bone_len:
            self.is_cached = False
        for action_name in self.stored_actions:
            if action_name not in bpy.data.actions:
                self.is_cached = False

        return self.is_cached

    def StoreActions(self, obj, actions):
        # Update new cache
        self.name = obj.name
        action_name_list = []
        for action in actions:
            action_name_list.append(action.name)
        self.stored_actions = action_name_list
        self.total_actions.clear()
        for action in bpy.data.actions:
            self.total_actions.append(self.ActionFromCache(action))
        self.total_rig_bone_len = len(obj.data.bones)
        self.is_cached = True
        # print("Stored action cache updated.")

    def GetStoredActions(self):
        actions = []
        for action_name in self.stored_actions:
            if action_name in bpy.data.actions:
                actions.append(bpy.data.actions[action_name])
        return actions

    def Clear(self):
        pass


MyCachedActions = CachedAction()


def UpdateActionCache(obj):
    # Force update cache export auto action list
    return GetCachedExportAutoActionList(obj, True)


def GetCachedExportAutoActionList(obj, force_update_cache=False):
    # This will cheak if the action contains
    # the same bones of the armature

    actions = []

    # Use the cache
    if force_update_cache:
        MyCachedActions.is_cached = False

    if MyCachedActions.CheckCache(obj):
        actions = MyCachedActions.GetStoredActions()

    else:
        MyCachedActions.Clear()

        objBoneNames = [bone.name for bone in obj.data.bones]
        for action in bpy.data.actions:
            if action.library is None:
                if GetIfActionIsAssociated(action, objBoneNames):
                    actions.append(action)
        # Update the cache
        MyCachedActions.StoreActions(obj, actions)
    return actions


def GetActionToExport(obj):
    # Returns only the actions that will be exported with the Armature

    if obj.ExportAsLod:
        return []

    TargetActionToExport = []  # Action list
    if obj.exportActionEnum == "dont_export":
        return []

    if obj.exportActionEnum == "export_current":
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                return [obj.animation_data.action]

    elif obj.exportActionEnum == "export_specific_list":
        for action in bpy.data.actions:
            for targetAction in obj.exportActionList:
                if targetAction.use:
                    if targetAction.name == action.name:
                        TargetActionToExport.append(action)

    elif obj.exportActionEnum == "export_specific_prefix":
        for action in bpy.data.actions:
            if fnmatch.fnmatchcase(action.name, obj.PrefixNameToExport+"*"):
                TargetActionToExport.append(action)

    elif obj.exportActionEnum == "export_auto":
        TargetActionToExport = GetCachedExportAutoActionList(obj)

    return TargetActionToExport


def EvaluateCameraPositionForUnreal(camera, previous_euler=mathutils.Euler()):
    # Get Transfrom
    matrix_y = Matrix.Rotation(radians(90.0), 4, 'Y')
    matrix_x = Matrix.Rotation(radians(-90.0), 4, 'X')
    matrix = camera.matrix_world @ matrix_y @ matrix_x
    matrix_rotation_offset = Matrix.Rotation(camera.AdditionalRotationForExport.z, 4, 'Z')
    loc = matrix.to_translation() * 100 * bpy.context.scene.unit_settings.scale_length
    loc += camera.AdditionalLocationForExport
    r = matrix.to_euler("XYZ", previous_euler)
    s = matrix.to_scale()

    loc *= mathutils.Vector([1, -1, 1])
    array_rotation = [degrees(r[0]), degrees(r[1])*-1, degrees(r[2])*-1]  # Roll Pith Yaw XYZ
    array_transform = [loc, array_rotation, s]

    # array_location = [loc[0], loc[1]*-1, loc[2]]
    # r = mathutils.Euler([degrees(r[0]), degrees(r[1])*-1, degrees(r[2])*-1], r.order)  # Roll Pith Yaw XYZ
    # array_transform = [array_location, r, s]

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

    elif obj.AnimStartEndTimeEnum == "with_keyframes":
        # GetFirstActionFrame + Offset
        startTime = int(action.frame_range.x) + obj.StartFramesOffset
        # GetLastActionFrame + Offset
        endTime = int(action.frame_range.y) + obj.EndFramesOffset
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif obj.AnimStartEndTimeEnum == "with_sceneframes":
        startTime = scene.frame_start + obj.StartFramesOffset
        endTime = scene.frame_end + obj.EndFramesOffset
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif obj.AnimStartEndTimeEnum == "with_customframes":
        startTime = obj.AnimCustomStartTime
        endTime = obj.AnimCustomEndTime
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)


def GetUseCustomLightMapResolution(obj):
    if obj.StaticMeshLightMapEnum == "Default":
        return False
    return True


def GetExportRealSurfaceArea(obj):
    scene = bpy.context.scene

    local_view_areas = MoveToGlobalView()
    bbpl.utils.SafeModeSet('OBJECT')

    SavedSelect = GetCurrentSelection()
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
    area = GetSurfaceArea(active)
    CleanDeleteObjects(bpy.context.selected_objects)
    SetCurrentSelection(SavedSelect)
    MoveToLocalView(local_view_areas)
    return area


def GetCompuntedLightMap(obj):
    if obj.StaticMeshLightMapEnum == "Default":
        return -1

    if obj.StaticMeshLightMapEnum == "CustomMap":
        return obj.customStaticMeshLightMapRes

    if obj.StaticMeshLightMapEnum == "SurfaceArea":
        # Get the area
        area = obj.computedStaticMeshLightMapRes
        area **= 0.5  # Adapte for light map

        if obj.useStaticMeshLightMapWorldScale:
            # Turn area at world scale
            x = max(obj.scale.x, obj.scale.x*-1)
            y = max(obj.scale.y, obj.scale.y*-1)
            z = max(obj.scale.z, obj.scale.z*-1)
            objScale = (x + y + z)/3
            area *= objScale

        # Computed light map equal light map scale for a plane vvv
        area *= bpy.context.scene.unit_settings.scale_length
        area *= obj.staticMeshLightMapSurfaceScale/2
        if obj.staticMeshLightMapRoundPowerOfTwo:

            return nearestPowerOfTwo(int(round(area)))
        return int(round(area))


def GetActionType(action):
    # return action type

    if action.frame_range.y - action.frame_range.x == 1:
        return "Pose"
    return "Action"


def GetCollectionType(collection):
    # return collection type

    return "Collection StaticMesh"


def GetIsAnimation(type):
    # return True if type(string) is a animation
    if (type == "NlAnim" or type == "Action" or type == "Pose"):
        return True
    return False


def GetAssetType(obj):
    # Return asset type of a object

    if obj.type == "CAMERA":
        return "Camera"

    if obj.ExportAsAlembic:
        return "Alembic"

    if obj.type == "ARMATURE" and not obj.ForceStaticMesh:
        return "SkeletalMesh"

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
        if selectObj.ExportEnum != "dont_export":
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
    # Selects only all child objects that must be exported with parent object
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


def RemoveSocketFromSelectForProxyArmature():
    select = UserSelectSave()
    select.SaveCurrentSelect()
    # With skeletal mesh the socket must be not exported,
    # ue4 read it like a bone
    sockets = []
    for obj in bpy.context.selected_objects:
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            sockets.append(obj)
    CleanDeleteObjects(sockets)
    select.ResetSelectByName()


def GoToMeshEditMode():
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            bbpl.utils.SafeModeSet('EDIT')

            return True
    return False


def ApplyNeededModifierToSelect():

    SavedSelect = GetCurrentSelection()
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            SelectSpecificObject(obj)
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

    SetCurrentSelection(SavedSelect)


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
        MoveToCenter = obj.MoveToCenterForExport
        RotateToZero = obj.RotateToZeroForExport

    elif use_type == "Action":
        MoveToCenter = obj.MoveActionToCenterForExport
        RotateToZero = obj.RotateActionToZeroForExport

    elif use_type == "NLA":
        MoveToCenter = obj.MoveNLAToCenterForExport
        RotateToZero = obj.RotateNLAToZeroForExport

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

    eul = obj.AdditionalRotationForExport
    loc = obj.AdditionalLocationForExport

    mat_rot = eul.to_matrix()
    mat_loc = mathutils.Matrix.Translation(loc)
    AddMat = mat_loc @ mat_rot.to_4x4()

    obj.matrix_world = newMatrix @ AddMat
    obj.scale = saveScale


def ApplySkeletalExportScale(armature, rescale, target_animation_data=None, is_a_proxy=False):

    # This function will rescale the armature and applys the new scale

    armature.scale = armature.scale*rescale
    # Save armature location
    old_location = armature.location.copy()

    if target_animation_data is None:
        armature_animation_data = bbpl.anim_utils.AnimationManagment()
        armature_animation_data.SaveAnimationData(armature)
        armature_animation_data.ClearAnimationData(armature)
    else:
        armature_animation_data = bbpl.anim_utils.AnimationManagment()
        armature_animation_data.ClearAnimationData(armature)

    armature.location = (0, 0, 0)

    # Save childs location
    ChildsLocation = []
    for Child in GetChilds(armature):
        ChildsLocation.append([Child, Child.location.copy(), Child.matrix_parent_inverse.copy()])

    if is_a_proxy:
        selection = GetCurrentSelection()
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)

    bpy.ops.object.transform_apply(
        location=True,
        scale=True,
        rotation=True,
        properties=True
        )

    if is_a_proxy:
        SetCurrentSelection(selection)

    # Apply armature location
    armature.location = old_location*rescale

    # Apply childs location
    # I need work with matrix ChildLocation[0].matrix_parent_inverse
    # But I don't understand how make it work.
    for ChildLocation in ChildsLocation:
        pass

    if target_animation_data is None:
        armature_animation_data.SetAnimationData(armature, True)
    else:
        target_animation_data.SetAnimationData(armature, True)


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


def RescaleActionCurve(action, scale):
    for fcurve in action.fcurves:
        if fcurve.data_path.split(".")[-1] == "location":
            for key in fcurve.keyframe_points:
                key.co[1] *= scale
                key.handle_left[1] *= scale
                key.handle_right[1] *= scale

            # Modifier
            for mod in fcurve.modifiers:
                if mod.type == "NOISE":
                    mod.strength *= scale


def RescaleAllActionCurve(bone_scale, scene_scale=1):
    for action in bpy.data.actions:
        print(action.name)
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


def GetFinalAssetToExport():
    # Returns all assets that will be exported

    def getHaveParentToExport(obj):
        if obj.parent is not None:
            if obj.parent.ExportEnum == 'export_recursive':
                return obj.parent
            else:
                return getHaveParentToExport(obj.parent)
        else:
            return None

    scene = bpy.context.scene
    export_filter = scene.bfu_export_selection_filter

    TargetAssetToExport = []  # Obj, Action, type

    class AssetToExport:
        def __init__(self, obj, action, type):
            self.obj = obj
            self.action = action
            self.type = type

    objList = []
    collectionList = []

    if export_filter == "default":
        objList = GetAllobjectsByExportType("export_recursive")
        for col in GetCollectionToExport(scene):
            collectionList.append(col.name)

    elif export_filter == "only_object" or export_filter == "only_object_action":
        recuList = GetAllobjectsByExportType("export_recursive")

        for obj in bpy.context.selected_objects:
            if obj in recuList:
                if obj not in objList:
                    objList.append(obj)
            parentTarget = getHaveParentToExport(obj)
            if parentTarget is not None:
                if parentTarget not in objList:
                    objList.append(parentTarget)

    for collection in collectionList:
        # Collection
        if scene.static_collection_export:
            TargetAssetToExport.append(AssetToExport(
                collection,
                None,
                "Collection StaticMesh"))

    for obj in objList:
        if GetAssetType(obj) == "Alembic":
            # Alembic
            if scene.alembic_export:
                TargetAssetToExport.append(AssetToExport(
                    obj,
                    None,
                    "Alembic"))

        if GetAssetType(obj) == "SkeletalMesh":

            # SkeletalMesh
            if scene.skeletal_export:
                TargetAssetToExport.append(AssetToExport(
                    obj,
                    None,
                    "SkeletalMesh"))

            # NLA
            if scene.anin_export:
                if obj.ExportNLA:
                    TargetAssetToExport.append(AssetToExport(
                        obj,
                        obj.animation_data,
                        "NlAnim"))

            for action in GetActionToExport(obj):
                if scene.bfu_export_selection_filter == "only_object_action":
                    if obj.animation_data:
                        if obj.animation_data.action == action:
                            TargetAssetToExport.append(AssetToExport(obj, action, "Action"))
                else:
                    # Action
                    if scene.anin_export:
                        if GetActionType(action) == "Action":
                            TargetAssetToExport.append(AssetToExport(obj, action, "Action"))

                    # Pose
                    if scene.anin_export:
                        if GetActionType(action) == "Pose":
                            TargetAssetToExport.append(AssetToExport(obj, action, "Pose"))
        # Camera
        if GetAssetType(obj) == "Camera" and scene.camera_export:
            TargetAssetToExport.append(AssetToExport(
                obj,
                None,
                "Camera"))

        # StaticMesh
        if GetAssetType(obj) == "StaticMesh" and scene.static_export:
            TargetAssetToExport.append(AssetToExport(
                obj,
                None,
                "StaticMesh"))

    return TargetAssetToExport


def ValidFilenameForUnreal(filename):
    # valid file name for unreal assets
    extension = os.path.splitext(filename)[1]
    newfilename = ValidFilename(os.path.splitext(filename)[0])
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
        scene.export_static_file_path,
        col.exportFolderName)

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
    return ValidFilename(obj.name)


def GetObjExportDir(obj, abspath=False):
    # Generate assset folder path
    FolderName = ValidDirName(obj.exportFolderName)

    scene = bpy.context.scene
    if GetAssetType(obj) == "SkeletalMesh":
        dirpath = os.path.join(
            scene.export_skeletal_file_path,
            FolderName,
            GetObjExportName(obj))
    if GetAssetType(obj) == "Alembic":
        dirpath = os.path.join(
            scene.export_alembic_file_path,
            FolderName,
            obj.name)
    if GetAssetType(obj) == "StaticMesh":
        dirpath = os.path.join(
            scene.export_static_file_path,
            FolderName)
    if GetAssetType(obj) == "Camera":
        dirpath = os.path.join(
            scene.export_camera_file_path,
            FolderName)
    if abspath:
        return bpy.path.abspath(dirpath)
    else:
        return dirpath


def GetCollectionExportFileName(collection, fileType=".fbx"):
    # Generate assset file name

    scene = bpy.context.scene
    return scene.static_mesh_prefix_export_name+collection+fileType


def GetObjExportFileName(obj, fileType=".fbx"):
    # Generate assset file name

    scene = bpy.context.scene
    if obj.bfu_use_custom_export_name:
        return ValidFilename(obj.bfu_custom_export_name+fileType)
    assetType = GetAssetType(obj)
    if assetType == "Camera":
        return ValidFilename(scene.camera_prefix_export_name+obj.name+fileType)
    elif assetType == "StaticMesh":
        return ValidFilename(scene.static_mesh_prefix_export_name+obj.name+fileType)
    elif assetType == "SkeletalMesh":
        return ValidFilename(scene.skeletal_mesh_prefix_export_name+obj.name+fileType)
    elif assetType == "Alembic":
        return ValidFilename(scene.alembic_prefix_export_name+obj.name+fileType)
    else:
        return None


def GetActionExportFileName(obj, action, fileType=".fbx"):
    # Generate action file name

    scene = bpy.context.scene
    if obj.bfu_anim_naming_type == "include_armature_name":
        ArmatureName = obj.name+"_"
    if obj.bfu_anim_naming_type == "action_name":
        ArmatureName = ""
    if obj.bfu_anim_naming_type == "include_custom_name":
        ArmatureName = obj.bfu_anim_naming_custom+"_"

    animType = GetActionType(action)
    if animType == "NlAnim" or animType == "Action":
        # Nla can be exported as action
        return ValidFilename(scene.anim_prefix_export_name+ArmatureName+action.name+fileType)

    elif animType == "Pose":
        return ValidFilename(scene.pose_prefix_export_name+ArmatureName+action.name+fileType)

    else:
        return None


def GetNLAExportFileName(obj, fileType=".fbx"):
    # Generate action file name

    scene = bpy.context.scene
    if obj.bfu_anim_naming_type == "include_armature_name":
        ArmatureName = obj.name+"_"
    if obj.bfu_anim_naming_type == "action_name":
        ArmatureName = ""
    if obj.bfu_anim_naming_type == "include_custom_name":
        ArmatureName = obj.bfu_anim_naming_custom+"_"

    return ValidFilename(scene.anim_prefix_export_name+ArmatureName+obj.NLAAnimName+fileType)


def GetImportAssetScriptCommand():
    scene = bpy.context.scene
    fileName = scene.file_import_asset_script_name
    absdirpath = bpy.path.abspath(scene.export_other_file_path)
    fullpath = os.path.join(absdirpath, fileName)
    addon_prefs = GetAddonPrefs()
    return 'py "'+fullpath+'"'


def GetImportCameraScriptCommand(objs, CineCamera=True):
    # Return (success, command)

    success = False
    command = ""
    report = ""
    add_camera_num = 0

    def AddCameraToCommand(camera):
        if camera.type == "CAMERA":
            t = ""
            # Get Camera Data
            scene = bpy.context.scene
            frame_current = scene.frame_current

            # First I get the camera data.
            # This is a very bad way to do this. I need do a new python file specific to camera with class to get data.
            data = bfu_write_text.WriteCameraAnimationTracks(camera, frame_current, frame_current)
            transform_track = data["Camera transform"][frame_current]
            location_x = transform_track["location_x"]
            location_y = transform_track["location_y"]
            location_z = transform_track["location_z"]
            rotation_x = transform_track["rotation_x"]
            rotation_y = transform_track["rotation_y"]
            rotation_z = transform_track["rotation_z"]
            scale_x = transform_track["scale_x"]
            scale_y = transform_track["scale_y"]
            scale_z = transform_track["scale_z"]
            NearClippingPlane = data["Camera NearClippingPlane"][frame_current]
            FarClippingPlane = data["Camera FarClippingPlane"][frame_current]
            FieldOfView = data["Camera FieldOfView"][frame_current]
            FocalLength = data["Camera FocalLength"][frame_current]
            SensorWidth = data["Camera SensorWidth"][frame_current]
            SensorHeight = data["Camera SensorHeight"][frame_current]
            FocusDistance = data["Camera FocusDistance"][frame_current]
            Aperture = data["Camera Aperture"][frame_current]
            AspectRatio = data["desired_screen_ratio"]
            CameraName = camera.name

            # Actor
            if CineCamera:
                t += "      " + "Begin Actor Class=/Script/CinematicCamera.CineCameraActor Name="+CameraName+" Archetype=/Script/CinematicCamera.CineCameraActor'/Script/CinematicCamera.Default__CineCameraActor'" + "\n"
            else:
                t += "      " + "Begin Actor Class=/Script/Engine.CameraActor Name="+CameraName+" Archetype=/Script/Engine.CameraActor'/Script/Engine.Default__CameraActor'" + "\n"

            # Init SceneComponent
            if CineCamera:
                t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/CinematicCamera.Default__CineCameraActor:SceneComponent'" + "\n"
                t += "         " + "End Object" + "\n"
            else:
                t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/Engine.Default__CameraActor:SceneComponent'" + "\n"
                t += "         " + "End Object" + "\n"

            # Init CameraComponent
            if CineCamera:
                t += "         " + "Begin Object Class=/Script/CinematicCamera.CineCameraComponent Name=\"CameraComponent\" Archetype=/Script/CinematicCamera.CineCameraComponent'/Script/CinematicCamera.Default__CineCameraActor:CameraComponent'" + "\n"
                t += "         " + "End Object" + "\n"
            else:
                t += "         " + "Begin Object Class=/Script/Engine.CameraComponent Name=\"CameraComponent\" Archetype=/Script/Engine.CameraComponent'/Script/Engine.Default__CameraActor:CameraComponent'" + "\n"
                t += "         " + "End Object" + "\n"

            # SceneComponent
            t += "         " + "Begin Object Name=\"SceneComponent\"" + "\n"
            t += "            " + "RelativeLocation=(X="+str(location_x)+",Y="+str(location_y)+",Z="+str(location_z)+")" + "\n"
            t += "            " + "RelativeRotation=(Pitch="+str(rotation_y)+",Yaw="+str(rotation_z)+",Roll="+str(rotation_x)+")" + "\n"
            t += "            " + "RelativeScale3D=(X="+str(scale_x)+",Y="+str(scale_y)+",Z="+str(scale_z)+")" + "\n"
            t += "         " + "End Object" + "\n"

            # CameraComponent
            t += "         " + "Begin Object Name=\"CameraComponent\"" + "\n"
            t += "            " + "Filmback=(SensorWidth="+str(SensorWidth)+",SensorHeight="+str(SensorHeight)+", SensorAspectRatio="+str(AspectRatio)+")" + "\n"
            t += "            " + "CurrentAperture="+str(Aperture)+")" + "\n"
            t += "            " + "CurrentFocalLength="+str(FocalLength)+")" + "\n"
            t += "            " + "CurrentFocusDistance="+str(FocusDistance)+")" + "\n"
            t += "            " + "CurrentFocusDistance="+str(FocusDistance)+")" + "\n"
            t += "            " + "CustomNearClippingPlane="+str(NearClippingPlane)+")" + "\n"
            t += "            " + "FieldOfView="+str(FieldOfView)+")" + "\n"
            t += "            " + "AspectRatio="+str(AspectRatio)+")" + "\n"
            t += "         " + "End Object" + "\n"

            # Attach
            t += "         " + "CameraComponent=\"CameraComponent\"" + "\n"
            t += "         " + "SceneComponent=\"SceneComponent\"" + "\n"
            t += "         " + "RootComponent=\"SceneComponent\"" + "\n"
            t += "         " + "ActorLabel=\""+CameraName+"\"" + "\n"

            # Close
            t += "      " + "End Actor" + "\n"
            return t
        return None

    cameras = []
    for obj in objs:
        if obj.type == "CAMERA":
            cameras.append(obj)

    if len(cameras) == 0:
        report = "Please select at least one camera."
        return (success, command, report)

    # And I apply the camrta data to the copy paste text.
    t = "Begin Map" + "\n"
    t += "   " + "Begin Level" + "\n"
    for camera in cameras:
        add_command = AddCameraToCommand(camera)
        if add_command:
            t += add_command
            add_camera_num += 1

    t += "   " + "End Level" + "\n"
    t += "Begin Surface" + "\n"
    t += "End Surface" + "\n"
    t += "End Object" + "\n"

    success = True
    command = t
    if CineCamera:
        report = str(add_camera_num)+" Cine camera(s) copied. Paste in Unreal Engine scene for import the camera. (Ctrl+V)"
    else:
        report = str(add_camera_num)+" Regular camera(s) copied. Paste in Unreal Engine scene for import the camera. (Ctrl+V)"

    return (success, command, report)


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
    fileName = scene.file_import_sequencer_script_name
    absdirpath = bpy.path.abspath(scene.export_other_file_path)
    fullpath = os.path.join(absdirpath, fileName)

    addon_prefs = GetAddonPrefs()
    return 'py "'+fullpath+'"'  # Vania


def GetAnimSample(obj):
    # return obj sample animation
    return obj.SampleAnimForExport


def GetArmatureRootBones(obj):
    rootBones = []
    if GetAssetType(obj) == "SkeletalMesh":

        if not obj.exportDeformOnly:
            for bone in obj.data.bones:
                if bone.parent is None:
                    rootBones.append(bone)

        if obj.exportDeformOnly:
            for bone in obj.data.bones:
                if bone.use_deform:
                    rootBone = getRootBoneParent(bone)
                    if rootBone not in rootBones:
                        rootBones.append(rootBone)
    return rootBones


def GetDesiredExportArmatureName(obj):
    addon_prefs = GetAddonPrefs()
    single_root = len(GetArmatureRootBones(obj)) == 1
    if addon_prefs.add_skeleton_root_bone or single_root != 1:
        return addon_prefs.skeleton_root_bone_name
    return "Armature"


def GetObjExportScale(obj):

    return obj.exportGlobalScale


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
    addon_prefs = GetAddonPrefs()

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
    ownerBone = bpy.context.active_pose_bone
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
                ConvertToConvexHull(obj)
                obj.modifiers.clear()
                obj.data
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
                    if not IsASocket(obj):
                        obj.name = GenerateUe4Name("SOCKET_"+obj.name)
                    bpy.ops.object.parent_set(
                        type='OBJECT',
                        keep_transform=True)
                    ConvertedObjs.append(obj)

            # SkeletalMesh Socket
            if obj.type == 'EMPTY' and SubType == "SK_Socket":
                if ownerObj.type == 'ARMATURE':

                    if not IsASocket(obj):
                        obj.name = GenerateUe4Name("SOCKET_"+obj.name)
                    bpy.ops.object.parent_set(type='BONE')
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
                if obj.type == 'EMPTY' and SubType == "SK_Socket":
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


def UpdateAreaLightMapList(list=None):
    # Updates area LightMap

    if list is not None:
        objs = list
    else:
        objs = []
        exportObjs = GetAllobjectsByExportType("export_recursive")
        for exportObj in exportObjs:
            if GetAssetType(exportObj) == "StaticMesh":
                objs.append(exportObj)

    UpdatedRes = 0

    counter = CounterTimer()
    for obj in objs:
        obj.computedStaticMeshLightMapRes = GetExportRealSurfaceArea(obj)
        UpdatedRes += 1
        UpdateProgress(
            "Update LightMap",
            (UpdatedRes/len(objs)),
            counter.GetTime())
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
