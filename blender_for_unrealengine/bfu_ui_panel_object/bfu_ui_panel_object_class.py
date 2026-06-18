# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List
import bpy
from .. import bfu_debug_settings
from .. import bbpl
from .. import addon_cached_propertys
from .. import bfu_custom_property
from .. import bfu_base_object
from .. import bfu_adv_object
from .. import bfu_base_collection
from .. import bfu_collection_as_staticmesh
from .. import bfu_material
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_vertex_color
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_modular_skeletal_mesh
from .. import bfu_lod
from .. import bfu_alembic_animation
from .. import bfu_anim_base
from .. import bfu_anim_action
from .. import bfu_anim_action_adv
from .. import bfu_anim_nla
from .. import bfu_anim_nla_adv
from .. import bfu_groom
from .. import bfu_uv_map
from .. import bfu_light_map
from .. import bfu_nanite
from .. import bfu_assets_references
from .. import bfu_collision

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

class BFU_PT_BlenderForUnrealObject(bpy.types.Panel):
    # Unreal engine export panel

    bl_idname = "BFU_PT_BlenderForUnrealObject"
    bl_label = "Unreal Engine Assets Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    class BFU_MT_ObjectGlobalPropertiesPresets(bpy.types.Menu):
        bl_label = 'Global Properties Presets'
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset  # type: ignore

    from bl_operators.presets import AddPresetBase

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

    def draw(self, context: bpy.types.Context):

        layout = self.layout
        if layout is None:
            return
        
        bfu_debug_settings.start_draw_record()
        events = bfu_debug_settings.root_events
        events.new_event("Draw Object Properties")

        # Extension details
        events.add_sub_event("Draw Extension Details")
        events.stop_last_and_start_new_event("S1")
        credit_box = layout.box()
        credit_box.label(text=bpy.app.translations.pgettext("Unreal Engine Assets Exporter by Xavier Loux. (BleuRaven)", "interface.intro"))
        credit_box.label(text='Version '+ addon_cached_propertys.ADDON_VERSION_STR)

        events.stop_last_and_start_new_event("S2")
        bbpl.blender_layout.layout_doc_button.functions.add_doc_page_operator(
            layout = layout,
            url = "https://github.com/xavier150/Blender-For-UnrealEngine-Addons",
            text = "Open Github page",
            icon="HELP"
            )
        events.stop_last_event()
        
        # Presets
        events.stop_last_and_start_new_event("Draw Presets")
        row = layout.row(align=True)
        row.menu('BFU_MT_ObjectGlobalPropertiesPresets', text='Global Properties Presets')
        row.operator('object.add_globalproperties_preset', text='', icon='ADD')
        row.operator('object.add_globalproperties_preset', text='', icon='REMOVE').remove_active = True  # type: ignore

        # Tab Buttons
        events.stop_last_and_start_new_event("Draw Tab Buttons")
        scene = context.scene
        layout.row().prop(scene, "bfu_active_tab", expand=True)
        if scene.bfu_active_tab == "OBJECT":  # type: ignore
            layout.row().prop(scene, "bfu_active_object_tab", expand=True)
        events.stop_last_event()

        # Modules UI
        if context.object is None:
            layout.row().label(text='No active object.')

        else:
            obj: bpy.types.Object = context.object
        
            # Object
            events.add_sub_event("Draw Object UI")
            # Global properties
            bfu_base_object.bfu_base_obj_ui.draw_general_ui_object(layout, context, obj)
            
            bfu_alembic_animation.bfu_alembic_animation_ui.draw_general_ui_object(layout, obj)
            bfu_groom.bfu_groom_ui.draw_general_ui_object(layout, obj)
            bfu_skeletal_mesh.bfu_skeletal_mesh_ui.draw_general_ui_object(layout, obj)
            bfu_spline.bfu_spline_ui.draw_general_ui_object(layout, obj)

            # Specific properties
            bfu_adv_object.bfu_adv_obj_ui.draw_ui_object(layout, context, obj)
            bfu_static_mesh.bfu_static_mesh_ui.draw_ui_object(layout, context, obj)
            bfu_skeletal_mesh.bfu_skeletal_mesh_ui.draw_ui_object(layout, context, obj)
            bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_ui.draw_ui_object(layout, context, obj)
            bfu_alembic_animation.bfu_alembic_animation_ui.draw_ui_object(layout, context, obj)
            bfu_groom.bfu_groom_ui.draw_ui_object(layout, context, obj)
            bfu_camera.bfu_camera_ui.draw_ui_object_camera(layout, context, obj)
            bfu_spline.bfu_spline_ui.draw_ui_object_spline(layout, context, obj)
            bfu_lod.bfu_lod_ui.draw_ui_object(layout, context, obj)
            bfu_collision.bfu_collision_ui.draw_ui_object(layout, context, obj)
            bfu_uv_map.bfu_uv_map_ui.draw_obj_ui(layout, context, obj)
            bfu_light_map.bfu_light_map_ui.draw_obj_ui(layout, context, obj)
            bfu_nanite.bfu_nanite_ui.draw_obj_ui(layout, context, obj)
            bfu_material.bfu_material_ui.draw_ui_object(layout, context, obj)
            bfu_vertex_color.bfu_vertex_color_ui.draw_ui_object(layout, context, obj)
            bfu_assets_references.bfu_asset_ref_ui.draw_ui_object(layout, context, obj)

            # Animations
            events.stop_last_and_start_new_event("Draw Animations UI")
            bfu_anim_action.bfu_anim_action_ui.draw_ui_object(layout, context, obj)
            bfu_anim_action_adv.bfu_anim_action_adv_ui.draw_ui_object(layout, context, obj)
            bfu_anim_nla.bfu_anim_nla_ui.draw_ui_object(layout, context, obj)
            bfu_anim_nla_adv.bfu_anim_nla_adv_ui.draw_ui_object(layout, context, obj)
            bfu_anim_base.bfu_anim_base_ui.draw_ui_object(layout, context, obj)
            events.stop_last_event()

        # Scene
        events.add_sub_event("Draw Scene UI")
        bfu_base_collection.bfu_base_col_ui.draw_ui_scene(layout, context)
        bfu_collection_as_staticmesh.bfu_static_col_ui.draw_ui_scene(layout, context)
        events.stop_last_event()

        events.stop_last_event()
        bfu_debug_settings.stop_draw_record_and_print()


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealObject,
    BFU_PT_BlenderForUnrealObject.BFU_MT_ObjectGlobalPropertiesPresets,
    BFU_PT_BlenderForUnrealObject.BFU_OT_AddObjectGlobalPropertiesPreset,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
