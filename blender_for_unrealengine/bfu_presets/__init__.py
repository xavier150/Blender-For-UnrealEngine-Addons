# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import importlib

import bpy

from . import bfu_base_presets
from . import bfu_object_presets
from . import bfu_export_presets

if "bfu_base_presets" in locals():
    importlib.reload(bfu_base_presets)
if "bfu_object_presets" in locals():
    importlib.reload(bfu_object_presets)
if "bfu_export_presets" in locals():
    importlib.reload(bfu_export_presets)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_base_presets.register()
    bfu_object_presets.register()
    bfu_export_presets.register()

def unregister():
    bfu_export_presets.unregister()
    bfu_object_presets.unregister()
    bfu_base_presets.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)