# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_export_control_type
from . import bfu_export_control_property
from . import bfu_export_control_utils

if "bfu_export_control_type" in locals():
    importlib.reload(bfu_export_control_type)
if "bfu_export_control_property" in locals():
    importlib.reload(bfu_export_control_property)
if "bfu_export_control_utils" in locals():
    importlib.reload(bfu_export_control_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_export_control_property.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_export_control_property.unregister()