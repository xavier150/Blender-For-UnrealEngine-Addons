# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_export_procedure
from . import bfu_base_col_props
from . import bfu_base_col_ui
from . import bfu_base_col_utils
from . import bfu_base_col_type

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
if "bfu_base_col_props" in locals():
    importlib.reload(bfu_base_col_props)
if "bfu_base_col_ui" in locals():
    importlib.reload(bfu_base_col_ui)
if "bfu_base_col_utils" in locals():
    importlib.reload(bfu_base_col_utils)
if "bfu_base_col_type" in locals():
    importlib.reload(bfu_base_col_type)
classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_export_procedure.register()
    bfu_base_col_props.register()
    bfu_base_col_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_base_col_type.unregister()
    bfu_base_col_props.unregister()
    bfu_export_procedure.unregister()