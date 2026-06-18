# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_socket_operator
from . import bfu_socket_props
from . import bfu_socket_types
from . import bfu_socket_ui
from . import bfu_socket_utils

if "bfu_socket_operator" in locals():
    importlib.reload(bfu_socket_operator)
if "bfu_socket_props" in locals():
    importlib.reload(bfu_socket_props)
if "bfu_socket_types" in locals():
    importlib.reload(bfu_socket_types)
if "bfu_socket_ui" in locals():
    importlib.reload(bfu_socket_ui)
if "bfu_socket_utils" in locals():
    importlib.reload(bfu_socket_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_socket_operator.register()
    bfu_socket_props.register()
    bfu_socket_types.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_socket_types.unregister()
    bfu_socket_props.unregister()
    bfu_socket_operator.unregister()