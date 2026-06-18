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
from . import bfu_static_mesh_props
from . import bfu_static_mesh_ui
from . import bfu_static_mesh_utils
from . import bfu_static_mesh_type
from . import bfu_static_mesh_config
from . import bfu_export_static_mesh_package

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
if "bfu_static_mesh_props" in locals():
    importlib.reload(bfu_static_mesh_props)
if "bfu_static_mesh_ui" in locals():
    importlib.reload(bfu_static_mesh_ui)
if "bfu_static_mesh_utils" in locals():
    importlib.reload(bfu_static_mesh_utils)
if "bfu_static_mesh_type" in locals():
    importlib.reload(bfu_static_mesh_type)
if "bfu_static_mesh_config" in locals():
    importlib.reload(bfu_static_mesh_config)
if "bfu_export_static_mesh_package" in locals():
    importlib.reload(bfu_export_static_mesh_package)



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_export_procedure.register()
    bfu_static_mesh_props.register()
    bfu_static_mesh_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_static_mesh_type.unregister()
    bfu_static_mesh_props.unregister()
    bfu_export_procedure.unregister()