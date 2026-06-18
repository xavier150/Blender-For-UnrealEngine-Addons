# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_asset_export_logs_types
from . import bfu_asset_export_logs_utils
from . import bfu_process_time_logs_types
from . import bfu_process_time_logs_utils

if "bfu_asset_export_logs_types" in locals():
    importlib.reload(bfu_asset_export_logs_types)
if "bfu_asset_export_logs_utils" in locals():
    importlib.reload(bfu_asset_export_logs_utils)
if "bfu_process_time_logs_types" in locals():
    importlib.reload(bfu_process_time_logs_types)
if "bfu_process_time_logs_utils" in locals():
    importlib.reload(bfu_process_time_logs_utils)


def clear_all_logs():
    bfu_process_time_logs_utils.clear_process_time_logs()

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_asset_export_logs_types.register()
    bfu_process_time_logs_types.register()

def unregister():
    bfu_process_time_logs_types.unregister()
    bfu_asset_export_logs_types.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

