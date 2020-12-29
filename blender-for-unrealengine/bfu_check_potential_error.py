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
    if "bfu_ui_utils" in locals():
        importlib.reload(bfu_ui_utils)

from . import bfu_basics
from .bfu_basics import *
from .bfu_utils import *
from . import bfu_ui_utils


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

class BFU_OT_UnrealPotentialError(bpy.types.PropertyGroup):
    type: bpy.props.IntProperty(default=0)  # 0:Info, 1:Warning, 2:Error
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    ###
    selectObjectButton: bpy.props.BoolProperty(default=True)
    selectVertexButton: bpy.props.BoolProperty(default=False)
    selectPoseBoneButton: bpy.props.BoolProperty(default=False)
    ###
    selectOption: bpy.props.StringProperty(default="None")  # 0:VertexWithZeroWeight
    itemName: bpy.props.StringProperty(default="None")
    text: bpy.props.StringProperty(default="Unknown")
    correctRef: bpy.props.StringProperty(default="None")
    correctlabel: bpy.props.StringProperty(default="Fix it !")
    correctDesc: bpy.props.StringProperty(default="Correct target error")
    docsOcticon: bpy.props.StringProperty(default="None")


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
    view_layer = bpy.context.view_layer
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

def register():
    from bpy.utils import register_class

    bpy.utils.register_class(BFU_OT_UnrealPotentialError)
    bpy.types.Scene.potentialErrorList = CollectionProperty(type=BFU_OT_UnrealPotentialError)

def unregister():
    from bpy.utils import unregister_class

    bpy.utils.unregister_class(BFU_OT_UnrealPotentialError)
    del bpy.types.Scene.potentialErrorList