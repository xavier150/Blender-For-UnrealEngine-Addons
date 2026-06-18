# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_check_types
from . import bfu_check_props
from . import bfu_check_operators
from . import bfu_check_ui
from . import bfu_check_utils
from . import bfu_check_list

if "bfu_check_types" in locals():
    importlib.reload(bfu_check_types)
if "bfu_check_props" in locals():
    importlib.reload(bfu_check_props)
if "bfu_check_operators" in locals():
    importlib.reload(bfu_check_operators)
if "bfu_check_ui" in locals():
    importlib.reload(bfu_check_ui)
if "bfu_check_utils" in locals():
    importlib.reload(bfu_check_utils)
if "bfu_check_list" in locals():
    importlib.reload(bfu_check_list)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_check_types.register()
    bfu_check_props.register()
    bfu_check_operators.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_check_operators.unregister()
    bfu_check_props.unregister()
    bfu_check_types.unregister()