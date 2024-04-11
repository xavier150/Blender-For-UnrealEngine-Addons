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
from bpy_extras.io_utils import axis_conversion
from . import bfu_export_utils
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_naming
from .. import bfu_check_potential_error
from .. import bfu_export_logs
from ..fbxio import export_fbx_bin

if "bpy" in locals():
    import importlib
    if "bfu_export_utils" in locals():
        importlib.reload(bfu_export_utils)
    if "bbpl" in locals():
        importlib.reload(bbpl)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)
    if "export_fbx_bin" in locals():
        importlib.reload(export_fbx_bin)

def ProcessSkeletalMeshExport(op, armature, mesh_parts, desired_name=""):
    addon_prefs = bfu_basics.GetAddonPrefs()
    dirpath = bfu_utils.GetObjExportDir(armature)
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene
    if desired_name:
        final_name = desired_name
    else:
        final_name = armature.name

    MyAsset: bfu_export_logs.BFU_OT_UnrealExportedAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = armature
    MyAsset.skeleton_name = armature.name
    MyAsset.asset_name = armature.name
    MyAsset.asset_global_scale = armature.bfu_export_global_scale
    MyAsset.folder_name = armature.bfu_export_folder_name
    MyAsset.asset_type = bfu_utils.GetAssetType(armature)

    file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
    file.file_name = bfu_naming.get_skeletal_mesh_file_name(armature, final_name, "")
    file.file_extension = "fbx"
    file.file_path = dirpath
    file.file_type = "FBX"

    MyAsset.StartAssetExport()
    ExportSingleSkeletalMesh(op, scene, dirpath, file.GetFileWithExtension(), armature, mesh_parts)

    if not armature.bfu_export_as_lod_mesh:
        if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
        
            file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
            file.file_name = bfu_naming.get_skeletal_mesh_file_name(armature, final_name+"_AdditionalTrack", "")
            file.file_extension = "json"
            file.file_path = dirpath
            file.file_type = "AdditionalTrack"
            bfu_export_utils.ExportAdditionalParameter(absdirpath, file.GetFileWithExtension(), MyAsset)

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleSkeletalMesh(
        op,
        originalScene,
        dirpath,
        filename,
        armature,
        mesh_parts
        ):

    '''
    #####################################################
            #SKELETAL MESH
    #####################################################
    '''
    # Export a single Mesh

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    export_as_proxy = bfu_utils.GetExportAsProxy(armature)
    export_proxy_child = bfu_utils.GetExportProxyChild(armature)

    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectParentAndSpecificChilds(armature, mesh_parts)
    asset_name = bfu_export_utils.PrepareExportName(armature, True)
    duplicate_data = bfu_export_utils.DuplicateSelectForExport()
    bfu_export_utils.SetDuplicateNameForExport(duplicate_data)

    bfu_export_utils.ConvertSelectedCurveToMesh()
    bfu_export_utils.MakeSelectVisualReal()

    bfu_utils.ApplyNeededModifierToSelect()
    for selected_obj in bpy.context.selected_objects:
        if armature.bfu_convert_geometry_node_attribute_to_uv:
            attrib_name = armature.bfu_convert_geometry_node_attribute_to_uv_name
            bfu_export_utils.ConvertGeometryNodeAttributeToUV(selected_obj, attrib_name)
        bfu_export_utils.SetVertexColorForUnrealExport(selected_obj)
        bfu_export_utils.CorrectExtremUVAtExport(selected_obj)
        bfu_export_utils.SetSocketsExportTransform(selected_obj)
        bfu_export_utils.SetSocketsExportName(selected_obj)

    saved_base_transforms = bfu_export_utils.SaveTransformObjects(armature)
    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active

    skeleton_export_procedure = active.bfu_skeleton_export_procedure

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
    bfu_utils.RemoveAllConsraints(active)
    bpy.context.object.data.pose_position = 'REST'

    bfu_export_utils.ConvertArmatureConstraintToModifiers(active)

    asset_name.SetExportName()

    save_use_simplify = bbpl.utils.SaveUserRenderSimplify()
    scene.render.use_simplify = False

    if (skeleton_export_procedure == "ue-standard"):
        export_fbx_bin.save(
            operator=op,
            context=bpy.context,
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            use_active_collection=False,
            global_matrix=axis_conversion(to_forward=active.bfu_export_axis_forward, to_up=active.bfu_export_axis_up).to_4x4(),
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={
                'ARMATURE',
                'EMPTY',
                'CAMERA',
                'LIGHT',
                'MESH',
                'OTHER'},
            use_custom_props=active.bfu_export_with_custom_props,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.bfu_export_deform_only,
            armature_nodetype='NULL',
            bake_anim=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=active.bfu_export_with_meta_data,
            primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(active),
            mirror_symmetry_right_side_bones=active.bfu_mirror_symmetry_right_side_bones,
            use_ue_mannequin_bone_alignment=active.bfu_use_ue_mannequin_bone_alignment,
            disable_free_scale_animation=active.bfu_disable_free_scale_animation,
            use_space_transform=bfu_export_utils.get_skeleton_export_use_space_transform(active),
            axis_forward=bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure == "blender-standard"):
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            use_active_collection=False,
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={
                'ARMATURE',
                'EMPTY',
                'CAMERA',
                'LIGHT',
                'MESH',
                'OTHER'},
            use_custom_props=active.bfu_export_with_custom_props,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.bfu_export_deform_only,
            armature_nodetype='NULL',
            bake_anim=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=active.bfu_export_with_meta_data,
            primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(active),
            use_space_transform=bfu_export_utils.get_skeleton_export_use_space_transform(active),
            axis_forward=bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure == "auto-rig-pro"):
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            # export_rig_name=GetDesiredExportArmatureName(active),
            bake_anim=False,
            mesh_smooth_type="FACE"
            )

    # This will rescale the rig and unit scale to get a root bone egal to 1
    if ShouldRescaleRig:
        # Reset Curve an unit
        my_scene_unit_settings.ResetUnit()

    # Reset Transform
    saved_base_transforms.reset_object_transforms()

    save_use_simplify.LoadUserRenderSimplify()
    asset_name.ResetNames()
    bfu_export_utils.ClearVertexColorForUnrealExport(active)
    bfu_export_utils.ResetArmatureConstraintToModifiers(active)
    bfu_export_utils.ResetSocketsExportName(active)
    bfu_export_utils.ResetSocketsTransform(active)
    bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    bfu_export_utils.ResetDuplicateNameAfterExport(duplicate_data)

    for armature in scene.objects:
        bfu_utils.ClearAllBFUTempVars(armature)
