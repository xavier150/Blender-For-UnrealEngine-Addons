# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_custom_property_props
from . import bfu_custom_property_ui

if "bfu_custom_property_props" in locals():
    importlib.reload(bfu_custom_property_props)
if "bfu_custom_property_ui" in locals():
    importlib.reload(bfu_custom_property_ui)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_custom_property_props.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_custom_property_props.unregister()