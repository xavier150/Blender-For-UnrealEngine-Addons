# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl
from .. import bfu_addon_prefs


def draw_ui_scene(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_export_filter_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:

            # Assets
            row = panel.row()
            AssetsCol = row.column()
            AssetsCol.label(text="Asset types to export", icon='PACKAGE')
            AssetsCol.prop(scene, 'bfu_use_static_export')
            AssetsCol.prop(scene, 'bfu_use_static_collection_export')
            AssetsCol.prop(scene, 'bfu_use_skeletal_export')
            AssetsCol.prop(scene, 'bfu_use_animation_export')
            AssetsCol.prop(scene, 'bfu_use_alembic_export')
            AssetsCol.prop(scene, 'bfu_use_groom_simulation_export')
            AssetsCol.prop(scene, 'bfu_use_camera_export')
            AssetsCol.prop(scene, 'bfu_use_spline_export')
            panel.separator()

            # Additional file
            FileCol = row.column()
            FileCol.label(text="Additional file", icon='PACKAGE')
            FileCol.prop(scene, 'bfu_use_text_export_log')
            FileCol.prop(scene, 'bfu_use_text_import_asset_script')
            FileCol.prop(scene, 'bfu_use_text_import_sequence_script')
            if addon_prefs.useGeneratedScripts:
                FileCol.prop(scene, 'bfu_use_text_additional_data')

            # exportProperty
            export_by_select = panel.row()
            export_by_select.prop(scene, 'bfu_export_selection_filter')