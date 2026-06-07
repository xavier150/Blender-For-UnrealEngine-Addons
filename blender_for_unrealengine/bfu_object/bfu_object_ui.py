# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl


def draw_tools_ui(layout: bpy.types.UILayout, context: bpy.types.Context):
    scene = context.scene

    accordion = bbpl.blender_layout.layout_accordion.get_accordion(scene, "bfu_object_tools_expanded")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            object_ui = panel.column()
            object_ui.label(text="Copy Active Transform for Unreal:")
            object_ui.operator("object.copy_active_object_location_for_unreal", icon="COPYDOWN", text="Location")
            object_ui.operator("object.copy_active_object_rotation_for_unreal", icon="COPYDOWN", text="Rotation")
            object_ui.operator("object.copy_active_object_scale_for_unreal", icon="COPYDOWN", text="Scale")