# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import bpy
import bmesh
import string
import fnmatch
import mathutils
import math
import os
import math
from . import bbpl
from . import bps
from . import bfu_write_text
from . import bfu_basics
from . import bfu_utils

    
def get_collection_file_name(collection, desired_name="", fileType=".fbx"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_static_mesh_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_static_mesh_prefix_export_name+collection.name+fileType)
    
def get_camera_file_name(camera, desired_name="", fileType=".fbx"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if camera.bfu_use_custom_export_name:
        if camera.bfu_custom_export_name:
            return camera.bfu_custom_export_name
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_camera_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_camera_prefix_export_name+camera.name+fileType)

def get_spline_file_name(spline, desired_name="", fileType=".fbx"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if spline.bfu_use_custom_export_name:
        if spline.bfu_custom_export_name:
            return spline.bfu_custom_export_name
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_spline_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_spline_prefix_export_name+spline.name+fileType)
    
def get_static_mesh_file_name(object, desired_name="", fileType=".fbx"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if object.bfu_use_custom_export_name:
        if object.bfu_custom_export_name:
            return object.bfu_custom_export_name
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_static_mesh_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_static_mesh_prefix_export_name+object.name+fileType)

def get_skeletal_mesh_file_name(armature, desired_name="", fileType=".fbx"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if armature.bfu_use_custom_export_name:
        if armature.bfu_custom_export_name:
            return armature.bfu_custom_export_name
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_skeletal_mesh_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_skeletal_mesh_prefix_export_name+armature.name+fileType)

def get_alembic_file_name(object, desired_name="", fileType=".abc"):
    # Generate assset file name for skeletal mesh
    scene = bpy.context.scene
    if object.bfu_use_custom_export_name:
        if object.bfu_custom_export_name:
            return object.bfu_custom_export_name
    if desired_name:
        return bfu_basics.ValidFilename(scene.bfu_alembic_prefix_export_name+desired_name+fileType)
    return bfu_basics.ValidFilename(scene.bfu_alembic_prefix_export_name+object.name+fileType)

def get_animation_file_name(obj, action, fileType=".fbx"):
    # Generate action file name

    scene = bpy.context.scene
    if obj.bfu_anim_naming_type == "include_armature_name":
        ArmatureName = obj.name+"_"
    if obj.bfu_anim_naming_type == "action_name":
        ArmatureName = ""
    if obj.bfu_anim_naming_type == "include_custom_name":
        ArmatureName = obj.bfu_anim_naming_custom+"_"

    animType = bfu_utils.GetActionType(action)
    if animType == "NlAnim" or animType == "Action":
        # Nla can be exported as action
        return bfu_basics.ValidFilename(scene.bfu_anim_prefix_export_name+ArmatureName+action.name+fileType)

    elif animType == "Pose":
        return bfu_basics.ValidFilename(scene.bfu_pose_prefix_export_name+ArmatureName+action.name+fileType)

    else:
        return None


def get_nonlinear_animation_file_name(obj, fileType=".fbx"):
    # Generate action file name

    scene = bpy.context.scene
    if obj.bfu_anim_naming_type == "include_armature_name":
        ArmatureName = obj.name+"_"
    if obj.bfu_anim_naming_type == "action_name":
        ArmatureName = ""
    if obj.bfu_anim_naming_type == "include_custom_name":
        ArmatureName = obj.bfu_anim_naming_custom+"_"

    return bfu_basics.ValidFilename(scene.bfu_anim_prefix_export_name+ArmatureName+obj.bfu_anim_nla_export_name+fileType)
