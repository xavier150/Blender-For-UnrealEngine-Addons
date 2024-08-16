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

def get_predicted_skeleton_name(obj):
    # Get the predicted skeleton name in Unreal Engine
    scene = bpy.context.scene
    return scene.bfu_skeleton_prefix_export_name + bfu_utils.ValidUnrealAssetsName(obj.name) + "_Skeleton"

def get_predicted_skeleton_path(obj):
    scene = bpy.context.scene
    skeleton_path = os.path.join("/" + scene.bfu_unreal_import_module + "/", scene.bfu_unreal_import_location, obj.bfu_export_folder_name)
    skeleton_path = skeleton_path.replace('\\', '/')
    return skeleton_path

def get_predicted_skeleton_ref(obj):
    name = get_predicted_skeleton_name(obj)
    path = get_predicted_skeleton_path(obj)
    skeleton_ref = os.path.join(path, f"{name}.{name}")
    skeleton_ref = skeleton_ref.replace('\\', '/')
    return f"/Script/Engine.Skeleton'{skeleton_ref}'"

def get_predicted_skeleton_name(obj):
    # Get the predicted SkeletalMesh name in Unreal Engine
    scene = bpy.context.scene
    return scene.bfu_skeletal_mesh_prefix_export_name + bfu_utils.ValidUnrealAssetsName(obj.name)

def get_predicted_skeleton_path(obj):
    scene = bpy.context.scene
    skeleton_path = os.path.join("/" + scene.bfu_unreal_import_module + "/", scene.bfu_unreal_import_location, obj.bfu_export_folder_name)
    skeleton_path = skeleton_path.replace('\\', '/')
    return skeleton_path

def get_predicted_skeleton_ref(obj):
    name = get_predicted_skeleton_name(obj)
    path = get_predicted_skeleton_path(obj)
    skeleton_ref = os.path.join(path, f"{name}.{name}")
    skeleton_ref = skeleton_ref.replace('\\', '/')
    return f"/Script/Engine.Skeleton'{skeleton_ref}'"

def generate_name_for_unreal_engine(desired_name, current_name = ""):
    # Generate a new name with suffix number

    clean_desired_name = desired_name

    def is_valid_name(tested_name):
        tested_name_without_start = tested_name[len(clean_desired_name):]
        parts = tested_name_without_start.split("_")

        # Ensure the name has a suffix and the suffix is numeric
        if len(parts) == 1 or not parts[-1].isnumeric():
            return False
        
        # Special case for checking against the current name
        if current_name and tested_name == current_name:
            return True

        # Ensure no existing object uses this name
        for obj in bpy.context.scene.objects:
            if tested_name == obj.name:
                return False

        return True

    # Check if the desired name itself is valid and unique
    if is_valid_name(clean_desired_name):
        return clean_desired_name

    # Attempt to append a numeric suffix to make the name unique
    for num in range(10000):
        new_name = f"{clean_desired_name}_{num:02d}"  # Pads number with leading zeros
        if is_valid_name(new_name):
            return new_name

    raise ValueError("ERROR: No valid name found within the given constraints.")