# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List
import bpy
from .. import bbpl


def get_preset_values() -> List[str]:
    preset_values = [
        ]
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_export_process_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Export process")
    bpy.types.Scene.bfu_script_tool_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Copy Import Script")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_script_tool_expanded
    del bpy.types.Scene.bfu_export_process_properties_expanded