# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_export_filter_props
from . import bfu_export_filter_ui
from . import bfu_export_filter_utils

if "bfu_export_filter_props" in locals():
    importlib.reload(bfu_export_filter_props)
if "bfu_export_filter_ui" in locals():
    importlib.reload(bfu_export_filter_ui)
if "bfu_export_filter_utils" in locals():
    importlib.reload(bfu_export_filter_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_export_filter_props.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_export_filter_props.unregister()