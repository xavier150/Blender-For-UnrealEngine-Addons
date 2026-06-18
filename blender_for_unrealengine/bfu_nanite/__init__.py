# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_nanite_props
from . import bfu_nanite_ui
from . import bfu_nanite_utils

if "bfu_nanite_props" in locals():
    importlib.reload(bfu_nanite_props)
if "bfu_nanite_ui" in locals():
    importlib.reload(bfu_nanite_ui)
if "bfu_nanite_utils" in locals():
    importlib.reload(bfu_nanite_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_nanite_props.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_nanite_props.unregister()