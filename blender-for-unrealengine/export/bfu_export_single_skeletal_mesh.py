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
from . import bfu_export_utils
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_check_potential_error


def ProcessSkeletalMeshExport(obj):
    addon_prefs = bfu_basics.GetAddonPrefs()
    dirpath = bfu_utils.GetObjExportDir(obj)
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.skeleton_name = obj.name
    MyAsset.asset_name = obj.name
    MyAsset.folder_name = obj.exportFolderName
    MyAsset.asset_type = bfu_utils.GetAssetType(obj)
    MyAsset.StartAssetExport()

    ExportSingleSkeletalMesh(scene, dirpath, bfu_utils.GetObjExportFileName(obj), obj)
    file = MyAsset.files.add()
    file.name = bfu_utils.GetObjExportFileName(obj)
    file.path = dirpath
    file.type = "FBX"

    if not obj.ExportAsLod:
        if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
            bfu_export_utils.ExportAdditionalParameter(absdirpath, MyAsset)
            file = MyAsset.files.add()
            file.name = bfu_utils.GetObjExportFileName(obj, "_AdditionalTrack.json")
            file.path = dirpath
            file.type = "AdditionalTrack"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleSkeletalMesh(
        originalScene,
        dirpath,
        filename,
        obj
        ):

    '''
    #####################################################
            #SKELETAL MESH
    #####################################################
    '''
    # Export a single Mesh

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    export_as_proxy = bfu_utils.GetExportAsProxy(obj)
    export_proxy_child = bfu_utils.GetExportProxyChild(obj)

    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectParentAndDesiredChilds(obj)
    asset_name = bfu_export_utils.PrepareExportName(obj, True)
    duplicate_data = bfu_export_utils.DuplicateSelectForExport()
    bfu_export_utils.SetDuplicateNameForExport(duplicate_data)

    bfu_utils.ApplyNeededModifierToSelect()
    for obj in bpy.context.selected_objects:
        bfu_export_utils.ConvertGeometryNodeAttributeToUV(obj)
        bfu_export_utils.CorrectExtremUVAtExport(obj)
        bfu_export_utils.SetVertexColorForUnrealExport(obj)
        bfu_export_utils.SetSocketsExportTransform(obj)
        bfu_export_utils.SetSocketsExportName(obj)

    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active

    export_procedure = active.bfu_export_procedure

    if export_as_proxy:
        bfu_export_utils.ApplyProxyData(active)

    bfu_utils.ApplyExportTransform(active, "Object")  # Apply export transform before rescale

    # This will rescale the rig and unit scale to get a root bone egal to 1
    ShouldRescaleRig = bfu_export_utils.GetShouldRescaleRig(active)

    if ShouldRescaleRig:

        rrf = bfu_export_utils.GetRescaleRigFactor()  # rigRescaleFactor
        my_scene_unit_settings = bfu_utils.SceneUnitSettings(bpy.context.scene)
        my_scene_unit_settings.SetUnitForUnrealEngineExport()
        my_skeletal_export_scale = bfu_utils.SkeletalExportScale(active)
        my_skeletal_export_scale.ApplySkeletalExportScale(rrf, is_a_proxy=export_as_proxy)

    meshType = bfu_utils.GetAssetType(active)

    # Set rename temporarily the Armature as "Armature"

    bfu_check_potential_error.UpdateNameHierarchy(
        bfu_utils.GetAllCollisionAndSocketsObj(bpy.context.selected_objects)
        )

    bfu_utils.RemoveAllConsraints(active)
    bpy.context.object.data.pose_position = 'REST'

    bfu_export_utils.ConvertArmatureConstraintToModifiers(active)

    asset_name.SetExportName()

    if (export_procedure == "normal"):
        pass
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            object_types={
                'ARMATURE',
                'EMPTY',
                'CAMERA',
                'LIGHT',
                'MESH',
                'OTHER'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.exportDeformOnly,
            bake_anim=False,
            use_metadata=addon_prefs.exportWithMetaData,
            primary_bone_axis=active.exportPrimaryBaneAxis,
            secondary_bone_axis=active.exporSecondaryBoneAxis,
            axis_forward=active.exportAxisForward,
            axis_up=active.exportAxisUp,
            bake_space_transform=False
            )

    if (export_procedure == "auto-rig-pro"):
        bfu_export_utils.ExportAutoProRig(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            # export_rig_name=GetDesiredExportArmatureName(active),
            bake_anim=False,
            mesh_smooth_type="FACE"
            )

    # This will rescale the rig and unit scale to get a root bone egal to 1
    if ShouldRescaleRig:
        # Reset Curve an unit
        my_scene_unit_settings.ResetUnit()

    asset_name.ResetNames()

    bfu_export_utils.ClearVertexColorForUnrealExport(active)
    bfu_export_utils.ResetArmatureConstraintToModifiers(active)
    bfu_export_utils.ResetSocketsExportName(active)
    bfu_export_utils.ResetSocketsTransform(active)
    bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    bfu_export_utils.ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)
