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
from . import bfu_spline_props
from . import bfu_spline_ui
from . import bfu_spline_utils
from . import bfu_spline_unreal_utils
from . import bfu_spline_data
from . import bfu_spline_write_text
from . import bfu_spline_write_paste_commands
from . import bfu_spline_type
from . import bfu_export_spline_package

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
if "bfu_spline_props" in locals():
    importlib.reload(bfu_spline_props)
if "bfu_spline_ui" in locals():
    importlib.reload(bfu_spline_ui)
if "bfu_spline_utils" in locals():
    importlib.reload(bfu_spline_utils)
if "bfu_spline_unreal_utils" in locals():
    importlib.reload(bfu_spline_unreal_utils)
if "bfu_spline_data" in locals():
    importlib.reload(bfu_spline_data)
if "bfu_spline_write_text" in locals():
    importlib.reload(bfu_spline_write_text)
if "bfu_spline_write_paste_commands" in locals():
    importlib.reload(bfu_spline_write_paste_commands)
if "bfu_spline_type" in locals():
    importlib.reload(bfu_spline_type)
if "bfu_export_spline_package" in locals():
    importlib.reload(bfu_export_spline_package)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_export_procedure.register()
    bfu_spline_props.register()
    bfu_spline_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_spline_type.unregister()
    bfu_spline_props.unregister()
    bfu_export_procedure.unregister()