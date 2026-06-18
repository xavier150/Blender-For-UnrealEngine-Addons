# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_modular_skeletal_mesh_props
from . import bfu_modular_skeletal_mesh_type
from . import bfu_modular_skeletal_mesh_ui
from . import bfu_modular_skeletal_mesh_utils


if "bfu_modular_skeletal_mesh_props" in locals():
    importlib.reload(bfu_modular_skeletal_mesh_props)
if "bfu_modular_skeletal_mesh_ui" in locals():
    importlib.reload(bfu_modular_skeletal_mesh_ui)
if "bfu_modular_skeletal_mesh_utils" in locals():
    importlib.reload(bfu_modular_skeletal_mesh_utils)
if "bfu_modular_skeletal_mesh_type" in locals():
    importlib.reload(bfu_modular_skeletal_mesh_type)


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_modular_skeletal_mesh_props.register()
    bfu_modular_skeletal_mesh_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_modular_skeletal_mesh_type.unregister()
    bfu_modular_skeletal_mesh_props.unregister()