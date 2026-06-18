# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy

from ... import bbpl

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
            panel.label(text="Presets @TODO")