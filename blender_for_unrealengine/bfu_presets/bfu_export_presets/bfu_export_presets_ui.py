# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy

def draw_export_presets_export_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    row = layout.row(align=True)
    row.menu('BFU_MT_NomenclaturePresets', text='Export Presets')
    row.operator('object.add_nomenclature_preset', text='', icon='ADD')
    row.operator('object.add_nomenclature_preset', text='', icon='REMOVE').remove_active = True  # type: ignore
