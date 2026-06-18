# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_cached_assets_blender_class

if "bfu_cached_assets_blender_class" in locals():
    importlib.reload(bfu_cached_assets_blender_class)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_cached_assets_blender_class.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_cached_assets_blender_class.unregister()