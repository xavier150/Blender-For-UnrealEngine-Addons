# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from pathlib import Path
from typing import TYPE_CHECKING
from .. import bfu_export
from .. import bbpl
from ..bbpl.utils import SaveUserRenderSimplify
from .. import bfu_utils
from .. import bfu_vertex_color
from ..bfu_assets_manager.bfu_asset_manager_type import AssetPackage
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from . import bfu_export_procedure
from .bfu_export_procedure import BFU_CollectionExportProcedure


def process_collection_as_static_mesh_export_from_package(
    op: bpy.types.Operator,
    package: AssetPackage
) -> bool:

    if package.file and package.collection:
        return export_collection_as_static_mesh(
            op=op,
            fullpath=package.file.get_full_path(),
            col=package.collection
        )
    else:
        return False


def export_collection_as_static_mesh(
    op: bpy.types.Operator,
    fullpath: Path,
    col: bpy.types.Collection
) -> bool:

    '''
    #####################################################
            # COLLECTION AS STATIC MESH
    #####################################################
    '''

    # Export a single collection
    my_timer_group = SafeTimeGroup()
    my_timer_group.start_timer(f"Prepare export")
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    objs = bfu_utils.get_export_collection_objects(col)

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
    duplicate_data = bfu_export.bfu_export_utils.duplicate_select_for_export(bpy.context, False)
    duplicate_data.set_duplicate_name_for_export()

    # Duplicated active that should be used for export.
    if bpy.context.active_object is None:
        raise ValueError("No active object found after duplicate!")
    active: bpy.types.Object = bpy.context.active_object
    bfu_export.bfu_export_utils.set_duplicated_object_export_name(
        duplicated_obj=active, 
        original_obj=objs[0], 
        is_skeletal=False
    )

    if TYPE_CHECKING:
        class FakeCollection(bpy.types.Collection):
            bfu_static_collection_export_procedure: str
        col = FakeCollection()  # type: ignore
        class FakeObject(bpy.types.Object):
            bfu_static_export_procedure: str
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
            attrib_name = active.bfu_convert_geometry_node_attribute_to_uv_name
            bfu_export.bfu_export_utils.ConvertGeometryNodeAttributeToUV(selected_obj, attrib_name)
        bfu_vertex_color.bfu_vertex_color_utils.SetVertexColorForUnrealExport(selected_obj)
        bfu_export.bfu_export_utils.CorrectExtremUVAtExport(selected_obj)
        bfu_export.bfu_export_utils.SetSocketsExportTransform(selected_obj)
        bfu_export.bfu_export_utils.SetSocketsExportName(selected_obj)
    bfu_export.bfu_export_utils.RemoveMaterialsOnCollisionMeshes(bpy.context.selected_objects)

    # [PREPARE SCENE FOR EXPORT]
    # Prepare scene for export (frame range, simplefying, etc.)
    saved_simplify.unsimplify_scene()

    my_timer_group.end_last_timer()

    # Process export
    my_timer_group.start_timer(f"Process export")
    static_collection_export_procedure: BFU_CollectionExportProcedure = bfu_export_procedure.get_col_export_procedure(col)
    export_result = None
    if (static_collection_export_procedure.value == BFU_CollectionExportProcedure.CUSTOM_FBX_EXPORT.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx_with_custom_fbx_io(
            operator=op,
            context=bpy.context,
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            global_scale=1,
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(active),
            use_custom_props=active.bfu_fbx_export_with_custom_props,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            # use_armature_deform_only=active.bfu_export_deform_only,
            bake_anim=False,
            use_metadata=active.bfu_export_with_meta_data,
            # primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(active),
            # secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(active),
            # use_space_transform=bfu_export_utils.get_export_use_space_transform(active),
            # axis_forward=bfu_export_utils.get_export_axis_forward(active),
            # axis_up=bfu_export_utils.get_export_axis_up(active),
            bake_space_transform=False
            )

    elif (static_collection_export_procedure.value == BFU_CollectionExportProcedure.STANDARD_FBX.value):
        export_result = bfu_export.bfu_fbx_export.export_scene_fbx(
            filepath=str(fullpath),
            check_existing=False,
            use_selection=True,
            global_scale=1,
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            #colors_type=bfu_vertex_color.bfu_vertex_color_utils.get_export_colors_type(obj), @TODO
            #use_custom_props=obj.bfu_fbx_export_with_custom_props, @TODO
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            # use_armature_deform_only=active.bfu_export_deform_only,
            bake_anim=False,
            #use_metadata=obj.bfu_export_with_meta_data, @TODO
            # use_space_transform=bfu_export_utils.get_export_use_space_transform(obj),
            # axis_forward=bfu_export_utils.get_export_axis_forward(obj),
            # axis_up=bfu_export_utils.get_export_axis_up(obj),
            bake_space_transform=False
            )
    elif (static_collection_export_procedure.value == BFU_CollectionExportProcedure.STANDARD_GLTF.value):
        # @TODO: Implement GLTF export
        export_result = bfu_export.bfu_gltf_export.export_scene_gltf()
    else:
        print(f"Error: The export procedure '{static_collection_export_procedure}' was not found!")
    my_timer_group.end_last_timer()

    # [RESTORE ASSET DATA]
    # Restore asset data after export like transforms, animation data, etc.
    my_timer_group.start_timer(f"Clean after export")
    saved_selection_names.restore_names()
    saved_simplify.reset_scene()


    for obj in bpy.context.selected_objects:
        bfu_vertex_color.bfu_vertex_color_utils.clear_vertex_color_for_unreal_export(obj)
        bfu_export.bfu_export_utils.reset_sockets_export_name(obj)
        bfu_export.bfu_export_utils.reset_sockets_transform(obj)

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