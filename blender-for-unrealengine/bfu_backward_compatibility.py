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

def update_variable(data, old_var_names, new_var_name, callback=None):
    for old_var_name in old_var_names:
        if old_var_name in data:
            try:
                if callback:
                    new_value = callback(data, old_var_name, new_var_name)
                    setattr(data, new_var_name, new_value)
                else:
                    setattr(data, new_var_name, data[old_var_name])

                del data[old_var_name]
                print(f'"{old_var_name}" updated to "{new_var_name}" in {data.name}')
            except Exception as e:
                print(f'Error updating "{old_var_name}" to "{new_var_name}" in {data.name}: {str(e)}')

def update_old_variables():
    print("Updating old bfu variables...")

    for obj in bpy.data.objects:


        update_variable(obj, ["bfu_skeleton_search_mode"], "bfu_engine_ref_skeleton_search_mode", enum_callback)
        update_variable(obj, ["bfu_target_skeleton_custom_path"], "bfu_engine_ref_skeleton_custom_path")
        update_variable(obj, ["bfu_target_skeleton_custom_name"], "bfu_engine_ref_skeleton_custom_name")
        update_variable(obj, ["bfu_target_skeleton_custom_ref"], "bfu_engine_ref_skeleton_custom_ref")
        
        update_variable(obj, ["exportWithCustomProps"], "bfu_export_with_custom_props")
        update_variable(obj, ["exportWithMetaData"], "bfu_export_with_meta_data")
        update_variable(obj, ["bfu_export_procedure"], "bfu_skeleton_export_procedure", enum_callback)
        update_variable(obj, ["ExportEnum"], "bfu_export_type", enum_callback)
        update_variable(obj, ["exportFolderName"], "bfu_export_folder_name")
        update_variable(obj, ["ExportAsLod"], "bfu_export_as_lod_mesh")
        update_variable(obj, ["ForceStaticMesh"], "bfu_export_skeletal_mesh_as_static_mesh")
        update_variable(obj, ["exportDeformOnly"], "bfu_export_deform_only")
        update_variable(obj, ["Ue4Lod1"], "bfu_lod_target1", object_pointer_callback)
        update_variable(obj, ["Ue4Lod2"], "bfu_lod_target2", object_pointer_callback)
        update_variable(obj, ["Ue4Lod3"], "bfu_lod_target3", object_pointer_callback)
        update_variable(obj, ["Ue4Lod4"], "bfu_lod_target4", object_pointer_callback)
        update_variable(obj, ["Ue4Lod5"], "bfu_lod_target5", object_pointer_callback)
        update_variable(obj, ["CreatePhysicsAsset"], "bfu_create_physics_asset")

        update_variable(obj, ["UseStaticMeshLODGroup"], "bfu_use_static_mesh_lod_group")
        update_variable(obj, ["StaticMeshLODGroup"], "bfu_static_mesh_lod_group")
        update_variable(obj, ["StaticMeshLightMapEnum", "bfu_static_mesh_light_map_enum"], "bfu_static_mesh_light_map_mode", enum_callback)
        update_variable(obj, ["customStaticMeshLightMapRes"], "bfu_static_mesh_custom_light_map_res")
        update_variable(obj, ["staticMeshLightMapSurfaceScale"], "bfu_static_mesh_light_map_surface_scale")
        update_variable(obj, ["staticMeshLightMapRoundPowerOfTwo"], "bfu_static_mesh_light_map_round_power_of_two")
        update_variable(obj, ["useStaticMeshLightMapWorldScale"], "bfu_use_static_mesh_light_map_world_scale")
        update_variable(obj, ["GenerateLightmapUVs"], "bfu_generate_light_map_uvs")
        update_variable(obj, ["convert_geometry_node_attribute_to_uv"], "bfu_convert_geometry_node_attribute_to_uv")
        update_variable(obj, ["convert_geometry_node_attribute_to_uv_name"], "bfu_convert_geometry_node_attribute_to_uv_name")
        update_variable(obj, ["correct_extrem_uv_scale"], "bfu_correct_extrem_uv_scale")
        update_variable(obj, ["AutoGenerateCollision"], "bfu_auto_generate_collision")
        update_variable(obj, ["MaterialSearchLocation"], "bfu_material_search_location", enum_callback)
        update_variable(obj, ["CollisionTraceFlag"], "bfu_collision_trace_flag", enum_callback)
        update_variable(obj, ["VertexColorImportOption"], "bfu_vertex_color_import_option", enum_callback)
        update_variable(obj, ["VertexOverrideColor"], "bfu_vertex_color_override_color")
        update_variable(obj, ["VertexColorToUse"], "bfu_vertex_color_to_use", enum_callback)
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

        update_variable(obj, ["exportActionList"], "bfu_animation_asset_list")
        update_variable(obj, ["active_ObjectAction"], "bfu_active_animation_asset_list")

        update_variable(obj, ["ExportAsAlembic, bfu_export_as_alembic"], "bfu_export_as_alembic_animation")

        


    for col in bpy.data.collections:
        update_variable(col, ["exportFolderName"], "bfu_export_folder_name")

    for scene in bpy.data.scenes:
        update_variable(scene, ["static_mesh_prefix_export_name"], "bfu_static_mesh_prefix_export_name")
        update_variable(scene, ["skeletal_mesh_prefix_export_name"], "bfu_skeletal_mesh_prefix_export_name")
        update_variable(scene, ["skeleton_prefix_export_name"], "bfu_skeleton_prefix_export_name")
        update_variable(scene, ["alembic_prefix_export_name", "bfu_alembic_prefix_export_name"], "bfu_alembic_animation_prefix_export_name")
        update_variable(scene, ["anim_prefix_export_name"], "bfu_anim_prefix_export_name")
        update_variable(scene, ["pose_prefix_export_name"], "bfu_pose_prefix_export_name")
        update_variable(scene, ["camera_prefix_export_name"], "bfu_camera_prefix_export_name")
        update_variable(scene, ["anim_subfolder_name"], "bfu_anim_subfolder_name")
        update_variable(scene, ["export_static_file_path"], "bfu_export_static_file_path")
        update_variable(scene, ["export_skeletal_file_path"], "bfu_export_skeletal_file_path")
        update_variable(scene, ["export_alembic_file_path"], "bfu_export_alembic_file_path")
        update_variable(scene, ["export_camera_file_path"], "bfu_export_camera_file_path")
        update_variable(scene, ["export_other_file_path"], "bfu_export_other_file_path")
        update_variable(scene, ["file_export_log_name"], "bfu_file_export_log_name")
        update_variable(scene, ["file_import_asset_script_name"], "bfu_file_import_asset_script_name")
        update_variable(scene, ["file_import_sequencer_script_name"], "bfu_file_import_sequencer_script_name")
        update_variable(scene, ["unreal_import_module"], "bfu_unreal_import_module")
        update_variable(scene, ["unreal_import_location"], "bfu_unreal_import_location")

        update_variable(scene, ["CollectionExportList"], "bfu_collection_asset_list")
        update_variable(scene, ["active_CollectionExportList"], "bfu_active_collection_asset_list")


def enum_callback(data, old_var_name, new_var_name):
    value = data[old_var_name] # Get value ast int

    enum_definition = data.bl_rna.properties.get(new_var_name)

    if enum_definition and enum_definition.type == "ENUM":
        # Obtenez la liste des valeurs de l'enum
        for enum_item in enum_definition.enum_items:
            if value == enum_item.value:
                return enum_item.identifier
    else:
        print("La propriété spécifiée n'est pas une énumération.")

    return value

def object_pointer_callback(data, old_var_name, new_var_name):
    value = data[old_var_name]
    if isinstance(value, bpy.types.Object):
        return value
    return None



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