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

class CollisionShapeType(Enum):
    BOX = "Box"
    CAPSULE = "Capsule"
    SPHERE = "Sphere"
    CONVEX = "Convex"

    def get_unreal_engine_prefix(self) -> str:
        # Set the name of the Prefix depending on the type of collision in agreement with Unreal Engine pipeline.
        # FBX: https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine

        # Note: the collision prefix are also supported with the new interchange import pipeline in Unreal Engine and it the same prefix. 
        # So that work too with glTF files.
        # Interchange: https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-import-reference-in-unreal-engine

        if self.value == self.BOX.value:
            return "UBX_" # Box Collision
        elif self.value == self.CAPSULE.value:
            return "UCP_" # Capsule Collision
        elif self.value == self.SPHERE.value:
            return "USP_" # Sphere Collision
        elif self.value == self.CONVEX.value:
            return "UCX_" # Convex Collision
        else:
            raise ValueError(f"Unknown CollisionShapeType: {self.value}")
        
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
