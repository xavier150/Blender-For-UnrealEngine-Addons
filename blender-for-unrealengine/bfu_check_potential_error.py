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
import math

from . import bbpl
from . import bfu_basics
from . import bfu_utils
from . import bfu_cached_asset_list


def CorrectBadProperty(list=None):
    # Corrects bad properties

    if list is not None:
        objs = list
    else:
        objs = bfu_utils.GetAllCollisionAndSocketsObj()

    UpdatedProp = 0
    for obj in objs:
        if obj.bfu_export_type == "export_recursive":
            obj.bfu_export_type = "auto"
            UpdatedProp += 1
    return UpdatedProp


def UpdateNameHierarchy(list=None):
    # Updates hierarchy names

    if list is not None:
        objs = list
    else:
        objs = bfu_utils.GetAllCollisionAndSocketsObj()

    UpdatedHierarchy = 0
    for obj in objs:
        if fnmatch.fnmatchcase(obj.name, "UBX*"):
            bfu_utils.UpdateUe4Name("Box", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "UCP*"):
            bfu_utils.UpdateUe4Name("Capsule", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "USP*"):
            bfu_utils.UpdateUe4Name("Sphere", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "UCX*"):
            bfu_utils.UpdateUe4Name("Convex", [obj])
            UpdatedHierarchy += 1
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            bfu_utils.UpdateUe4Name("Socket", [obj])
            UpdatedHierarchy += 1
        return UpdatedHierarchy


def GetVertexWithZeroWeight(Armature, Mesh):
    vertices = []
    
    # Créez un ensemble des noms des os de l'armature pour une recherche plus rapide
    armature_bone_names = set(bone.name for bone in Armature.data.bones)
    
    
    for vertex in Mesh.data.vertices: #MeshVertex(bpy_struct)
        cumulateWeight = 0
        
        if vertex.groups:
            for group_elem in vertex.groups: #VertexGroupElement(bpy_struct)
                if group_elem.weight > 0:
                    group_index = group_elem.group
                    group_len = len(Mesh.vertex_groups)
                    if group_index <= group_len:
                        group = Mesh.vertex_groups[group_elem.group]
                        
                        # Utilisez l'ensemble des noms d'os pour vérifier l'appartenance à l'armature
                        if group.name in armature_bone_names:
                            cumulateWeight += group_elem.weight
        
        if cumulateWeight == 0:
            vertices.append(vertex)
    
    return vertices


def ContainsArmatureModifier(obj):
    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            return True
    return False


def GetSkeletonMeshs(obj):
    meshs = []
    if bfu_utils.GetAssetType(obj) == "SkeletalMesh":  # Skeleton /  Armature
        childs = bfu_utils.GetExportDesiredChilds(obj)
        for child in childs:
            if child.type == "MESH":
                meshs.append(child)
    return meshs


def UpdateUnrealPotentialError():
    # Find and reset list of all potential error in scene

    addon_prefs = bfu_basics.GetAddonPrefs()
    PotentialErrors = bpy.context.scene.potentialErrorList
    PotentialErrors.clear()

    # prepares the data to avoid unnecessary loops
    objToCheck = []
    final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
    final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
    for Asset in final_asset_list_to_export:
        if Asset.obj in bfu_utils.GetAllobjectsByExportType("export_recursive"):
            if Asset.obj not in objToCheck:
                objToCheck.append(Asset.obj)
            for child in bfu_utils.GetExportDesiredChilds(Asset.obj):
                if child not in objToCheck:
                    objToCheck.append(child)

    MeshTypeToCheck = []
    for obj in objToCheck:
        if obj.type == 'MESH':
            MeshTypeToCheck.append(obj)

    MeshTypeWithoutCol = []  # is Mesh Type To Check Without Collision
    for obj in MeshTypeToCheck:
        if not bfu_utils.CheckIsCollision(obj):
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
                    if obj.bfu_export_type == "export_recursive":
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
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
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

    def CheckArmatureNumber():
        # check Modifier or Constraint ARMATURE number = 1
        for obj in objToCheck:
            meshs = GetSkeletonMeshs(obj)
            for mesh in meshs:
                # Count
                armature_modifiers = 0
                armature_constraint = 0
                for mod in mesh.modifiers:
                    if mod.type == "ARMATURE":
                        armature_modifiers += 1
                for const in mesh.constraints:
                    if const.type == "ARMATURE":
                        armature_constraint += 1

                # Check result > 1
                if armature_modifiers + armature_constraint > 1:
                    MyError = PotentialErrors.add()
                    MyError.name = mesh.name
                    MyError.type = 2
                    MyError.text = (
                        'In object "'+mesh.name + '" ' +
                        str(armature_modifiers) + ' Armature modifier(s) and ' +
                        str(armature_modifiers) + ' Armature constraint(s) was found. ' +
                        ' Please use only one Armature modifier or one Armature constraint.')
                    MyError.object = mesh

                # Check result == 0
                if armature_modifiers + armature_constraint == 0:
                    MyError = PotentialErrors.add()
                    MyError.name = mesh.name
                    MyError.type = 2
                    MyError.text = (
                        'In object "'+mesh.name + '" ' +
                        ' no Armature modifiers or constraints was found. ' +
                        ' Please use only one Armature modifier or one Armature constraint.')
                    MyError.object = mesh

    def CheckArmatureModData():
        # check the parameter of Modifier ARMATURE
        for obj in MeshTypeToCheck:
            for mod in obj.modifiers:
                if mod.type == "ARMATURE":
                    if mod.use_deform_preserve_volume:
                        MyError = PotentialErrors.add()
                        MyError.name = obj.name
                        MyError.type = 2
                        MyError.text = (
                            'In object "'+obj.name +
                            '" the modifier '+mod.type +
                            ' named "'+mod.name +
                            '". The parameter Preserve Volume' +
                            ' must be set to False.')
                        MyError.object = obj
                        MyError.itemName = mod.name
                        MyError.correctRef = "PreserveVolume"
                        MyError.correctlabel = 'Set Preserve Volume to False'

    def CheckArmatureConstData():
        # check the parameter of constraint ARMATURE
        for obj in MeshTypeToCheck:
            for const in obj.constraints:
                if const.type == "ARMATURE":
                    pass
                    # TO DO.

    def CheckArmatureBoneData():
        # check the parameter of the ARMATURE bones
        for obj in objToCheck:
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                for bone in obj.data.bones:
                    if (not obj.bfu_export_deform_only or
                            (bone.use_deform and obj.bfu_export_deform_only)):

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
            export_as_proxy = bfu_utils.GetExportAsProxy(obj)
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                childs = bfu_utils.GetExportDesiredChilds(obj)
                validChild = 0
                for child in childs:
                    if child.type == "MESH":
                        validChild += 1
                if export_as_proxy:
                    if bfu_utils.GetExportProxyChild(obj) is not None:
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

    def CheckArmatureChildWithBoneParent():
        # If you use Parent Bone to parent your mesh to your armature the import will fail.
        for obj in objToCheck:
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                childs = bfu_utils.GetExportDesiredChilds(obj)
                for child in childs:
                    if child.type == "MESH":
                        if child.parent_type == 'BONE':
                            MyError = PotentialErrors.add()
                            MyError.name = child.name
                            MyError.type = 2
                            MyError.text = (
                                'Object "'+child.name +
                                '" use Parent Bone to parent. ' +
                                '\n If you use Parent Bone to parent your mesh to your armature the import will fail.')
                            MyError.object = child
                            MyError.docsOcticon = 'armature-child-with-bone-parent'

    def CheckArmatureMultipleRoots():
        # Check that skeleton have multiples roots
        for obj in objToCheck:
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                rootBones = bfu_utils.GetArmatureRootBones(obj)

                if len(rootBones) > 1:
                    MyError = PotentialErrors.add()
                    MyError.name = obj.name
                    MyError.type = 1
                    MyError.text = (
                        'Object "'+obj.name +
                        '" have Multiple roots bones.' +
                        ' Unreal only support single root bone')
                    MyError.text += '\nA custom root bone will be added at the export.'
                    MyError.text += ' '+str(len(rootBones))+' root bones found: '
                    MyError.text += '\n'
                    for rootBone in rootBones:
                        MyError.text += rootBone.name+', '
                    MyError.object = obj

    def CheckArmatureNoDeformBone():
        # Check that skeleton have at less one deform bone
        for obj in objToCheck:
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                if obj.bfu_export_deform_only:
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
            meshs = GetSkeletonMeshs(obj)
            for mesh in meshs:
                if mesh.type == "MESH":
                    if ContainsArmatureModifier(mesh):
                        # Result data
                        VertexWithZeroWeight = GetVertexWithZeroWeight(
                            obj,
                            mesh)
                        if len(VertexWithZeroWeight) > 0:
                            MyError = PotentialErrors.add()
                            MyError.name = mesh.name
                            MyError.type = 1
                            MyError.text = (
                                'Object named "'+mesh.name +
                                '" contains '+str(len(VertexWithZeroWeight)) +
                                ' vertex with zero cumulative valid weight.')
                            MyError.text += (
                                '\nNote: Vertex groups must have' +
                                ' a bone with the same name to be valid.')
                            MyError.object = mesh
                            MyError.selectVertexButton = True
                            MyError.selectOption = "VertexWithZeroWeight"

    def CheckZeroScaleKeyframe():
        # Check that animations do not use a invalid value
        for obj in objToCheck:
            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
                animation_to_export = animation_asset_cache.GetAnimationAssetList()
                for action in animation_to_export:
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
    CheckArmatureNumber()
    CheckArmatureModData()
    CheckArmatureConstData()
    CheckArmatureBoneData()
    CheckArmatureValidChild()
    CheckArmatureMultipleRoots()
    CheckArmatureChildWithBoneParent()
    CheckArmatureNoDeformBone()
    CheckMarkerOverlay()
    CheckVertexGroupWeight()
    CheckZeroScaleKeyframe()

    return PotentialErrors


def SelectPotentialErrorObject(errorIndex):
    # Select potential error

    bbpl.utils.safe_mode_set('OBJECT', bpy.context.active_object)
    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object

    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_viewport = False
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # show collection for select object
    for collection in bpy.data.collections:
        for ColObj in collection.objects:
            if ColObj == obj:
                bfu_basics.SetCollectionUse(collection)
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorVertex(errorIndex):
    # Select potential error
    SelectPotentialErrorObject(errorIndex)
    bbpl.utils.safe_mode_set('EDIT')

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    bbpl.utils.safe_mode_set('OBJECT')
    if error.selectOption == "VertexWithZeroWeight":
        for vertex in GetVertexWithZeroWeight(obj.parent, obj):
            vertex.select = True
    bbpl.utils.safe_mode_set('EDIT')
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorPoseBone(errorIndex):
    # Select potential error
    SelectPotentialErrorObject(errorIndex)
    bbpl.utils.safe_mode_set('POSE')

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

    local_view_areas = bbpl.scene_utils.move_to_global_view()

    MyCurrentDataSave = bbpl.utils.UserSceneSave()
    MyCurrentDataSave.save_current_scene()

    bbpl.utils.safe_mode_set('OBJECT', MyCurrentDataSave.user_select_class.user_active)

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
        if bbpl.utils.safe_mode_set("EDIT", obj):
            bpy.ops.uv.smart_project()
            successCorrect = True
        else:
            successCorrect = False

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
    MyCurrentDataSave.reset_select_by_name()
    MyCurrentDataSave.reset_scene_at_save()
    bbpl.scene_utils.move_to_local_view(local_view_areas)

    # ----------------------------------------

    if successCorrect:
        scene.potentialErrorList.remove(errorIndex)
        print("end correct, Error: " + error.correctRef)
        return "Corrected"
    print("end correct, Error not found")
    return "Correct fail"


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


classes = (
    BFU_OT_UnrealPotentialError,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.potentialErrorList = bpy.props.CollectionProperty(type=BFU_OT_UnrealPotentialError)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.potentialErrorList
