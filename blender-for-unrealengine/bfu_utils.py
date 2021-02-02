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

if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
from . import bfu_basics
from .bfu_basics import *


class SavedObject():

    def __init__(self, obj):
        if obj:
            self.name = obj.name
            self.select = obj.select_get()
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


class UserSceneSave():

    def __init__(self):

        # Select
        self.user_active = None
        self.user_active_name = None
        self.user_bone_active = None
        self.user_bone_active_name = None
        self.user_selected = []

        # Stats
        self.user_mode = None
        self.use_simplify = False

        # Data
        self.objects = []
        self.object_bones = []
        self.collections = []
        self.view_layers_children = []
        self.action_names = []
        self.collection_names = []

    def SaveCurrentScene(self):
        # Save data (This can take time)

        c = bpy.context
        # Select
        self.user_active = c.active_object  # Save current active object
        if self.user_active:
            self.user_active_name = self.user_active.name
        self.user_selected = c.selected_objects  # Save current selected objects

        # Stats
        if self.user_active:
            if bpy.ops.object.mode_set.poll():
                self.user_mode = self.user_active.mode  # Save current mode
        self.use_simplify = bpy.context.scene.render.use_simplify

        # Data
        for obj in bpy.data.objects:
            self.objects.append(SavedObject(obj))
        for col in bpy.data.collections:
            self.collections.append(SavedCollection(col))
        for vlayer in c.scene.view_layers:
            for childCol in vlayer.layer_collection.children:
                self.view_layers_children.append(SavedViewLayerChildren(vlayer, childCol))
        for action in bpy.data.actions:
            self.action_names.append(action.name)
        for collection in bpy.data.collections:
            self.collection_names.append(collection.name)

        # Data for armature
        if self.user_active:
            if self.user_active.type == "ARMATURE":
                if self.user_active.data.bones.active:
                    self.user_bone_active = self.user_active.data.bones.active
                    self.user_bone_active_name = self.user_active.data.bones.active.name
                for bone in self.user_active.data.bones:
                    self.object_bones.append(SavedBones(bone))

    def ResetSelectByRef(self):
        SafeModeSet(bpy.ops.object, "OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:  # Resets previous selected object if still exist
            if obj in self.user_selected:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = self.user_active

        self.ResetModeAtSave()
        self.ResetBonesSelectByName()

    def ResetSelectByName(self):
        SafeModeSet(bpy.ops.object, "OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.objects:  # Resets previous selected object if still exist
            if obj.select:
                if obj.name in bpy.data.objects:
                    bpy.data.objects[obj.name].select_set(True)

        if self.user_active_name:
            if self.user_active_name in bpy.data.objects:
                bpy.context.view_layer.objects.active = bpy.data.objects[self.user_active_name]

        self.ResetModeAtSave()
        self.ResetBonesSelectByName()

    def ResetBonesSelectByName(self):
        # Work only in pose mode!
        if len(self.object_bones) > 0:
            if self.user_active:
                if bpy.ops.object.mode_set.poll():
                    if self.user_active.mode == "POSE":
                        bpy.ops.pose.select_all(action='DESELECT')
                        for bone in self.object_bones:
                            if bone.select:
                                if bone.name in self.user_active.data.bones:
                                    self.user_active.data.bones[bone.name].select = True

                        if self.user_bone_active_name is not None:
                            if self.user_bone_active_name in self.user_active.data.bones:
                                new_active = self.user_active.data.bones[self.user_bone_active_name]
                                self.user_active.data.bones.active = new_active

    def ResetModeAtSave(self):
        if self.user_mode:
            if bpy.ops.object:
                SafeModeSet(bpy.ops.object, self.user_mode)

    def ResetSceneAtSave(self):
        scene = bpy.context.scene
        self.ResetModeAtSave()

        bpy.context.scene.render.use_simplify = self.use_simplify

        # Reset hide and select (bpy.data.objects)
        for obj in self.objects:
            if obj.name in bpy.data.objects:
                if bpy.data.objects[obj.name].hide_select != obj.hide_select:
                    bpy.data.objects[obj.name].hide_select = obj.hide_select
                if bpy.data.objects[obj.name].hide_viewport != obj.hide_viewport:
                    bpy.data.objects[obj.name].hide_viewport = obj.hide_viewport
            else:
                print("/!\\ "+obj.name+" not found in bpy.data.objects")

        # Reset hide and select (bpy.data.collections)
        for col in self.collections:
            if col.name in bpy.data.collections:
                if bpy.data.collections[col.name].hide_select != col.hide_select:
                    bpy.data.collections[col.name].hide_select = col.hide_select
                if bpy.data.collections[col.name].hide_viewport != col.hide_viewport:
                    bpy.data.collections[col.name].hide_viewport = col.hide_viewport
            else:
                print("/!\\ "+col.name+" not found in bpy.data.collections")

        # Reset hide in and viewport (collections from view_layers)
        for childCol in self.view_layers_children:
            if childCol.vlayer_name in scene.view_layers:
                view_layer = scene.view_layers[childCol.vlayer_name]
                if childCol.name in view_layer.layer_collection.children:
                    layer_col_children = view_layer.layer_collection.children[childCol.name]

                    if layer_col_children.exclude != childCol.exclude:
                        layer_col_children.exclude = childCol.exclude
                    if layer_col_children.hide_viewport != childCol.hide_viewport:
                        layer_col_children.hide_viewport = childCol.hide_viewport


def SafeModeSet(obj, target_mode='OBJECT'):
    if obj:
        if obj.mode != target_mode:
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode=target_mode)
    return False


class CounterTimer():
    
    def __init__(self):
        self.start = time.perf_counter()

    def ResetTime(self):
        self.start = time.perf_counter()

    def GetTime(self):
        return time.perf_counter()-self.start


def update_progress(job_title, progress, time=None):

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
    sys.stdout.write(msg)
    sys.stdout.flush()


def RemoveUselessSpecificData(name, type):
    if type == "MESH":
        oldData = bpy.data.meshes[name]
        if oldData.users == 0:
            bpy.data.meshes.remove(oldData)

    if type == "ARMATURE":
        oldData = bpy.data.armatures[name]
        if oldData.users == 0:
            bpy.data.armatures.remove(oldData)


def CleanJoinSelect():
    view_layer = bpy.context.view_layer
    if len(bpy.context.selected_objects) < 1:
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
    socket = [obj for obj in GetExportDesiredChilds(targetObj) if (
        fnmatch.fnmatchcase(obj.name, "SOCKET*"))]
    return socket


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
            colExport.append(col.name)
    return colExport


class CachedAction():

    '''
    I can't use bpy.types.Scene or bpy.types.Object Property.
    "Writing to ID classes in this context is not allowed"
    So I use simple python var
    '''

    def __init__(self):
        self.name = ""
        self.is_cached = False
        self.stored_actions = []
        self.total_action_len = 0
        self.total_bone_len = 0

    def CheckCache(self, obj):
        # Check if the cache need update
        if self.name != obj.name:
            MyCachedActions.is_cached = False
        if len(bpy.data.actions) != self.total_action_len:
            MyCachedActions.is_cached = False
        if len(obj.data.bones) != self.total_bone_len:
            MyCachedActions.is_cached = False

        return MyCachedActions.is_cached

    def StoreActions(self, obj, actions):
        # Update new cache
        self.is_cached = True
        self.name = obj.name
        action_name_list = []
        for action in actions:
            action_name_list.append(action.name)
        self.stored_actions = action_name_list
        self.total_action_len = len(bpy.data.actions)
        self.total_bone_len = len(obj.data.bones)

    def GetStoredActions(self):
        actions = []
        for action_name in self.stored_actions:
            if action_name in bpy.data.actions:
                actions.append(bpy.data.actions[action_name])
        return actions

    def Clear(self):
        pass


MyCachedActions = CachedAction()


def GetCachedExportAutoActionList(obj):
    # This will cheak if the action contains
    # the same bones of the armature

    actions = []

    # Use the cache
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
        print("Up")
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


def ExportCompuntedLightMapValue(obj):
    if obj.StaticMeshLightMapEnum == "Default":
        return False
    return True


def GetExportRealSurfaceArea(obj):
    scene = bpy.context.scene

    MoveToGlobalView()
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

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

    obj.select_set(True)
    if obj.ExportAsProxy:
        if obj.ExportProxyChild is not None:
            obj.ExportProxyChild.select_set(True)

    selectedObjs.append(obj)
    bpy.context.view_layer.objects.active = obj
    return selectedObjs


def GoToMeshEditMode():
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
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
                        bpy.ops.object.modifier_apply(modifier=mod.name)

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


def ApplyExportTransform(obj):
    newMatrix = obj.matrix_world @ mathutils.Matrix.Translation((0, 0, 0))
    saveScale = obj.scale * 1

    # Ref
    # Moves object to the center of the scene for export
    if obj.MoveToCenterForExport:
        mat_trans = mathutils.Matrix.Translation((0, 0, 0))
        mat_rot = newMatrix.to_quaternion().to_matrix()
        newMatrix = mat_trans @ mat_rot.to_4x4()

    # Turn object to the center of the scene for export
    if obj.RotateToZeroForExport:
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


def ApplySkeletalExportScale(obj, rescale):
    # That a correct name ?
    obj.scale = obj.scale*rescale
    bpy.ops.object.transform_apply(
        location=True,
        scale=True,
        rotation=True,
        properties=True
        )


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


def RescaleAllActionCurve(scale):
    for action in bpy.data.actions:
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
    TargetAssetToExport = []  # Obj, Action, type

    class AssetToExport:
        def __init__(self, obj, action, type):
            self.obj = obj
            self.action = action
            self.type = type

    if scene.export_ExportOnlySelected:
        objList = []
        collectionList = []
        recuList = GetAllobjectsByExportType("export_recursive")

        for obj in bpy.context.selected_objects:
            if obj in recuList:
                if obj not in objList:
                    objList.append(obj)
            parentTarget = getHaveParentToExport(obj)
            if parentTarget is not None:
                if parentTarget not in objList:
                    objList.append(parentTarget)

    else:
        objList = GetAllobjectsByExportType("export_recursive")
        collectionList = GetCollectionToExport(scene)

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
                # Action
                if scene.anin_export:
                    if GetActionType(action) == "Action":
                        TargetAssetToExport.append(AssetToExport(
                            obj,
                            action,
                            "Action"))

                # Pose
                if scene.anin_export:
                    if GetActionType(action) == "Pose":
                        TargetAssetToExport.append(AssetToExport(
                            obj,
                            action,
                            "Pose"))
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


def ValidUnrealAssetename(filename):
    # Normalizes string, removes non-alpha characters
    # Asset name in Unreal use

    filename = filename.replace('.', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    filename = filename.replace(' ', '_')
    valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename


def GetCollectionExportDir(abspath=False):
    # Generate assset folder path
    scene = bpy.context.scene

    if abspath:
        return bpy.path.abspath(dirpath)
    else:
        return os.path.join(scene.export_static_file_path, "")


def GetObjExportName(obj):
    # Return Proxy Name for Proxy and Object Name for other
    if GetAssetType(obj) == "SkeletalMesh":
        if obj.ExportAsProxy:
            if obj.ExportProxyChild is not None:
                return obj.ExportProxyChild.name
    return ValidFilename(obj.name)


def GetObjExportDir(obj, abspath=False):
    # Generate assset folder path
    scene = bpy.context.scene
    if GetAssetType(obj) == "SkeletalMesh":
        dirpath = os.path.join(
            scene.export_skeletal_file_path,
            obj.exportFolderName,
            GetObjExportName(obj))
    if GetAssetType(obj) == "Alembic":
        dirpath = os.path.join(
            scene.export_alembic_file_path,
            obj.exportFolderName,
            obj.name)
    if GetAssetType(obj) == "StaticMesh":
        dirpath = os.path.join(
            scene.export_static_file_path,
            obj.exportFolderName)
    if GetAssetType(obj) == "Camera":
        dirpath = os.path.join(
            scene.export_camera_file_path,
            obj.exportFolderName)
    if abspath:
        return bpy.path.abspath(dirpath)
    else:
        return dirpath


def GetCollectionExportFileName(collection, fileType=".fbx"):
    # Generate assset file name

    scene = bpy.context.scene
    return scene.static_prefix_export_name+collection+fileType


def GetObjExportFileName(obj, fileType=".fbx"):
    # Generate assset file name

    scene = bpy.context.scene
    if obj.bfu_use_custom_export_name:
        return ValidFilename(obj.bfu_custom_export_name+fileType)
    assetType = GetAssetType(obj)
    if assetType == "Camera":
        return ValidFilename(scene.camera_prefix_export_name+obj.name+fileType)
    elif assetType == "StaticMesh":
        return ValidFilename(scene.static_prefix_export_name+obj.name+fileType)
    elif assetType == "SkeletalMesh":
        return ValidFilename(scene.skeletal_prefix_export_name+obj.name+fileType)
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
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    return 'py "'+fullpath+'"'


def GetImportSequencerScriptCommand():
    scene = bpy.context.scene
    fileName = scene.file_import_sequencer_script_name
    absdirpath = bpy.path.abspath(scene.export_other_file_path)
    fullpath = os.path.join(absdirpath, fileName)

    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    return 'py "'+fullpath+'"'  # Vania


def GetAnimSample(obj):
    # return obj sample animation
    # return 1000 #Debug
    return obj.SampleAnimForExport


def GetDesiredExportArmatureName():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    if addon_prefs.removeSkeletonRootBone:
        return "Armature"
    return addon_prefs.skeletonRootBoneName


def GetObjExportScale(obj):

    return obj.exportGlobalScale


def RenameArmatureAsExportName(obj):
    # Rename temporarily the Armature as DefaultArmature

    scene = bpy.context.scene
    oldArmatureName = None
    newArmatureName = GetDesiredExportArmatureName()
    if obj.name != newArmatureName:
        oldArmatureName = obj.name
        # Avoid same name for two armature
        if newArmatureName in scene.objects:
            newArmature = scene.objects[newArmatureName]
            newArmature.name = "ArmatureTemporarilyNameForUe4Export"
        obj.name = newArmatureName
    return oldArmatureName


def ResetArmatureName(obj, oldArmatureName):
    # Reset armature name

    scene = bpy.context.scene
    if oldArmatureName is not None:
        obj.name = oldArmatureName
        if "ArmatureTemporarilyNameForUe4Export" in scene.objects:
            armature = scene.objects["ArmatureTemporarilyNameForUe4Export"]
            armature.name = GetDesiredExportArmatureName()


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
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

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
                    if not obj.name.startswith("SOCKET_"):
                        obj.name = GenerateUe4Name("SOCKET_"+obj.name)
                    bpy.ops.object.parent_set(
                        type='OBJECT',
                        keep_transform=True)
                    ConvertedObjs.append(obj)

            # SkeletalMesh Socket
            if obj.type == 'EMPTY' and SubType == "SK_Socket":
                if ownerObj.type == 'ARMATURE':
                    if not obj.name.startswith("SOCKET_"):
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
                        if not obj.name.startswith("SOCKET_"):
                            obj.name = GenerateUe4Name("SOCKET_"+obj.name)

                # SkeletalMesh Socket
                if obj.type == 'EMPTY' and SubType == "SK_Socket":
                    if ownerObj.type == 'ARMATURE':
                        if not obj.name.startswith("SOCKET_"):
                            obj.name = GenerateUe4Name("SOCKET_"+obj.name)


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
        update_progress(
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
