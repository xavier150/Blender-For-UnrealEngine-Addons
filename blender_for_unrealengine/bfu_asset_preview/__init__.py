# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_asset_preview_operators
from . import bfu_asset_preview_ui

if "bfu_asset_preview_operators" in locals():
    importlib.reload(bfu_asset_preview_operators)
if "bfu_asset_preview_ui" in locals():
    importlib.reload(bfu_asset_preview_ui)



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_asset_preview_operators.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_asset_preview_operators.unregister()
