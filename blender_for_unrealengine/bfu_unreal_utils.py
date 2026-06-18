# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import os
import bpy
from . import bfu_utils
from . import bfu_export_nomenclature
from . import bfu_base_object

def get_predicted_skeleton_name(obj: bpy.types.Object) -> str:
    # Get the predicted skeleton name in Unreal Engine
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    return bfu_export_nomenclature.bfu_export_nomenclature_props.get_skeleton_prefix_export_name(scene) + bfu_utils.clean_filename_for_unreal(obj.name) + "_Skeleton"

def get_predicted_skeleton_path(obj: bpy.types.Object) -> str:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
    unreal_import_location = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_location(scene)
    export_folder_name = bfu_base_object.bfu_base_obj_props.get_object_export_folder_name(obj)

    ref_path = os.path.join("/" + unreal_import_module + "/", unreal_import_location, export_folder_name)
    ref_path = ref_path.replace('\\', '/')
    return ref_path

def get_predicted_skeleton_ref(obj: bpy.types.Object) -> str:
    name = get_predicted_skeleton_name(obj)
    path = get_predicted_skeleton_path(obj)
    ref_path = os.path.join(path, f"{name}.{name}")
    ref_path = ref_path.replace('\\', '/')
    return f"/Script/Engine.Skeleton'{ref_path}'"

def get_predicted_skeletal_mesh_name(obj: bpy.types.Object) -> str:
    # Get the predicted SkeletalMesh name in Unreal Engine
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    
    return bfu_export_nomenclature.bfu_export_nomenclature_props.get_skeletal_mesh_prefix_export_name(scene) + bfu_utils.clean_filename_for_unreal(obj.name)

def get_predicted_skeletal_mesh_path(obj: bpy.types.Object) -> str:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
    unreal_import_location = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_location(scene)
    export_folder_name = bfu_base_object.bfu_base_obj_props.get_object_export_folder_name(obj)

    ref_path = os.path.join("/" + unreal_import_module + "/", unreal_import_location, export_folder_name)
    ref_path = ref_path.replace('\\', '/')
    return ref_path

def get_predicted_skeletal_mesh_ref(obj: bpy.types.Object) -> str:
    name = get_predicted_skeletal_mesh_name(obj)
    path = get_predicted_skeletal_mesh_path(obj)
    ref_path = os.path.join(path, f"{name}.{name}")
    ref_path = ref_path.replace('\\', '/')
    return f"/Script/Engine.SkeletalMesh'{ref_path}'"

def generate_name_for_unreal_engine(desired_name: str, current_name: str = "") -> str:
    # Generate a new name with suffix number

    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    clean_desired_name = desired_name

    # Create a set of existing names once (O(n) instead of O(n*m))
    existing_names = {obj.name for obj in scene.objects}

    # Check if desired name is already available
    if clean_desired_name not in existing_names or clean_desired_name == current_name:
        return clean_desired_name

    # Append numeric suffix until finding a unique name
    for num in range(10000):
        new_name = f"{clean_desired_name}_{num:02d}"  # Pads number with leading zeros
        
        if new_name not in existing_names or new_name == current_name:
            return new_name

    raise ValueError("ERROR: No valid name found within the given constraints.")
