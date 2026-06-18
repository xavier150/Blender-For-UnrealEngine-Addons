# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_presets_props
from . import bfu_presets_operator
from . import bfu_presets_ui
from . import bfu_presets_utils

if "bfu_presets_props" in locals():
    importlib.reload(bfu_presets_props)
if "bfu_presets_operator" in locals():
    importlib.reload(bfu_presets_operator)
if "bfu_presets_ui" in locals():
    importlib.reload(bfu_presets_ui)
if "bfu_presets_utils" in locals():
    importlib.reload(bfu_presets_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_presets_props.register()
    bfu_presets_operator.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_presets_operator.unregister()
    bfu_presets_props.unregister()