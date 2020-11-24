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


def CounterStart():
    return time.perf_counter()


def CounterEnd(start):
    return time.perf_counter()-start


def update_progress(job_title, progress, time=None):

    length = 20  # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(
        job_title,
        "#"*block + "-"*(length-block),
        round(progress*100, 2))
    if progress >= 1:
        if time is not None	:
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
        # This will cheak if the action contains
        # the same bones of the armature
        objBoneNames = [bone.name for bone in obj.data.bones]
        for action in bpy.data.actions:
            if action.library is None:
                if GetIfActionIsAssociated(action, objBoneNames):
                    TargetActionToExport.append(action)
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
            objScale = (obj.scale.x + obj.scale.y + obj.scale.z)/3
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


def GetCollectionExportDir(abspath=False):
    # Generate assset folder path
    scene = bpy.context.scene

    if abspath:
        return bpy.path.abspath(dirpath)
    else:
        return os.path.join(scene.export_static_file_path, "")


def GetObjExportDir(obj, abspath=False):
    # Generate assset folder path
    scene = bpy.context.scene
    if GetAssetType(obj) == "SkeletalMesh":
        dirpath = os.path.join(
            scene.export_skeletal_file_path,
            obj.exportFolderName,
            obj.name)
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
        return obj.bfu_custom_export_name+fileType
    assetType = GetAssetType(obj)
    if assetType == "Camera":
        return scene.camera_prefix_export_name+obj.name+fileType
    elif assetType == "StaticMesh":
        return scene.static_prefix_export_name+obj.name+fileType
    elif assetType == "SkeletalMesh":
        return scene.skeletal_prefix_export_name+obj.name+fileType
    elif assetType == "Alembic":
        return scene.alembic_prefix_export_name+obj.name+fileType
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
        return scene.anim_prefix_export_name+ArmatureName+action.name+fileType
    elif animType == "Pose":
        return scene.pose_prefix_export_name+ArmatureName+action.name+fileType
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

    return scene.anim_prefix_export_name+ArmatureName+obj.NLAAnimName+fileType


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


def UpdateNameHierarchy(list=None):
    # Updates hierarchy names

    if list is not None:
        objs = list
    else:
        objs = GetAllCollisionAndSocketsObj()

    UpdatedHierarchy = 0
    for obj in objs:
        if fnmatch.fnmatchcase(obj.name, "UBX*"):
            UpdateUe4Name("Box", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "UCP*"):
            UpdateUe4Name("Capsule", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "USP*"):
            UpdateUe4Name("Sphere", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "UCX*"):
            UpdateUe4Name("Convex", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            UpdateUe4Name("Socket", [obj])
            UpdatedHierarchy += 1
        return UpdatedHierarchy


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

    s = CounterStart()
    for obj in objs:
        obj.computedStaticMeshLightMapRes = GetExportRealSurfaceArea(obj)
        UpdatedRes += 1
        update_progress(
            "Update LightMap",
            (UpdatedRes/len(objs)),
            CounterEnd(s))
    return UpdatedRes


def CorrectBadProperty(list=None):
    # Corrects bad properties

    if list is not None:
        objs = list
    else:
        objs = GetAllCollisionAndSocketsObj()

    UpdatedProp = 0
    for obj in objs:
        if obj.ExportEnum == "export_recursive":
            obj.ExportEnum = "auto"
            UpdatedProp += 1
    return UpdatedProp


def GetVertexWithZeroWeight(Armature, Mesh):
    vertices = []
    for vertex in Mesh.data.vertices:
        cumulateWeight = 0
        if len(vertex.groups) > 0:
            for GroupElem in vertex.groups:
                if (Mesh.vertex_groups[GroupElem.group].name in
                        Armature.data.bones):
                    cumulateWeight += GroupElem.weight
        if cumulateWeight == 0:
            vertices.append(vertex)
    return vertices


def UpdateUnrealPotentialError():
    # Find and reset list of all potential error in scene

    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    PotentialErrors = bpy.context.scene.potentialErrorList
    PotentialErrors.clear()

    # prepares the data to avoid unnecessary loops
    objToCheck = []
    for Asset in GetFinalAssetToExport():
        if Asset.obj in GetAllobjectsByExportType("export_recursive"):
            if Asset.obj not in objToCheck:
                objToCheck.append(Asset.obj)
            for child in GetExportDesiredChilds(Asset.obj):
                if child not in objToCheck:
                    objToCheck.append(child)

    MeshTypeToCheck = []
    for obj in objToCheck:
        if obj.type == 'MESH':
            MeshTypeToCheck.append(obj)

    MeshTypeWithoutCol = []  # is Mesh Type To Check Without Collision
    for obj in MeshTypeToCheck:
        if not CheckIsCollision(obj):
            MeshTypeWithoutCol.append(obj)

    def CheckUnitScale():
        # Check if the unit scale is equal to 0.01.
        if addon_prefs.notifyUnitScalePotentialError:
            if not math.isclose(
                    bpy.context.scene.unit_settings.scale_length,
                    0.01,
                    rel_tol=1e-5):
                MyError = PotentialErrors.add()
                MyError.name = bpy.context.scene.name
                MyError.type = 1
                MyError.text = (
                    'Scene "'+bpy.context.scene.name +
                    '" has a UnitScale egal to ' +
                    str(bpy.context.scene.unit_settings.scale_length))
                MyError.text += (
                    '\nFor Unreal unit scale equal to 0.01 is recommended.')
                MyError.text += (
                    '\n(You can disable this potential error in addon_prefs)')
                MyError.object = None
                MyError.correctRef = "SetUnrealUnit"
                MyError.correctlabel = 'Set Unreal Unit'

    def CheckObjType():
        # Check if objects use a non-recommended type
        for obj in objToCheck:
            if (obj.type == "SURFACE" or
                    obj.type == "META" or
                    obj.type == "FONT"):
                MyError = PotentialErrors.add()
                MyError.name = obj.name
                MyError.type = 1
                MyError.text = (
                    'Object "'+obj.name +
                    '" is a '+obj.type +
                    '. The object of the type SURFACE,' +
                    ' META and FONT is not recommended.')
                MyError.object = obj
                MyError.correctRef = "ConvertToMesh"
                MyError.correctlabel = 'Convert to mesh'

    def CheckShapeKeys():
        for obj in MeshTypeToCheck:
            if obj.data.shape_keys is not None:
                # Check that no modifiers is destructive for the key shapes
                if len(obj.data.shape_keys.key_blocks) > 0:
                    for modif in obj.modifiers:
                        if modif.type != "ARMATURE":
                            MyError = PotentialErrors.add()
                            MyError.name = obj.name
                            MyError.type = 2
                            MyError.object = obj
                            MyError.itemName = modif.name
                            MyError.text = (
                                'In object "'+obj.name +
                                '" the modifier '+modif.type +
                                ' named "'+modif.name +
                                '" can destroy shape keys.' +
                                ' Please use only Armature modifier' +
                                ' with shape keys.')
                            MyError.correctRef = "RemoveModfier"
                            MyError.correctlabel = 'Remove modifier'

                # Check that the key shapes are not out of bounds for Unreal
                for key in obj.data.shape_keys.key_blocks:
                    # Min
                    if key.slider_min < -5:
                        MyError = PotentialErrors.add()
                        MyError.name = obj.name
                        MyError.type = 1
                        MyError.object = obj
                        MyError.itemName = key.name
                        MyError.text = (
                            'In object "'+obj.name +
                            '" the shape key "'+key.name +
                            '" is out of bounds for Unreal.' +
                            ' The min range of must not be inferior to -5.')
                        MyError.correctRef = "SetKeyRangeMin"
                        MyError.correctlabel = 'Set min range to -5'

                    # Max
                    if key.slider_max > 5:
                        MyError = PotentialErrors.add()
                        MyError.name = obj.name
                        MyError.type = 1
                        MyError.object = obj
                        MyError.itemName = key.name
                        MyError.text = (
                            'In object "'+obj.name +
                            '" the shape key "'+key.name +
                            '" is out of bounds for Unreal.' +
                            ' The max range of must not be superior to 5.')
                        MyError.correctRef = "SetKeyRangeMax"
                        MyError.correctlabel = 'Set max range to -5'

    def CheckUVMaps():
        # Check that the objects have at least one UV map valid
        for obj in MeshTypeWithoutCol:
            if len(obj.data.uv_layers) < 1:
                MyError = PotentialErrors.add()
                MyError.name = obj.name
                MyError.type = 1
                MyError.text = (
                    'Object "'+obj.name +
                    '" does not have any UV Layer.')
                MyError.object = obj
                MyError.correctRef = "CreateUV"
                MyError.correctlabel = 'Create Smart UV Project'

    def CheckBadStaicMeshExportedLikeSkeletalMesh():
        # Check if the correct object is defined as exportable
        for obj in MeshTypeToCheck:
            for modif in obj.modifiers:
                if modif.type == "ARMATURE":
                    if obj.ExportEnum == "export_recursive":
                        MyError = PotentialErrors.add()
                        MyError.name = obj.name
                        MyError.type = 1
                        MyError.text = (
                            'In object "'+obj.name +
                            '" the modifier '+modif.type +
                            ' named "'+modif.name +
                            '" will not be applied when exported' +
                            ' with StaticMesh assets.\nNote: with armature' +
                            ' if you want export objets as skeletal mesh you' +
                            ' need set only the armature as' +
                            ' export_recursive not the childs')
                        MyError.object = obj

    def CheckArmatureScale():
        # Check if the ARMATURE use the same value on all scale axes
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                if obj.scale.z != obj.scale.y or obj.scale.z != obj.scale.x:
                    MyError = PotentialErrors.add()
                    MyError.name = obj.name
                    MyError.type = 2
                    MyError.text = (
                        'In object "'+obj.name +
                        '" do not use the same value on all scale axes ')
                    MyError.text += (
                        '\nScale x:' +
                        str(obj.scale.x)+' y:'+str(obj.scale.y) +
                        ' z:'+str(obj.scale.z))
                    MyError.object = obj

    def CheckArmatureModNumber():
        # check that there is no more than
        # one Modifier ARMATURE at the same time
        for obj in MeshTypeToCheck:
            ArmatureModifiers = 0
            for modif in obj.modifiers:
                if modif.type == "ARMATURE":
                    ArmatureModifiers = ArmatureModifiers + 1
            if ArmatureModifiers > 1:
                MyError = PotentialErrors.add()
                MyError.name = obj.name
                MyError.type = 2
                MyError.text = (
                    'In object "'+obj.name +
                    '" there are several Armature modifiers' +
                    ' at the same time.' +
                    ' Please use only one Armature modifier.')
                MyError.object = obj

    def CheckArmatureModData():
        # check the parameter of Modifier ARMATURE
        for obj in MeshTypeToCheck:
            for modif in obj.modifiers:
                if modif.type == "ARMATURE":
                    if modif.use_deform_preserve_volume:
                        MyError = PotentialErrors.add()
                        MyError.name = obj.name
                        MyError.type = 2
                        MyError.text = (
                            'In object "'+obj.name +
                            '" the modifier '+modif.type +
                            ' named "'+modif.name +
                            '". The parameter Preserve Volume' +
                            ' must be set to False.')
                        MyError.object = obj
                        MyError.itemName = modif.name
                        MyError.correctRef = "PreserveVolume"
                        MyError.correctlabel = 'Set Preserve Volume to False'

    def CheckArmatureBoneData():
        # check the parameter of the ARMATURE bones
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                for bone in obj.data.bones:
                    if (not obj.exportDeformOnly or
                            (bone.use_deform and obj.exportDeformOnly)):

                        if bone.bbone_segments > 1:
                            MyError = PotentialErrors.add()
                            MyError.name = obj.name
                            MyError.type = 1
                            MyError.text = (
                                'In object3 "'+obj.name +
                                '" the bone named "'+bone.name +
                                '". The parameter Bendy Bones / Segments' +
                                ' must be set to 1.')
                            MyError.text += (
                                '\nBendy bones are not supported by' +
                                ' Unreal Engine, so that better to disable' +
                                ' it if you want the same animation preview' +
                                ' in Unreal and blender.')
                            MyError.object = obj
                            MyError.itemName = bone.name
                            MyError.selectPoseBoneButton = True
                            MyError.correctRef = "BoneSegments"
                            MyError.correctlabel = 'Set Bone Segments to 1'
                            MyError.docsOcticon = 'bendy-bone'

    def CheckArmatureValidChild():
        # Check that skeleton also has a mesh to export
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                childs = GetExportDesiredChilds(obj)
                validChild = 0
                for child in childs:
                    if child.type == "MESH":
                        validChild += 1
                if obj.ExportAsProxy:
                    if obj.ExportProxyChild is not None:
                        validChild += 1
                if validChild < 1:
                    MyError = PotentialErrors.add()
                    MyError.name = obj.name
                    MyError.type = 2
                    MyError.text = (
                        'Object "'+obj.name +
                        '" is an Armature and does not have' +
                        ' any valid children.')
                    MyError.object = obj

    def CheckArmatureMultipleRoots():
        # Check that skeleton have multiples roots
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":

                rootBones = []
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

                if len(rootBones) > 1:
                    MyError = PotentialErrors.add()
                    MyError.name = obj.name
                    MyError.type = 2
                    MyError.text = (
                        'Object "'+obj.name +
                        '" have Multiple roots bones.' +
                        ' Unreal only support single root bone.')
                    MyError.text += '\nRoot bones: '
                    for rootBone in rootBones:
                        MyError.text += rootBone.name+' '
                    MyError.object = obj

    def CheckArmatureNoDeformBone():
        # Check that skeleton have at less one deform bone
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                if obj.exportDeformOnly:
                    for bone in obj.data.bones:
                        if bone.use_deform:
                            return
                    MyError = PotentialErrors.add()
                    MyError.name = obj.name
                    MyError.type = 2
                    MyError.text = (
                        'Object "'+obj.name +
                        '" don\'t have any deform bones.' +
                        ' Unreal will import it like a StaticMesh.')
                    MyError.object = obj

    def CheckMarkerOverlay():
        # Check that there is no overlap with the Marker
        usedFrame = []
        for marker in bpy.context.scene.timeline_markers:
            if marker.frame in usedFrame:
                MyError = PotentialErrors.add()
                MyError.type = 2
                MyError.text = (
                    'In the scene timeline the frame "' +
                    str(marker.frame)+'" contains overlaped Markers' +
                    '\n To avoid camera conflict in the generation' +
                    ' of sequencer you must use max one marker per frame.')
            else:
                usedFrame.append(marker.frame)

    def CheckVertexGroupWeight():
        # Check that all vertex have a weight
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                childs = GetExportDesiredChilds(obj)
                for child in childs:
                    if child.type == "MESH":
                        # Result data
                        VertexWithZeroWeight = GetVertexWithZeroWeight(
                            obj,
                            child)
                        if len(VertexWithZeroWeight) > 0:
                            MyError = PotentialErrors.add()
                            MyError.name = child.name
                            MyError.type = 1
                            MyError.text = (
                                'Object named "'+child.name +
                                '" contains '+str(len(VertexWithZeroWeight)) +
                                ' vertex with zero cumulative valid weight.')
                            MyError.text += (
                                '\nNote: Vertex groups must have' +
                                ' a bone with the same name to be valid.')
                            MyError.object = child
                            MyError.selectVertexButton = True
                            MyError.selectOption = "VertexWithZeroWeight"

    def CheckZeroScaleKeyframe():
        # Check that animations do not use a invalid value
        for obj in objToCheck:
            if GetAssetType(obj) == "SkeletalMesh":
                for action in GetActionToExport(obj):
                    for fcurve in action.fcurves:
                        if fcurve.data_path.split(".")[-1] == "scale":
                            for key in fcurve.keyframe_points:
                                xCurve, yCurve = key.co
                                if key.co[1] == 0:
                                    MyError = PotentialErrors.add()
                                    MyError.type = 2
                                    MyError.text = (
                                        'In action "'+action.name +
                                        '" at frame '+str(key.co[0]) +
                                        ', the bone named "' +
                                        fcurve.data_path.split('"')[1] +
                                        '" has a zero value in scale' +
                                        ' transform. ' +
                                        'This is invalid in Unreal.')

    CheckUnitScale()
    CheckObjType()
    CheckShapeKeys()
    CheckUVMaps()
    CheckBadStaicMeshExportedLikeSkeletalMesh()
    CheckArmatureScale()
    CheckArmatureModNumber()
    CheckArmatureModData()
    CheckArmatureBoneData()
    CheckArmatureValidChild()
    CheckArmatureMultipleRoots()
    CheckArmatureNoDeformBone()
    CheckMarkerOverlay()
    CheckVertexGroupWeight()
    CheckZeroScaleKeyframe()

    return PotentialErrors


def SelectPotentialErrorObject(errorIndex):
    # Select potential error

    if (bpy.context.active_object and
            bpy.context.active_object.mode != 'OBJECT' and
            bpy.ops.object.mode_set.poll()):
        bpy.ops.object.mode_set(mode="OBJECT")
    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object

    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_viewport = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # show collection for select object
    for collection in bpy.data.collections:
        for ColObj in collection.objects:
            if ColObj == obj:
                SetCollectionUse(collection)
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorVertex(errorIndex):
    # Select potential error
    SelectPotentialErrorObject(errorIndex)
    bpy.ops.object.mode_set(mode="EDIT")

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode='OBJECT')
    if error.selectOption == "VertexWithZeroWeight":
        for vertex in GetVertexWithZeroWeight(obj.parent, obj):
            vertex.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorPoseBone(errorIndex):
    # Select potential error
    SelectPotentialErrorObject(errorIndex)
    bpy.ops.object.mode_set(mode="POSE")

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object
    bone = obj.data.bones[error.itemName]

    # Make bone visible if hide in a layer
    for x, layer in enumerate(bone.layers):
        if not obj.data.layers[x] and layer:
            obj.data.layers[x] = True

    bpy.ops.pose.select_all(action='DESELECT')
    obj.data.bones.active = bone
    bone.select = True

    bpy.ops.view3d.view_selected()
    return obj


def TryToCorrectPotentialError(errorIndex):
    # Try to correct potential error

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    global successCorrect
    successCorrect = False
    # ----------------------------------------Save data
    UserActive = bpy.context.active_object  # Save current active object
    UserMode = None
    if (UserActive and
            UserActive.mode != 'OBJECT' and
            bpy.ops.object.mode_set.poll()):
        UserMode = UserActive.mode  # Save current mode
        bpy.ops.object.mode_set(mode='OBJECT')
    # Save current selected objects
    UserSelected = bpy.context.selected_objects
    UsedViewLayerCollectionHideViewport = []
    UsedCollectionHideViewport = []
    UsedCollectionHideselect = []
    for collection in bpy.data.collections:
        # Save previous collections visibility
        layer_collection = view_layer.layer_collection
        if collection.name in layer_collection.children:
            layer_children = layer_collection.children[collection.name]
            UsedViewLayerCollectionHideViewport.append(
                layer_children.hide_viewport)
        else:
            print(collection.name, " not found in layer_collection")
            pass
        UsedCollectionHideViewport.append(collection.hide_viewport)
        UsedCollectionHideselect.append(collection.hide_select)
        SetCollectionUse(collection)

    # ----------------------------------------
    print("Start correct")

    def SelectObj(obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    # Correction list

    if error.correctRef == "SetUnrealUnit":
        bpy.context.scene.unit_settings.scale_length = 0.01
        successCorrect = True

    if error.correctRef == "ConvertToMesh":
        obj = error.object
        SelectObj(obj)
        bpy.ops.object.convert(target='MESH')
        successCorrect = True

    if error.correctRef == "SetKeyRangeMin":
        obj = error.object
        key = obj.data.shape_keys.key_blocks[error.itemName]
        key.slider_min = -5
        successCorrect = True

    if error.correctRef == "SetKeyRangeMax":
        obj = error.object
        key = obj.data.shape_keys.key_blocks[error.itemName]
        key.slider_max = 5
        successCorrect = True

    if error.correctRef == "CreateUV":
        obj = error.object
        SelectObj(obj)
        bpy.ops.uv.smart_project()
        successCorrect = True

    if error.correctRef == "RemoveModfier":
        obj = error.object
        mod = obj.modifiers[error.itemName]
        obj.modifiers.remove(mod)
        successCorrect = True

    if error.correctRef == "PreserveVolume":
        obj = error.object
        mod = obj.modifiers[error.itemName]
        mod.use_deform_preserve_volume = False
        successCorrect = True

    if error.correctRef == "BoneSegments":
        obj = error.object
        bone = obj.data.bones[error.itemName]
        bone.bbone_segments = 1
        successCorrect = True

    if error.correctRef == "InheritScale":
        obj = error.object
        bone = obj.data.bones[error.itemName]
        bone.use_inherit_scale = True
        successCorrect = True

    # ----------------------------------------Reset data
    for x, collection in enumerate(bpy.data.collections):
        layer_collection = view_layer.layer_collection
        if collection.name in layer_collection.children:
            layer_child = layer_collection.children[collection.name]
            layer_child.hide_viewport = UsedViewLayerCollectionHideViewport[x]
        else:
            print(collection.name, " not found in layer_collection")

        collection.hide_viewport = UsedCollectionHideViewport[x]
        collection.hide_select = UsedCollectionHideselect[x]

    bpy.ops.object.select_all(action='DESELECT')
    for obj in UserSelected:  # Resets previous selected object if still exist
        if obj.name in scene.objects:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = UserActive
    # Resets previous active object
    if UserActive and UserMode and bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=UserMode)  # Resets previous mode
    # ----------------------------------------

    if successCorrect:
        scene.potentialErrorList.remove(errorIndex)
        print("end correct, Error: " + error.correctRef)
        return "Corrected"
    print("end correct, Error not found")
    return "Correct fail"


def AddFrontEachLine(ImportScript, text="\t"):

    NewImportScript = ""
    text_splited = ImportScript.split('\n')
    for line in text_splited:
        NewImportScript += text + line + "\n"

    return NewImportScript
