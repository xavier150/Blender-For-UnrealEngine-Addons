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
from .. import bfu_export_nomenclature
from .. import bfu_export_filter
from .. import bfu_export_process

def get_export_global_preset_propertys() -> List[str]:
    preset_values: List[str] = []
    preset_values += bfu_export_nomenclature.bfu_export_nomenclature_props.get_preset_values()
    preset_values += bfu_export_filter.bfu_export_filter_props.get_preset_values()
    preset_values += bfu_export_process.bfu_export_process_props.get_preset_values()
    return preset_values

class BFU_PT_Export(bpy.types.Panel):
    # Is Export panel

    bl_idname = "BFU_PT_Export"
    bl_label = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"


    class BFU_MT_NomenclaturePresets(bpy.types.Menu):
        bl_label = 'Nomenclature Presets'
        preset_subdir = 'blender-for-unrealengine/nomenclature-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset  # type: ignore

    from bl_operators.presets import AddPresetBase

    class BFU_OT_AddNomenclaturePreset(AddPresetBase, bpy.types.Operator):  # type: ignore[override]
        bl_idname = 'object.add_nomenclature_preset'
        bl_label = 'Add or remove a preset for Nomenclature'
        bl_description = 'Add or remove a preset for Nomenclature'
        preset_menu = 'BFU_MT_NomenclaturePresets'


        # Common variable used for all preset values
        preset_defines = [
                            'obj = bpy.context.object',
                            'scene = bpy.context.scene'
                         ]

        # Properties to store in the preset
        preset_values = get_export_global_preset_propertys()

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/nomenclature-presets'


    def draw(self, context: bpy.types.Context):
        
        layout = self.layout
        if layout is None:
            return
        
        bfu_debug_settings.start_draw_record()
        events = bfu_debug_settings.root_events
        events.new_event("Draw Export Panel")


        # Presets
        events.add_sub_event("Draw Export Presets")
        row = layout.row(align=True)
        row.menu('BFU_MT_NomenclaturePresets', text='Export Presets')
        row.operator('object.add_nomenclature_preset', text='', icon='ADD')
        row.operator('object.add_nomenclature_preset', text='', icon='REMOVE').remove_active = True  # type: ignore

        # Export sections
        events.stop_last_and_start_new_event("Draw Export Nomenclature")
        bfu_export_nomenclature.bfu_export_nomenclature_ui.draw_ui_scene(layout, context)
        events.stop_last_and_start_new_event("Draw Export Filter")
        bfu_export_filter.bfu_export_filter_ui.draw_ui_scene(layout, context)
        events.stop_last_and_start_new_event("Draw Export Process")
        bfu_export_process.bfu_export_process_ui.draw_ui_scene(layout, context)
        events.stop_last_event()


        events.stop_last_event()
        bfu_debug_settings.stop_draw_record_and_print()

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_Export,
    BFU_PT_Export.BFU_MT_NomenclaturePresets,
    BFU_PT_Export.BFU_OT_AddNomenclaturePreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
