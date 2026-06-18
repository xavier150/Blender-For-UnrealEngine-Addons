# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List
from enum import Enum

class SocketType(Enum):
    STATIC_SOCKET = "Static Socket"
    SKELETAL_SOCKET = "Skeletal Socket"

    def get_unreal_engine_prefix(self) -> str:


        if self.value == self.STATIC_SOCKET.value:
            return "SOCKET_" # Static Mesh Socket
        elif self.value == self.SKELETAL_SOCKET.value:
            return "SOCKET_" # Skeletal Mesh Socket
        else:
            raise ValueError(f"Unknown SocketType: {self.value}")

    @classmethod
    def get_prefix_list(cls) -> List[str]:
        return [member.get_unreal_engine_prefix() for member in cls]

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (

)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
