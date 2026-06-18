# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import os

import bpy

from ... import bbpl
from . import bfu_object_presets_props

def draw_object_presets_object_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    row = layout.row(align=True)
    row.menu('BFU_MT_ObjectGlobalPropertiesPresets', text='Global Properties Presets')
    row.operator('object.add_globalproperties_preset', text='', icon='ADD')
    row.operator('object.add_globalproperties_preset', text='', icon='REMOVE').remove_active = True  # type: ignore


def draw_object_presets_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_tools_presets_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            row = panel.row(align=True)
            wm = context.window_manager
            preset_path = bfu_object_presets_props.get_selected_global_preset_path(wm)
            if preset_path and os.path.isfile(preset_path):
                preset_name = os.path.splitext(os.path.basename(preset_path))[0]
                row.menu('BFU_MT_ApplyGlobalPropertiesPresets', text=preset_name)
            else:
                row.menu('BFU_MT_ApplyGlobalPropertiesPresets', text='Select Preset')
            row.operator('wm.apply_globalproperties_preset_to_selected', text='Apply to Selected')