# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import Set, Any
from .. import bbpl
from . import bfu_socket_utils
from .bfu_socket_types import SocketType

class BFU_OT_ConvertToStaticSocketButton(bpy.types.Operator):
    bl_label = "Convert to StaticMesh socket"
    bl_idname = "object.converttostaticsocket"
    bl_description = ("Convert selected Empty(s) to Unreal sockets ready for export (StaticMesh)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        ConvertedObj = bfu_socket_utils.convert_select_to_unrealengine_socket(SocketType.STATIC_SOCKET)
        if len(ConvertedObj) > 0:
            self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE Socket. (Static)")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active mesh object is the owner of the socket)")
        return {'FINISHED'}

class BFU_OT_ConvertToSkeletalSocketButton(bpy.types.Operator):
    bl_label = "Convert to SkeletalMesh socket"
    bl_idname = "object.converttoskeletalsocket"
    bl_description = ("Convert selected Empty(s) to Unreal sockets ready for export (SkeletalMesh)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        ConvertedObj = bfu_socket_utils.convert_select_to_unrealengine_socket(SocketType.SKELETAL_SOCKET)
        if len(ConvertedObj) > 0:
            self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE Socket. (Skeletal)")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active armature object is the owner of the socket)")
        return {'FINISHED'}

class BFU_OT_CopySkeletalSocketButton(bpy.types.Operator):
    bl_label = "Copy Skeletal Mesh Sockets for Unreal"
    bl_idname = "object.copy_skeletalsocket_command"
    bl_description = "Copy Skeletal Socket Script command"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        obj = context.object
        if obj:
            if obj.type == "ARMATURE":
                bbpl.basics.set_windows_clipboard(bfu_socket_utils.get_import_skeletal_mesh_socket_script_command(obj))
                self.report(
                    {'INFO'},
                    "Skeletal sockets copied. Paste in Unreal Engine Skeletal Mesh assets for import sockets. (Ctrl+V)")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ConvertToStaticSocketButton,
    BFU_OT_ConvertToSkeletalSocketButton,
    BFU_OT_CopySkeletalSocketButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

