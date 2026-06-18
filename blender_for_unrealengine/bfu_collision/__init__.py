# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_collision_operator
from . import bfu_collision_props
from . import bfu_collision_types
from . import bfu_collision_ui
from . import bfu_collision_utils
from . import bfu_collision_mesh_shape
from . import shape_algorithms

if "bfu_collision_operator" in locals():
    importlib.reload(bfu_collision_operator)
if "bfu_collision_types" in locals():
    importlib.reload(bfu_collision_types)
if "bfu_collision_props" in locals():
    importlib.reload(bfu_collision_props)
if "bfu_collision_ui" in locals():
    importlib.reload(bfu_collision_ui)
if "bfu_collision_utils" in locals():
    importlib.reload(bfu_collision_utils)
if "bfu_collision_mesh_shape" in locals():
    importlib.reload(bfu_collision_mesh_shape)
if "shape_algorithms" in locals():
    importlib.reload(shape_algorithms)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_collision_operator.register()
    bfu_collision_types.register()
    bfu_collision_props.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_collision_props.unregister()
    bfu_collision_types.unregister()
    bfu_collision_operator.unregister()