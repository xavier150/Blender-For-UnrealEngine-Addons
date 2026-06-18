# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy

from ... import bbpl


def get_tools_presets_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_tools_presets_properties_expanded.is_expanded()  # type: ignore



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_tools_presets_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Presets")  # type: ignore[attr-defined]


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_tools_presets_properties_expanded  # type: ignore[attr-defined]