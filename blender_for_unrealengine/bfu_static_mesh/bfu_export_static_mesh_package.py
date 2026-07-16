# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List
from pathlib import Path

import bpy

from .. import bfu_export
from ..bbpl.utils import SaveUserRenderSimplify
from .. import bbpl
from .. import bfu_utils
from .. import bfu_vertex_color
from .. import bfu_material
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage
from .. import bfu_adv_object
from .. import bfu_uv_map
from .. import bfu_custom_property
from .. import bfu_anim_base
from .. import bfu_skeletal_mesh
from . import bfu_export_procedure
from .bfu_export_procedure import BFU_StaticExportProcedure


def process_static_mesh_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage
) -> bool:

    if package.file:
        return export_as_static_mesh(
            op = op,
            fullpath=package.file.get_full_path(),
            objs=package.objects
        )
    else:
        return False


def export_as_static_mesh(
    op: bpy.types.Operator,
    fullpath: Path,
    objs: List[bpy.types.Object]
) -> bool:
    
    '''
    #####################################################
            #STATIC MESH
    #####################################################
    '''
        
    # Export a single Mesh
    my_timer_group = SafeTimeGroup()
    my_timer_group.start_timer(f"Prepare export")
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    # [SAVE ASSET DATA]
    # Save asset data before export like transforms, animation data, etc.
    # So can be restored after export.
    saved_simplify: SaveUserRenderSimplify = SaveUserRenderSimplify()
    saved_selection_names = bfu_export.bfu_export_utils.SavedObjectNames()
    saved_selection_names.save_new_names(objs)


    # [SELECT AND DUPLICATE] 
    # Select and duplicate objects for export (Export the duplicated objects)
    bbpl.utils.safe_mode_set('OBJECT')
    bbpl.utils.select_specific_object_list(objs[0], objs)
    duplicate_data = bfu_export.bfu_export_utils.DuplicateData()
    duplicate_data.duplicate_select_for_export_with_rename_and_reparent(bpy.context, False)

    # Duplicated active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object
    bfu_export.bfu_export_utils.set_duplicated_object_export_name(
        duplicated_obj=active, 
        original_obj=objs[0], 
        is_skeletal=False
    )

    # [MAKE REAL COPY] 
    # Make objects real to be able to edit before export.
    bfu_export.bfu_export_utils.convert_selected_to_mesh()
    bfu_export.bfu_export_utils.make_select_visual_real()

    bfu_export.bfu_export_utils.apply_select_needed_modifiers_for_export() 
    if bpy.context.selected_objects:
        for selected_obj in bpy.context.selected_objects:
            if bfu_uv_map.bfu_uv_map_props.get_object_convert_geometry_node_attribute_to_uv(active):
                attrib_name: str = bfu_uv_map.bfu_uv_map_props.get_object_convert_geometry_node_attribute_to_uv_name(active)
                bfu_export.bfu_export_utils.ConvertGeometryNodeAttributeToUV(selected_obj, attrib_name)
            bfu_vertex_color.bfu_vertex_color_utils.SetVertexColorForUnrealExport(selected_obj)
            bfu_export.bfu_export_utils.CorrectExtremUVAtExport(selected_obj)
            bfu_export.bfu_export_utils.SetSocketsExportTransform(selected_obj)
            bfu_export.bfu_export_utils.SetSocketsExportName(selected_obj)
        bfu_export.bfu_export_utils.RemoveMaterialsOnCollisionMeshes(list(bpy.context.selected_objects))

    bfu_adv_object.bfu_adv_obj_utils.apply_object_export_transform(active)

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    static_export_procedure: BFU_StaticExportProcedure = bfu_export_procedure.get_object_export_procedure(active)
    export_result = None
    if (static_export_procedure.value == BFU_StaticExportProcedure.CUSTOM_FBX_EXPORT.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx_with_custom_fbx_io(
            operator=op,
            context=bpy.context,
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            global_matrix=bfu_export.bfu_export_utils.get_static_axis_conversion(active),
            apply_unit_scale=True,
            global_scale=bfu_adv_object.bfu_adv_obj_props.get_object_export_global_scale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(active),
            use_custom_props=bfu_custom_property.bfu_custom_property_props.get_object_fbx_export_with_custom_props(active),
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            bake_anim=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=bfu_adv_object.bfu_adv_obj_props.get_object_export_with_meta_data(active),
            primary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_primary_bone_axis(active),
            secondary_bone_axis=bfu_export.bfu_export_utils.get_final_fbx_export_secondary_bone_axis(active),
            use_ue_mannequin_bone_alignment=bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_use_ue_mannequin_bone_alignment(active),
            disable_free_scale_animation=bfu_anim_base.bfu_anim_base_props.get_object_disable_free_scale_animation(active),
            use_space_transform=bfu_export.bfu_export_utils.get_static_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_static_fbx_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_static_fbx_export_axis_up(active),
            bake_space_transform=False
            
            )
    elif (static_export_procedure.value == BFU_StaticExportProcedure.STANDARD_FBX.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            apply_unit_scale=True,
            global_scale=bfu_adv_object.bfu_adv_obj_props.get_object_export_global_scale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(active),
            use_custom_props=bfu_custom_property.bfu_custom_property_props.get_object_fbx_export_with_custom_props(active),
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            bake_anim=False,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=bfu_adv_object.bfu_adv_obj_props.get_object_export_with_meta_data(active),
            use_space_transform=bfu_export.bfu_export_utils.get_static_fbx_export_use_space_transform(active),
            axis_forward=bfu_export.bfu_export_utils.get_static_fbx_export_axis_forward(active),
            axis_up=bfu_export.bfu_export_utils.get_static_fbx_export_axis_up(active),
            bake_space_transform=False
            )
    elif (static_export_procedure.value == BFU_StaticExportProcedure.STANDARD_GLTF.value):
        export_result = bpy.ops.export_scene.gltf(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            export_materials=bfu_material.bfu_material_utils.get_gltf_export_materials(active),
            export_image_format=bfu_material.bfu_material_utils.get_gltf_export_textures(active),
            export_apply = True,
            )
    else:
        print(f"Error: The export procedure '{static_export_procedure}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()




    bfu_vertex_color.bfu_vertex_color_utils.clear_vertex_color_for_unreal_export(active)
    bfu_export.bfu_export_utils.reset_sockets_export_name(active)
    bfu_export.bfu_export_utils.reset_sockets_transform(active)
    if bpy.context.selected_objects:
        bfu_utils.clean_delete_objects(list(bpy.context.selected_objects)) #sequence to list
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