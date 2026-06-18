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
from . import bfu_camera_props
from . import bfu_camera_operators
from . import bfu_camera_ui
from . import bfu_camera_utils
from . import bfu_camera_unreal_utils
from . import bfu_camera_data
from . import bfu_camera_write_text
from . import bfu_camera_write_paste_commands
from . import bfu_camera_type
from . import bfu_camera_config
from . import bfu_export_camera_package

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
if "bfu_camera_props" in locals():
    importlib.reload(bfu_camera_props)
if "bfu_camera_ui" in locals():
    importlib.reload(bfu_camera_ui)
if "bfu_camera_utils" in locals():
    importlib.reload(bfu_camera_utils)
if "bfu_camera_unreal_utils" in locals():
    importlib.reload(bfu_camera_unreal_utils)
if "bfu_camera_data" in locals():
    importlib.reload(bfu_camera_data)
if "bfu_camera_write_text" in locals():
    importlib.reload(bfu_camera_write_text)
if "bfu_camera_write_paste_commands" in locals():
    importlib.reload(bfu_camera_write_paste_commands)
if "bfu_camera_type" in locals():
    importlib.reload(bfu_camera_type)
if "bfu_camera_config" in locals():
    importlib.reload(bfu_camera_config)
if "bfu_export_camera_package" in locals():
    importlib.reload(bfu_export_camera_package)


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    bfu_export_procedure.register()
    bfu_camera_props.register()
    bfu_camera_operators.register()
    bfu_camera_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    bfu_camera_type.unregister()
    bfu_camera_operators.unregister()
    bfu_camera_props.unregister()
    bfu_export_procedure.unregister()