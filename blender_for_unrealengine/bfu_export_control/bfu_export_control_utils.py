# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from .bfu_export_control_type import BFU_ExportTypeEnum



def get_object_export_type(obj: bpy.types.Object) -> BFU_ExportTypeEnum:
    for export_type in BFU_ExportTypeEnum:
        if obj.bfu_export_type == export_type.value:  # type: ignore
            return export_type
        
    print(f"Warning: Object '{obj.name}' has an invalid export type '{obj.bfu_export_type}'. Using default export type.")  # type: ignore
    return BFU_ExportTypeEnum.default()

# Check functions

def is_auto(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to auto export.
    """
    return get_object_export_type(obj) == BFU_ExportTypeEnum.AUTO

def is_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to export recursively.
    """
    return get_object_export_type(obj) == BFU_ExportTypeEnum.EXPORT_RECURSIVE

def is_not_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to export recursively.
    """
    return get_object_export_type(obj) != BFU_ExportTypeEnum.EXPORT_RECURSIVE

def is_auto_or_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to auto or export recursively.
    """
    return get_object_export_type(obj) in (BFU_ExportTypeEnum.AUTO, BFU_ExportTypeEnum.EXPORT_RECURSIVE)

# Set functions

def set_auto(obj: bpy.types.Object) -> None:
    """
    Set the object to auto export.
    """
    obj.bfu_export_type = BFU_ExportTypeEnum.AUTO.value  # type: ignore

# Objects getters

def get_all_export_recursive_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if obj.bfu_export_type == BFU_ExportTypeEnum.EXPORT_RECURSIVE.value:  # type: ignore
            found_objects.append(obj)
    return found_objects

def get_all_export_recursive_armatures(scene: bpy.types.Scene) ->  List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if isinstance(obj.data, bpy.types.Armature):
            if obj.bfu_export_type == BFU_ExportTypeEnum.EXPORT_RECURSIVE.value:  # type: ignore
                found_objects.append(obj)
    return found_objects

def get_all_selected_export_recursive_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if obj.select_get():
            if obj.bfu_export_type == BFU_ExportTypeEnum.EXPORT_RECURSIVE.value:  # type: ignore
                found_objects.append(obj)
    return found_objects

