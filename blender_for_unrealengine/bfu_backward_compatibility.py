# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Any
import bpy
from bpy.app.handlers import persistent
from . import bbpl
from .bbpl.backward_compatibility.data_variable_updater import enum_callback
from .bbpl.backward_compatibility.data_variable_updater import object_pointer_callback

def update_old_variables(print_log: bool = False) -> None:
    print("Updating old bfu variables...")

    bfu_addon_updater = bbpl.backward_compatibility.data_variable_updater.DataVariableUpdater()
    bfu_addon_updater.print_log = print_log

    for obj in bpy.data.objects:
        bfu_addon_updater.update_data_variable(obj, ["bfu_skeleton_search_mode"], "bfu_engine_ref_skeleton_search_mode", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["bfu_target_skeleton_custom_path"], "bfu_engine_ref_skeleton_custom_path")
        bfu_addon_updater.update_data_variable(obj, ["bfu_target_skeleton_custom_name"], "bfu_engine_ref_skeleton_custom_name")
        bfu_addon_updater.update_data_variable(obj, ["bfu_target_skeleton_custom_ref"], "bfu_engine_ref_skeleton_custom_ref")

        bfu_addon_updater.update_data_variable(obj, ["exportWithMetaData"], "bfu_export_with_meta_data")
        bfu_addon_updater.update_data_variable(obj, ["bfu_export_procedure"], "bfu_skeleton_export_procedure", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["ExportEnum"], "bfu_export_type", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["exportFolderName"], "bfu_export_folder_name")
        bfu_addon_updater.update_data_variable(obj, ["ExportAsLod"], "bfu_export_as_lod_mesh")
        bfu_addon_updater.update_data_variable(obj, ["ForceStaticMesh"], "bfu_export_skeletal_mesh_as_static_mesh")
        bfu_addon_updater.update_data_variable(obj, ["exportDeformOnly"], "bfu_export_deform_only")
        bfu_addon_updater.update_data_variable(obj, ["Ue4Lod1"], "bfu_lod_target1", object_pointer_callback)
        bfu_addon_updater.update_data_variable(obj, ["Ue4Lod2"], "bfu_lod_target2", object_pointer_callback)
        bfu_addon_updater.update_data_variable(obj, ["Ue4Lod3"], "bfu_lod_target3", object_pointer_callback)
        bfu_addon_updater.update_data_variable(obj, ["Ue4Lod4"], "bfu_lod_target4", object_pointer_callback)
        bfu_addon_updater.update_data_variable(obj, ["Ue4Lod5"], "bfu_lod_target5", object_pointer_callback)
        bfu_addon_updater.update_data_variable(obj, ["CreatePhysicsAsset"], "bfu_create_physics_asset")

        bfu_addon_updater.update_data_variable(obj, ["UseStaticMeshLODGroup"], "bfu_use_static_mesh_lod_group")
        bfu_addon_updater.update_data_variable(obj, ["StaticMeshLODGroup"], "bfu_static_mesh_lod_group")
        bfu_addon_updater.update_data_variable(obj, ["StaticMeshLightMapEnum", "bfu_static_mesh_light_map_enum"], "bfu_static_mesh_light_map_mode", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["customStaticMeshLightMapRes"], "bfu_static_mesh_custom_light_map_res")
        bfu_addon_updater.update_data_variable(obj, ["staticMeshLightMapSurfaceScale"], "bfu_static_mesh_light_map_surface_scale")
        bfu_addon_updater.update_data_variable(obj, ["staticMeshLightMapRoundPowerOfTwo"], "bfu_static_mesh_light_map_round_power_of_two")
        bfu_addon_updater.update_data_variable(obj, ["useStaticMeshLightMapWorldScale"], "bfu_use_static_mesh_light_map_world_scale")
        bfu_addon_updater.update_data_variable(obj, ["GenerateLightmapUVs"], "bfu_generate_light_map_uvs")
        bfu_addon_updater.update_data_variable(obj, ["convert_geometry_node_attribute_to_uv"], "bfu_convert_geometry_node_attribute_to_uv")
        bfu_addon_updater.update_data_variable(obj, ["convert_geometry_node_attribute_to_uv_name"], "bfu_convert_geometry_node_attribute_to_uv_name")
        bfu_addon_updater.update_data_variable(obj, ["AutoGenerateCollision"], "bfu_auto_generate_collision")
        bfu_addon_updater.update_data_variable(obj, ["MaterialSearchLocation"], "bfu_material_search_location", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["CollisionTraceFlag"], "bfu_collision_trace_flag", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["VertexColorImportOption"], "bfu_vertex_color_import_option", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["VertexOverrideColor"], "bfu_vertex_color_override_color")
        bfu_addon_updater.update_data_variable(obj, ["VertexColorToUse"], "bfu_vertex_color_to_use", enum_callback)
        bfu_addon_updater.update_data_variable(obj, ["VertexColorIndexToUse"], "bfu_vertex_color_index_to_use")
        bfu_addon_updater.update_data_variable(obj, ["PrefixNameToExport"], "bfu_prefix_name_to_export")

        bfu_addon_updater.update_data_variable(obj, ["SampleAnimForExport"], "bfu_sample_anim_for_export")
        bfu_addon_updater.update_data_variable(obj, ["SimplifyAnimForExport"], "bfu_simplify_anim_for_export")

        bfu_addon_updater.update_data_variable(obj, ["exportGlobalScale"], "bfu_export_global_scale")

        bfu_addon_updater.update_data_variable(obj, ["MoveToCenterForExport"], "bfu_move_to_center_for_export")
        bfu_addon_updater.update_data_variable(obj, ["RotateToZeroForExport"], "bfu_rotate_to_zero_for_export")
        bfu_addon_updater.update_data_variable(obj, ["MoveActionToCenterForExport"], "bfu_move_action_to_center_for_export")
        bfu_addon_updater.update_data_variable(obj, ["RotateActionToZeroForExport"], "bfu_rotate_action_to_zero_for_export")
        bfu_addon_updater.update_data_variable(obj, ["MoveNLAToCenterForExport"], "bfu_move_nla_to_center_for_export")
        bfu_addon_updater.update_data_variable(obj, ["RotateNLAToZeroForExport"], "bfu_rotate_nla_to_zero_for_export")
        bfu_addon_updater.update_data_variable(obj, ["AdditionalLocationForExport"], "bfu_additional_location_for_export")
        bfu_addon_updater.update_data_variable(obj, ["AdditionalRotationForExport"], "bfu_additional_rotation_for_export")

        bfu_addon_updater.update_data_variable(obj, ["exportActionList", "bfu_animation_asset_list"], "bfu_action_asset_list")
        bfu_addon_updater.update_data_variable(obj, ["active_ObjectAction", "bfu_active_animation_asset_list"], "bfu_active_action_asset_list")

        bfu_addon_updater.update_data_variable(obj, ["ExportAsAlembic", "bfu_export_as_alembic"], "bfu_export_as_alembic_animation")

        bfu_addon_updater.update_data_variable(obj, ["correct_extrem_uv_scale", "bfu_correct_extrem_uv_scale"], "bfu_use_correct_extrem_uv_scale")
        bfu_addon_updater.update_data_variable(obj, ["bfu_invert_normal_maps"], "bfu_flip_normal_map_green_channel")

        bfu_addon_updater.update_data_variable(obj, ["exportAxisForward", "bfu_export_use_space_transform"], "bfu_fbx_export_use_space_transform")
        bfu_addon_updater.update_data_variable(obj, ["exportAxisForward", "bfu_export_axis_forward"], "bfu_fbx_export_axis_forward")
        bfu_addon_updater.update_data_variable(obj, ["exportAxisUp", "bfu_export_axis_up"], "bfu_fbx_export_axis_up")
        bfu_addon_updater.update_data_variable(obj, ["exportPrimaryBoneAxis", "bfu_export_primary_bone_axis"], "bfu_fbx_export_primary_bone_axis")
        bfu_addon_updater.update_data_variable(obj, ["exportSecondaryBoneAxis", "bfu_export_secondary_bone_axis"], "bfu_fbx_export_secondary_bone_axis")

        bfu_addon_updater.update_data_variable(obj, ["exportWithCustomProps", "bfu_export_with_custom_props"], "bfu_fbx_export_with_custom_props")

        bfu_addon_updater.update_data_variable(obj, ["computedStaticMeshLightMapRes"], "bfu_computed_static_mesh_light_map_res")

    for col in bpy.data.collections:
        bfu_addon_updater.update_data_variable(col, ["exportFolderName"], "bfu_export_folder_name")
        bfu_addon_updater.update_data_variable(col, ["bfu_collection_export_procedure"], "bfu_static_collection_export_procedure")
        
    for scene in bpy.data.scenes:
        bfu_addon_updater.update_data_variable(scene, ["static_mesh_prefix_export_name"], "bfu_static_mesh_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["skeletal_mesh_prefix_export_name"], "bfu_skeletal_mesh_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["skeleton_prefix_export_name"], "bfu_skeleton_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["alembic_prefix_export_name", "bfu_alembic_prefix_export_name"], "bfu_alembic_animation_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["anim_prefix_export_name"], "bfu_anim_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["pose_prefix_export_name"], "bfu_pose_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["camera_prefix_export_name"], "bfu_camera_prefix_export_name")
        bfu_addon_updater.update_data_variable(scene, ["anim_subfolder_name"], "bfu_anim_subfolder_name")
        bfu_addon_updater.update_data_variable(scene, ["export_static_file_path", "bfu_export_static_file_path"], "bfu_export_static_mesh_file_path")
        bfu_addon_updater.update_data_variable(scene, ["export_skeletal_file_path", "bfu_export_skeletal_file_path"], "bfu_export_skeletal_mesh_file_path")
        bfu_addon_updater.update_data_variable(scene, ["export_alembic_file_path"], "bfu_export_alembic_file_path")
        bfu_addon_updater.update_data_variable(scene, ["export_camera_file_path"], "bfu_export_camera_file_path")
        bfu_addon_updater.update_data_variable(scene, ["export_other_file_path"], "bfu_export_other_file_path")
        bfu_addon_updater.update_data_variable(scene, ["file_export_log_name"], "bfu_file_export_log_name")
        bfu_addon_updater.update_data_variable(scene, ["file_import_asset_script_name"], "bfu_file_import_asset_script_name")
        bfu_addon_updater.update_data_variable(scene, ["file_import_sequencer_script_name"], "bfu_file_import_sequencer_script_name")
        bfu_addon_updater.update_data_variable(scene, ["unreal_import_module"], "bfu_unreal_import_module")
        bfu_addon_updater.update_data_variable(scene, ["unreal_import_location"], "bfu_unreal_import_location")

        bfu_addon_updater.update_data_variable(scene, ["CollectionExportList", "bfu_collection_asset_list"], "bfu_static_collection_asset_list")
        bfu_addon_updater.update_data_variable(scene, ["active_CollectionExportList", "bfu_active_collection_asset_list"], "bfu_active_static_collection_asset_list")

        bfu_addon_updater.update_data_variable(scene, ["static_export"], "bfu_use_static_export")
        bfu_addon_updater.update_data_variable(scene, ["static_collection_export"], "bfu_use_static_collection_export")
        bfu_addon_updater.update_data_variable(scene, ["skeletal_export"], "bfu_use_skeletal_export")
        bfu_addon_updater.update_data_variable(scene, ["anin_export", "bfu_use_anin_export", "bfu_use_anim_export"], "bfu_use_animation_export")
        bfu_addon_updater.update_data_variable(scene, ["alembic_export"], "bfu_use_alembic_export")
        bfu_addon_updater.update_data_variable(scene, ["groom_simulation_export"], "bfu_use_groom_simulation_export")
        bfu_addon_updater.update_data_variable(scene, ["camera_export"], "bfu_use_camera_export")
        bfu_addon_updater.update_data_variable(scene, ["spline_export"], "bfu_use_spline_export")

        bfu_addon_updater.update_data_variable(scene, ["text_ExportLog"], "bfu_use_text_export_log")
        bfu_addon_updater.update_data_variable(scene, ["text_ImportAssetScript"], "bfu_use_text_import_asset_script")
        bfu_addon_updater.update_data_variable(scene, ["text_ImportSequenceScript"], "bfu_use_text_import_sequence_script")
        bfu_addon_updater.update_data_variable(scene, ["text_AdditionalData"], "bfu_use_text_additional_data")
        bfu_addon_updater.remove_data_variable(scene, ["UnrealExportedAssetsList", "bfu_unreal_exported_assets_logs"])
        bfu_addon_updater.update_data_variable(scene, ["potentialErrorList"], "bfu_export_potential_errors")

    print("End update_rig_backward_compatibility")
    if print_log:
        bfu_addon_updater.print_update_log()



@persistent
def bfu_load_handler(dummy: Any):
    update_old_variables()

def deferred_execution():
    update_old_variables()
    return None  # Important so the timer doesn't repeat

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(bfu_load_handler)
    
    bpy.app.timers.register(deferred_execution, first_interval=0.1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(bfu_load_handler)