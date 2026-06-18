# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_asset_manager_type
from . import bfu_asset_manager_ui
from . import bfu_asset_manager_utils
from . import bfu_asset_manager_registred_assets

if "bfu_asset_manager_type" in locals():
    importlib.reload(bfu_asset_manager_type)
if "bfu_asset_manager_ui" in locals():
    importlib.reload(bfu_asset_manager_ui)
if "bfu_asset_manager_utils" in locals():
    importlib.reload(bfu_asset_manager_utils)
if "bfu_asset_manager_registred_assets" in locals():
    importlib.reload(bfu_asset_manager_registred_assets)




classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
