# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_object_props
from . import bfu_object_operators
from . import bfu_object_ui
from . import bfu_object_utils
from . import bfu_object_write_paste_commands

if "bfu_object_props" in locals():
    importlib.reload(bfu_object_props)
if "bfu_object_operators" in locals():
    importlib.reload(bfu_object_operators)
if "bfu_object_ui" in locals():
    importlib.reload(bfu_object_ui)
if "bfu_object_utils" in locals():
    importlib.reload(bfu_object_utils)
if "bfu_object_write_paste_commands" in locals():
    importlib.reload(bfu_object_write_paste_commands)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_object_props.register()
    bfu_object_operators.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_object_operators.unregister()
    bfu_object_props.unregister()