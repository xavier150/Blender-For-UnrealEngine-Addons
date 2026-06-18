# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_vertex_color_props
from . import bfu_vertex_color_ui
from . import bfu_vertex_color_utils

if "bfu_vertex_color_props" in locals():
    importlib.reload(bfu_vertex_color_props)
if "bfu_vertex_color_ui" in locals():
    importlib.reload(bfu_vertex_color_ui)
if "bfu_vertex_color_utils" in locals():
    importlib.reload(bfu_vertex_color_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_vertex_color_props.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_vertex_color_props.unregister()