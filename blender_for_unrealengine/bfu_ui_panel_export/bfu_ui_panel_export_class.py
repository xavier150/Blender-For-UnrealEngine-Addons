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
from ..bfu_presets import bfu_export_presets

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

    def draw(self, context: bpy.types.Context):
        
        layout = self.layout
        if layout is None:
            return
        
        bfu_debug_settings.start_draw_record()
        events = bfu_debug_settings.root_events
        events.new_event("Draw Export Panel")


        # Presets
        events.add_sub_event("Draw Export Presets")
        bfu_export_presets.bfu_export_presets_ui.draw_export_presets_export_ui(layout, context)

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
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
