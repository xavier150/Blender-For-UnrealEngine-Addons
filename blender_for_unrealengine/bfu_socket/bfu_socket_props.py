# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from .. import bbpl


def get_scene_socket_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_tools_socket_properties_expanded.is_expanded() # type: ignore

def get_object_use_socket_custom_name(obj: bpy.types.Object) -> bool:
    return obj.bfu_use_socket_custom_name # type: ignore

def get_object_socket_custom_name(obj: bpy.types.Object) -> str:
    return obj.bfu_socket_custom_name # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_tools_socket_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Socket")  # type: ignore

    bpy.types.Object.bfu_use_socket_custom_name = bpy.props.BoolProperty(  # type: ignore
        name="Socket custom name",
        description='Use a custom name in Unreal Engine for this socket?',
        default=False
        )

    bpy.types.Object.bfu_socket_custom_name = bpy.props.StringProperty(  # type: ignore
        name="",
        description='',
        default="MySocket"
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_socket_custom_name # type: ignore
    del bpy.types.Object.bfu_use_socket_custom_name # type: ignore

    del bpy.types.Scene.bfu_tools_socket_properties_expanded # type: ignore