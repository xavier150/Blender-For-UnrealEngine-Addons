# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List
from pathlib import Path
from typing import TYPE_CHECKING
from .. import bbpl
from ..bbpl.utils import SaveUserRenderSimplify
from .. import bfu_utils
from .. import bfu_skeletal_mesh
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_SkeletonExportProcedure
from .. import bfu_vertex_color
from .. import bfu_material
from .. import bfu_export
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage


def process_skeletal_mesh_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage
) -> bool:
    if package.file:
        return export_as_skeletal_mesh(
            op=op,
            fullpath=package.file.get_full_path(),
            armature=package.objects[0],
            mesh_parts=package.objects[1:]
        )
    else:
        return False


def export_as_skeletal_mesh(
    op: bpy.types.Operator,
    fullpath: Path,
    armature: bpy.types.Object,
    mesh_parts: List[bpy.types.Object]
) -> bool:

    '''
    #####################################################
            #SKELETAL MESH
    #####################################################
    '''

    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError(f"The armature object is not a valid Armature type! Inputs: armature: {armature.name}")  

    # Export a single Mesh
    my_timer_group = SafeTimeGroup()
    my_timer_group.start_timer(f"Prepare export")
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    
    is_library: bool = armature.data.library is not None  # type: ignore

    # [SAVE ASSET DATA]
    # Save asset data before export like transforms, animation data, etc.
    # So can be restored after export.
    saved_simplify: SaveUserRenderSimplify = SaveUserRenderSimplify()
    saved_selection_names = bfu_export.bfu_export_utils.SavedObjectNames()
    saved_selection_names.save_new_name(armature)
    saved_selection_names.save_new_names(mesh_parts)
    saved_unit_scale = scene.unit_settings.scale_length


    # [SELECT AND DUPLICATE] 
    # Select and duplicate objects for export (Export the duplicated objects)
    bbpl.utils.safe_mode_set('OBJECT')
    bbpl.utils.select_specific_object_list(armature, mesh_parts)
    # Deselect sockets because Unreal Engine detect them as bones
    bfu_skeletal_mesh.bfu_skeletal_mesh_utils.deselect_socket(armature) 

    duplicate_data = bfu_export.bfu_export_utils.DuplicateData()
    if not is_library:
        duplicate_data.duplicate_select_for_export(bpy.context, False)
        duplicate_data.set_duplicate_name_for_export()

    # Duplicated active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object

    bfu_export.bfu_export_utils.set_duplicated_object_export_name(
        duplicated_obj=active, 
        original_obj=armature, 
        is_skeletal=True
    )

    if TYPE_CHECKING:
        class FakeObject(bpy.types.Object):
            bfu_skeleton_export_procedure: str
            bfu_convert_geometry_node_attribute_to_uv: bool
            bfu_convert_geometry_node_attribute_to_uv_name: str
            bfu_fbx_export_with_custom_props: bool
            bfu_export_deform_only: bool
            bfu_export_with_meta_data: bool
            bfu_mirror_symmetry_right_side_bones: bool
            bfu_use_ue_mannequin_bone_alignment: bool
            bfu_disable_free_scale_animation: bool
            bfu_fbx_export_with_custom_props: bool
        active = FakeObject()  # type: ignore

    # [MAKE REAL COPY] Make objects real to be able to edit before export
    bfu_export.bfu_export_utils.convert_selected_to_mesh()
    bfu_export.bfu_export_utils.make_select_visual_real()

    bfu_export.bfu_export_utils.apply_select_needed_modifiers_for_export()
    for selected_obj in bpy.context.selected_objects:
        if active.bfu_convert_geometry_node_attribute_to_uv:
            attrib_name: str = str(active.bfu_convert_geometry_node_attribute_to_uv_name)
            bfu_export.bfu_export_utils.ConvertGeometryNodeAttributeToUV(selected_obj, attrib_name)
        bfu_vertex_color.bfu_vertex_color_utils.SetVertexColorForUnrealExport(selected_obj)
        bfu_export.bfu_export_utils.CorrectExtremUVAtExport(selected_obj)
        bfu_export.bfu_export_utils.SetSocketsExportTransform(selected_obj)
        bfu_export.bfu_export_utils.SetSocketsExportName(selected_obj)
    bfu_export.bfu_export_utils.RemoveMaterialsOnCollisionMeshes(bpy.context.selected_objects)

    bfu_utils.apply_export_transform(active, "Object")  # Apply export transform before rescale

    # This will rescale the rig and unit scale to get a root bone egal to 1
    should_rescale_rig = bfu_export.bfu_export_utils.get_should_rescale_skeleton_for_fbx_export(active) 
    if should_rescale_rig:
        rrf = bfu_export.bfu_export_utils.get_rescale_rig_factor()  # rigRescaleFactor
        scene.unit_settings.scale_length = 0.01
        my_skeletal_export_scale = bfu_utils.SkeletalExportScale(active)
        my_skeletal_export_scale.apply_skeletal_export_scale(rrf)
        my_modifiers_data_scale = bfu_utils.ModifiersDataScale(rrf)
        my_modifiers_data_scale.rescale_for_unreal_engine()

    # Set rename temporarily the Armature as "Armature"
    armature_bones_constraints = bfu_export.bfu_export_utils.disable_all_bone_constraints(active) # @TODO: Please what the reason to disable all bones constraints at skeletal mesh export?
    armature_rest_pose_data = bfu_export.bfu_export_utils.set_armature_to_rest_pose(active)
    bfu_export.bfu_export_utils.convert_armature_constraint_to_modifiers(active)

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    skeleton_export_procedure = bfu_skeletal_mesh.bfu_export_procedure.get_object_export_procedure(active)
    export_result = None
    if (skeleton_export_procedure.value == BFU_SkeletonExportProcedure.CUSTOM_FBX_EXPORT.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx_with_custom_fbx_io(
            operator=op,
            context=bpy.context,
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            use_active_collection=False,
            global_matrix=bfu_export.bfu_export_utils.get_skeleton_axis_conversion(active),
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
            colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(active),
            use_custom_props=active.bfu_fbx_export_with_custom_props,
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
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            mirror_symmetry_right_side_bones=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_mirror_symmetry_right_side_bones(active),
            use_ue_mannequin_bone_alignment=active.bfu_use_ue_mannequin_bone_alignment,
            disable_free_scale_animation=active.bfu_disable_free_scale_animation,
            use_space_transform=bfu_export.bfu_export_utils.get_skeleton_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_FBX.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx(
            filepath=str(fullpath),
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
            colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(active),
            use_custom_props=active.bfu_fbx_export_with_custom_props,
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
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            use_space_transform=bfu_export.bfu_export_utils.get_skeleton_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_skeleton_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_skeleton_export_axis_up(active),
            bake_space_transform=False
            )
    elif (skeleton_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_GLTF.value):
        export_result = bpy.ops.export_scene.gltf(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            export_def_bones=active.bfu_export_deform_only,
            export_materials=bfu_material.bfu_material_utils.get_gltf_export_materials(active),  # type: ignore
            export_image_format=bfu_material.bfu_material_utils.get_gltf_export_textures(active),  # type: ignore
            export_apply = True,
            export_animations = False,

            # If export_try_sparse_sk is True the import fail in Unreal Engine 5.4 and older versions.
            # It a bug from the Interchange pipeline when the skeletal mesh contrains several shape keys. (morph targets)
            # That now fixed since Unreal Engine 5.5. but I keep it on False for compatibility.
            export_try_sparse_sk=False,
            )
    else:
        print(f"Error: The export procedure '{skeleton_export_procedure}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    scene.unit_settings.scale_length = saved_unit_scale
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()

    # This will rescale the rig and unit scale to get a root bone egal to 1
    if should_rescale_rig:
        # Reset Curve an unit
        my_modifiers_data_scale.ResetScaleAfterExport()  # type: ignore

    bfu_vertex_color.bfu_vertex_color_utils.clear_vertex_color_for_unreal_export(active)
    bfu_export.bfu_export_utils.reset_armature_constraint_to_modifiers(active)
    bfu_export.bfu_export_utils.reset_sockets_export_name(active)
    bfu_export.bfu_export_utils.reset_sockets_transform(active)
    
    if is_library:
        armature_bones_constraints.reset_all_bone_constraints()
        armature_rest_pose_data.reset_armature_pose_position()
    else:
        bfu_utils.clean_delete_objects(bpy.context.selected_objects)

        for data in duplicate_data.data_to_remove:
            data.remove_data()

        duplicate_data.reset_duplicate_name_after_export()

        

    for obj in scene.objects:
        bfu_utils.clear_all_bfu_temp_vars(obj)
    my_timer_group.end_last_timer()

    # [RETURN EXPORT RESULT]
    if export_result:
        if export_result == {'FINISHED'}:
            return True
    return False