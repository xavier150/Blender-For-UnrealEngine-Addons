# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_base_obj_props
from . import bfu_base_obj_ui
from . import bfu_base_obj_utils

if "bfu_base_obj_props" in locals():
    importlib.reload(bfu_base_obj_props)
if "bfu_base_obj_ui" in locals():
    importlib.reload(bfu_base_obj_ui)
if "bfu_base_obj_utils" in locals():
    importlib.reload(bfu_base_obj_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_base_obj_props.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_base_obj_props.unregister()