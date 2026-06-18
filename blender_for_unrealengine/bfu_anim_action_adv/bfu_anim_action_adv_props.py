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
        'obj.bfu_move_action_to_center_for_export',
        'obj.bfu_rotate_action_to_zero_for_export',
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

    bpy.types.Scene.bfu_animation_action_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions Advanced Properties")

    bpy.types.Object.bfu_move_action_to_center_for_export = bpy.props.BoolProperty(
        name="Move animation to center",
        description=(
            "(Action animation only) If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)" +
            " Note: Unreal Engine ignore the position of the skeleton at the import."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_action_to_zero_for_export = bpy.props.BoolProperty(
        name="Rotate Action to zero",
        description=(
            "(Action animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_rotate_action_to_zero_for_export
    del bpy.types.Object.bfu_move_action_to_center_for_export

    del bpy.types.Scene.bfu_animation_action_advanced_properties_expanded