# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import importlib

import bpy

from . import bfu_ui_panel_object_class

if "bfu_ui_panel_object_class" in locals():
    importlib.reload(bfu_ui_panel_object_class)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_ui_panel_object_class.register()

def unregister():
    bfu_ui_panel_object_class.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    