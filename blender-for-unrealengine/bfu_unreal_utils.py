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

import os
import bpy
from . import bbpl
from . import bps
from . import bfu_basics
from . import bfu_utils

def GetPredictedSkeletonName(obj):
    # Get the predicted skeleton name in Unreal Engine
    scene = bpy.context.scene
    return scene.bfu_skeleton_prefix_export_name + bfu_utils.ValidUnrealAssetsName(obj.name) + "_Skeleton"

def GetPredictedSkeletonPath(obj):
    scene = bpy.context.scene
    skeleton_path = os.path.join("/" + scene.bfu_unreal_import_module + "/", scene.bfu_unreal_import_location, obj.bfu_export_folder_name)
    skeleton_path = skeleton_path.replace('\\', '/')
    return skeleton_path

def GetPredictedSkeletonRef(obj):
    name = GetPredictedSkeletonName(obj)
    path = GetPredictedSkeletonPath(obj)
    skeleton_ref = os.path.join(path, name + "." + name)
    skeleton_ref = skeleton_ref.replace('\\', '/')
    return "/Script/Engine.Skeleton'" + skeleton_ref + "'"

def GetPredictedSkeletalMeshName(obj):
    # Get the predicted SkeletalMesh name in Unreal Engine
    scene = bpy.context.scene
    return scene.bfu_skeletal_mesh_prefix_export_name + bfu_utils.ValidUnrealAssetsName(obj.name)

def GetPredictedSkeletalMeshPath(obj):
    scene = bpy.context.scene
    skeleton_path = os.path.join("/" + scene.bfu_unreal_import_module + "/", scene.bfu_unreal_import_location, obj.bfu_export_folder_name)
    skeleton_path = skeleton_path.replace('\\', '/')
    return skeleton_path

def GetPredictedSkeletalMeshRef(obj):
    name = GetPredictedSkeletalMeshName(obj)
    path = GetPredictedSkeletalMeshPath(obj)
    skeletal_mesh_ref = os.path.join(path, name + "." + name)
    skeletal_mesh_ref = skeletal_mesh_ref.replace('\\', '/')
    return "/Script/Engine.SkeletalMesh'" + skeletal_mesh_ref + "'"