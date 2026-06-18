# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List

import bpy
from bl_operators.presets import AddPresetBase

from ... import bfu_custom_property
from ... import bfu_base_object
from ... import bfu_adv_object
from ... import bfu_base_collection
from ... import bfu_collection_as_staticmesh
from ... import bfu_material
from ... import bfu_camera
from ... import bfu_spline
from ... import bfu_vertex_color
from ... import bfu_static_mesh
from ... import bfu_skeletal_mesh
from ... import bfu_modular_skeletal_mesh
from ... import bfu_lod
from ... import bfu_alembic_animation
from ... import bfu_anim_base
from ... import bfu_anim_action
from ... import bfu_anim_action_adv
from ... import bfu_anim_nla
from ... import bfu_anim_nla_adv
from ... import bfu_groom
from ... import bfu_uv_map
from ... import bfu_light_map
from ... import bfu_nanite
from ... import bfu_assets_references
from ... import bfu_collision


def get_object_global_preset_propertys() -> List[str]:
    preset_values: List[str] = []
    # Global properties
    preset_values += bfu_base_object.bfu_base_obj_props.get_preset_values()
    preset_values += bfu_adv_object.bfu_adv_obj_props.get_preset_values()
    preset_values += bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_props.get_preset_values()
    preset_values += bfu_custom_property.bfu_custom_property_props.get_preset_values()
    preset_values += bfu_material.bfu_material_props.get_preset_values()
    preset_values += bfu_vertex_color.bfu_vertex_color_props.get_preset_values()
    preset_values += bfu_lod.bfu_lod_props.get_preset_values()
    preset_values += bfu_uv_map.bfu_uv_map_props.get_preset_values()
    preset_values += bfu_nanite.bfu_nanite_props.get_preset_values()
    preset_values += bfu_light_map.bfu_light_map_props.get_preset_values()
    preset_values += bfu_assets_references.bfu_asset_ref_props.get_preset_values()
    preset_values += bfu_collision.bfu_collision_props.get_preset_values()

    # Scene assets
    preset_values += bfu_base_collection.bfu_base_col_props.get_preset_values()
    preset_values += bfu_collection_as_staticmesh.bfu_static_col_props.get_preset_values()
    preset_values += bfu_collection_as_staticmesh.bfu_export_procedure.get_preset_values()

    # Object assets
    preset_values += bfu_camera.bfu_camera_props.get_preset_values()
    preset_values += bfu_camera.bfu_export_procedure.get_preset_values()
    preset_values += bfu_spline.bfu_spline_props.get_preset_values()
    preset_values += bfu_spline.bfu_export_procedure.get_preset_values()
    preset_values += bfu_groom.bfu_groom_props.get_preset_values()
    preset_values += bfu_groom.bfu_export_procedure.get_preset_values()
    preset_values += bfu_static_mesh.bfu_static_mesh_props.get_preset_values()
    preset_values += bfu_static_mesh.bfu_export_procedure.get_preset_values()
    preset_values += bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_preset_values()
    preset_values += bfu_skeletal_mesh.bfu_export_procedure.get_preset_values()
    preset_values += bfu_alembic_animation.bfu_alembic_animation_props.get_preset_values()
    preset_values += bfu_alembic_animation.bfu_export_procedure.get_preset_values()

    # Skeletal sub assets
    preset_values += bfu_anim_base.bfu_anim_base_props.get_preset_values()
    preset_values += bfu_anim_action.bfu_anim_action_props.get_preset_values()
    preset_values += bfu_anim_action_adv.bfu_anim_action_adv_props.get_preset_values()
    preset_values += bfu_anim_nla.bfu_anim_nla_props.get_preset_values()
    preset_values += bfu_anim_nla_adv.bfu_anim_nla_adv_props.get_preset_values()

    return preset_values


class BFU_MT_ObjectGlobalPropertiesPresets(bpy.types.Menu):
    bl_label = 'Global Properties Presets'
    preset_subdir = 'blender-for-unrealengine/global-properties-presets'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset  # type: ignore


class BFU_OT_AddObjectGlobalPropertiesPreset(AddPresetBase, bpy.types.Operator):  # type: ignore[override]
    bl_idname = 'object.add_globalproperties_preset'
    bl_label = 'Add or remove a preset for Global properties'
    bl_description = 'Add or remove a preset for Global properties'
    preset_menu = 'BFU_MT_ObjectGlobalPropertiesPresets'

    # Common variable used for all preset values
    preset_defines = [
                        'obj = bpy.context.object',
                        'col = bpy.context.collection',
                        'scene = bpy.context.scene'
                        ]

    # Properties to store in the preset
    preset_values = get_object_global_preset_propertys()

    # Directory to store the presets
    preset_subdir = 'blender-for-unrealengine/global-properties-presets'



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_MT_ObjectGlobalPropertiesPresets,
    BFU_OT_AddObjectGlobalPropertiesPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

