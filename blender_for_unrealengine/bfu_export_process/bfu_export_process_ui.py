# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl
from .. import bfu_asset_preview
from .. import bfu_addon_prefs


def draw_ui_scene(layout: bpy.types.UILayout, context: bpy.types.Context):
    draw_export_ui(layout, context)
    draw_copy_import_script_ui(layout, context)

def draw_export_ui(
    layout: bpy.types.UILayout, 
    context: bpy.types.Context,
) -> None:
    
    scene = context.scene
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_export_process_properties_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:

            # Feedback info :
            bfu_asset_preview.bfu_asset_preview_ui.draw_asset_preview_bar(panel, context)

            # Export button :
            checkButton = panel.row(align=True)
            checkButton.operator("object.checkpotentialerror", icon='FILE_TICK')
            checkButton.operator("object.openpotentialerror", icon='LOOP_BACK', text="")

            exportButton = panel.row()
            exportButton.scale_y = 2.0
            exportButton.operator("object.exportforunreal", icon='EXPORT')


def draw_copy_import_script_ui(
    layout: bpy.types.UILayout, 
    context: bpy.types.Context,
) -> None:
    
    scene = context.scene
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_script_tool_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            if addon_prefs.useGeneratedScripts:
                copyButton = panel.row()
                copyButton.operator("object.copy_importassetscript_command")
                copyButton.operator("object.copy_importsequencerscript_command")
                panel.label(text="Click on one of the buttons to copy the import command.", icon='INFO')
                panel.label(text="Then paste it into the cmd console of unreal.")
                panel.label(text="You need activate python plugins in Unreal Engine.")

            else:
                panel.label(text='(Generated scripts are deactivated.)')