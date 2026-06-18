# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy

from .. import bfu_ui


def draw_ui_scene(layout: bpy.types.UILayout, context: bpy.types.Context):

    scene = bpy.context.scene
    if scene is None:
        return 

    if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("SCENE", "GENERAL"):
        pass