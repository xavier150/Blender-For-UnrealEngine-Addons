# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from . import bfu_export_control_property
from .bfu_export_control_type import BFU_ExportTypeEnum



def get_object_export_type(obj: bpy.types.Object) -> BFU_ExportTypeEnum:
    for export_type in BFU_ExportTypeEnum:
        if obj.bfu_export_type == export_type.value:  # type: ignore
            return export_type
        
    print(f"Warning: Object '{obj.name}' has an invalid export type '{obj.bfu_export_type}'. Using default export type.")  # type: ignore
    return BFU_ExportTypeEnum.default()

# Direct Type Check functions

def is_auto(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to auto export.
    """
    return get_object_export_type(obj).is_auto()

def is_not_auto(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to auto export.
    """
    return not is_auto(obj)

def is_export_self_only(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to export self.
    """
    return get_object_export_type(obj).is_export_self_only()

def is_not_export_self_only(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to export self.
    """
    return not is_export_self_only(obj)

def is_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to export recursively.
    """
    return get_object_export_type(obj).is_export_recursive()

def is_not_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to export recursively.
    """
    return not is_export_recursive(obj)

def is_dont_export(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to not export.
    """
    return get_object_export_type(obj).is_dont_export()

def is_not_dont_export(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to not export.
    """
    return not is_dont_export(obj)

# Type Check functions

def is_export_self(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to export self or export recursively.
    """
    return get_object_export_type(obj).is_export_self()

def is_not_export_self(obj: bpy.types.Object) -> bool:
    """
    Check if the object is not set to export self or export recursively.
    """
    return not is_export_self(obj)

def is_auto_or_export_recursive(obj: bpy.types.Object) -> bool:
    """
    Check if the object is set to auto or export recursively.
    """
    return get_object_export_type(obj).is_auto() or get_object_export_type(obj).is_export_recursive()

# Set functions

def set_auto(obj: bpy.types.Object) -> None:
    """
    Set the object to auto export.
    """
    bfu_export_control_property.set_object_export_type(obj, BFU_ExportTypeEnum.AUTO)

# Objects getters
def get_all_export_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if bfu_export_control_property.get_object_export_type(obj).is_export_self():
            found_objects.append(obj)
    return found_objects

def get_all_export_armatures(scene: bpy.types.Scene) ->  List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if isinstance(obj.data, bpy.types.Armature):
            if bfu_export_control_property.get_object_export_type(obj).is_export_self():
                found_objects.append(obj)
    return found_objects

def get_all_selected_export_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if obj.select_get():
            if bfu_export_control_property.get_object_export_type(obj).is_export_self():
                found_objects.append(obj)
    return found_objects

def get_all_export_recursive_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if bfu_export_control_property.get_object_export_type(obj).is_export_recursive():
            found_objects.append(obj)
    return found_objects

def get_all_export_recursive_armatures(scene: bpy.types.Scene) ->  List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if isinstance(obj.data, bpy.types.Armature):
            if bfu_export_control_property.get_object_export_type(obj).is_export_recursive():
                found_objects.append(obj)
    return found_objects

def get_all_selected_export_recursive_objects(scene: bpy.types.Scene) -> List[bpy.types.Object]:
    found_objects: List[bpy.types.Object] = []
    for obj in scene.objects:
        if obj.select_get():
            if bfu_export_control_property.get_object_export_type(obj).is_export_recursive():
                found_objects.append(obj)
    return found_objects

