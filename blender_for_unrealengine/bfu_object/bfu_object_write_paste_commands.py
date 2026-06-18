# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import mathutils
import math
from typing import Tuple, List
from .. import bfu_utils

def get_object_location_for_unreal_script_command(obj: bpy.types.Object) -> Tuple[bool, str, str]:
    # Return (success, command)
    # If object location is mathutils.Vector((0.0, -6.0, 77.0)) 
    # Return a string like this:(X=0.000000,Y=600.000000,Z=7700.000000)

    scene = bpy.context.scene
    if not scene:
        return (False, "", "No active scene found.")

    unreal_location: mathutils.Vector = bfu_utils.get_object_location_vector_for_unreal(obj)
    command = f"Location=(X={unreal_location.x:.6f},Y={unreal_location.y:.6f},Z={unreal_location.z:.6f})"
    return (True, command, "Object location copied to clipboard for Unreal Engine.")
    
def get_object_rotation_for_unreal_script_command(obj: bpy.types.Object) -> Tuple[bool, str, str]:
    # Return (success, command)
    # If object rotation_euler is mathutils.Euler((0.0, 0.0, 0.0), 'XYZ') 
    # Return a string like this:(Pitch=0.000000,Yaw=0.000000,Roll=0.000000)

    scene = bpy.context.scene
    if not scene:
        return (False, "", "No active scene found.")

    unreal_rotation: mathutils.Euler = bfu_utils.get_object_euler_for_unreal(obj)
    array_rotation: List[float] = [math.degrees(unreal_rotation.x), math.degrees(unreal_rotation.y), math.degrees(unreal_rotation.z)]  # Roll, Pitch, Yaw: XYZ
    command = f"Rotation=(Pitch={array_rotation[0]:.6f},Yaw={array_rotation[1]:.6f},Roll={array_rotation[2]:.6f})"
    return (True, command, "Object rotation copied to clipboard for Unreal Engine.")

def get_object_scale_for_unreal_script_command(obj: bpy.types.Object) -> Tuple[bool, str, str]:
    # Return (success, command)
    # If object scale is mathutils.Vector((1.0, 1.0, 1.0)) 
    # Return a string like this:(X=1.000000,Y=1.000000,Z=1.000000)

    scene = bpy.context.scene
    if not scene:
        return (False, "", "No active scene found.")

    unreal_scale: mathutils.Vector = bfu_utils.get_object_scale_vector_for_unreal(obj)
    command = f"Scale=(X={unreal_scale.x:.6f},Y={unreal_scale.y:.6f},Z={unreal_scale.z:.6f})"
    return (True, command, "Object scale copied to clipboard for Unreal Engine.")