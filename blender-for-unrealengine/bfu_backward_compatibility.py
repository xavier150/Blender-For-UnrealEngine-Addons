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
from bpy.app.handlers import persistent

def update_variable(data, old_vars, new_var, callback=None):
    for old_var in old_vars:
        if old_var in data:
            if callback:
                data[new_var] = callback(data[old_var])
            else:
                data[new_var] = data[old_var]
            del data[old_var]
            print(f'"{old_var}" updated to "{new_var}" in {data.name}')

def update_old_variables():
    print("Updating old bfu variables...")

    for obj in bpy.data.objects:
        update_variable(obj, ["ExportEnum"], "bfu_export_type", export_enum_callback)
        update_variable(obj, ["exportFolderName"], "bfu_export_folder_name")
        update_variable(obj, ["ExportAsAlembic"], "bfu_export_as_alembic")
        update_variable(obj, ["ExportAsLod"], "bfu_export_as_lod_mesh")
        update_variable(obj, ["ForceStaticMesh"], "bfu_export_skeletal_mesh_as_static_mesh")
        update_variable(obj, ["exportDeformOnly"], "bfu_export_deform_only")
        update_variable(obj, ["Ue4Lod1"], "bfu_lod_target1")
        update_variable(obj, ["Ue4Lod2"], "bfu_lod_target2")
        update_variable(obj, ["Ue4Lod3"], "bfu_lod_target3")
        update_variable(obj, ["Ue4Lod4"], "bfu_lod_target4")
        update_variable(obj, ["Ue4Lod5"], "bfu_lod_target5")
        update_variable(obj, ["CreatePhysicsAsset"], "bfu_create_physics_asset")

        update_variable(obj, ["UseStaticMeshLODGroup"], "bfu_use_static_mesh_lod_group")
        update_variable(obj, ["StaticMeshLODGroup"], "bfu_static_mesh_lod_group")
        update_variable(obj, ["StaticMeshLightMapEnum"], "bfu_static_mesh_light_map_enum")
        update_variable(obj, ["customStaticMeshLightMapRes"], "bfu_static_mesh_custom_light_map_res")
        update_variable(obj, ["staticMeshLightMapSurfaceScale"], "bfu_static_mesh_light_map_surface_scale")
        update_variable(obj, ["staticMeshLightMapRoundPowerOfTwo"], "bfu_static_mesh_light_map_round_power_of_two")
        update_variable(obj, ["useStaticMeshLightMapWorldScale"], "bfu_use_static_mesh_light_map_world_scale")
        update_variable(obj, ["GenerateLightmapUVs"], "bfu_generate_light_map_uvs")
        update_variable(obj, ["convert_geometry_node_attribute_to_uv"], "bfu_convert_geometry_node_attribute_to_uv")
        update_variable(obj, ["convert_geometry_node_attribute_to_uv_name"], "bfu_convert_geometry_node_attribute_to_uv_name")
        update_variable(obj, ["correct_extrem_uv_scale"], "bfu_correct_extrem_uv_scale")
        update_variable(obj, ["AutoGenerateCollision"], "bfu_auto_generate_collision")
        update_variable(obj, ["MaterialSearchLocation"], "bfu_material_search_location")
        update_variable(obj, ["CollisionTraceFlag"], "bfu_collision_trace_flag")
        update_variable(obj, ["VertexColorImportOption"], "bfu_vertex_color_import_option")
        update_variable(obj, ["VertexOverrideColor"], "bfu_vertex_color_override_color")
        update_variable(obj, ["VertexColorToUse"], "bfu_vertex_color_to_use")
        update_variable(obj, ["VertexColorIndexToUse"], "bfu_vertex_color_index_to_use")
        update_variable(obj, ["PrefixNameToExport"], "bfu_prefix_name_to_export")

        update_variable(obj, ["SampleAnimForExport"], "bfu_sample_anim_for_export")
        update_variable(obj, ["SimplifyAnimForExport"], "bfu_simplify_anim_for_export")

        update_variable(obj, ["exportGlobalScale"], "bfu_export_global_scale")
        update_variable(obj, ["exportAxisForward"], "bfu_export_axis_forward")
        update_variable(obj, ["exportAxisUp"], "bfu_export_axis_up")
        update_variable(obj, ["exportPrimaryBoneAxis"], "bfu_export_primary_bone_axis")
        update_variable(obj, ["exportSecondaryBoneAxis"], "bfu_export_secondary_bone_axis")

        update_variable(obj, ["MoveToCenterForExport"], "bfu_move_to_center_for_export")
        update_variable(obj, ["RotateToZeroForExport"], "bfu_rotate_to_zero_for_export")
        update_variable(obj, ["MoveActionToCenterForExport"], "bfu_move_action_to_center_for_export")
        update_variable(obj, ["RotateActionToZeroForExport"], "bfu_rotate_action_to_zero_for_export")
        update_variable(obj, ["MoveNLAToCenterForExport"], "bfu_move_nla_to_center_for_export")
        update_variable(obj, ["RotateNLAToZeroForExport"], "bfu_rotate_nla_to_zero_for_export")
        update_variable(obj, ["AdditionalLocationForExport"], "bfu_additional_location_for_export")
        update_variable(obj, ["AdditionalRotationForExport"], "bfu_additional_rotation_for_export")


    for col in bpy.data.collections:
        update_variable(col, ["exportFolderName"], "bfu_export_folder_name")

    for scene in bpy.data.scenes:
        update_variable(col, ["static_mesh_prefix_export_name"], "bfu_static_mesh_prefix_export_name")
        update_variable(col, ["skeletal_mesh_prefix_export_name"], "bfu_skeletal_mesh_prefix_export_name")
        update_variable(col, ["skeleton_prefix_export_name"], "bfu_skeleton_prefix_export_name")
        update_variable(col, ["alembic_prefix_export_name"], "bfu_alembic_prefix_export_name")
        update_variable(col, ["anim_prefix_export_name"], "bfu_anim_prefix_export_name")
        update_variable(col, ["pose_prefix_export_name"], "bfu_pose_prefix_export_name")
        update_variable(col, ["camera_prefix_export_name"], "bfu_camera_prefix_export_name")
        update_variable(col, ["anim_subfolder_name"], "bfu_anim_subfolder_name")
        update_variable(col, ["export_static_file_path"], "bfu_export_static_file_path")
        update_variable(col, ["export_skeletal_file_path"], "bfu_export_skeletal_file_path")
        update_variable(col, ["export_alembic_file_path"], "bfu_export_alembic_file_path")
        update_variable(col, ["export_camera_file_path"], "bfu_export_camera_file_path")
        update_variable(col, ["export_other_file_path"], "bfu_export_other_file_path")
        update_variable(col, ["file_export_log_name"], "bfu_file_export_log_name")
        update_variable(col, ["file_import_asset_script_name"], "bfu_file_import_asset_script_name")
        update_variable(col, ["file_import_sequencer_script_name"], "bfu_file_import_sequencer_script_name")
        update_variable(col, ["unreal_import_module"], "bfu_unreal_import_module")
        update_variable(col, ["unreal_import_location"], "bfu_unreal_import_location")


def export_enum_callback(value):
    mapping = {
        1: "auto",
        2: "export_recursive",
        3: "dont_export"
    }
    return mapping.get(value, "")


@persistent
def bfu_load_handler(dummy):
    update_old_variables()

def deferred_execution():
    update_old_variables()
    return None  # Important pour que le timer ne se répète pas

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