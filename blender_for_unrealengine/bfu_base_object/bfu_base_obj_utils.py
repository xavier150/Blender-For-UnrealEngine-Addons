# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from pathlib import Path
from .. import bfu_export_control
from .. import bfu_basics
from .. import bfu_export_nomenclature
from . import bfu_base_obj_props

def in_hidden_collection(obj: bpy.types.Object) -> bool:
    # When link an object some object may follow the link and be placed in a collection named "OVERRIDE_HIDDEN"
    # Most of the case the is hidden object that should not be exported with the linked collection.
    # So I don't export them.
    for coll in obj.users_collection:
        if coll.name == "OVERRIDE_HIDDEN":
            # Print for debug only:
            # print(f"Object {obj.name} is in collection {coll.name} and will not be exported.")
            return True
    return False

def check_valid_object(obj: bpy.types.Object) -> bool:
    if in_hidden_collection(obj):
        return False
    return True

def get_recursive_obj_childs(obj: bpy.types.Object) -> List[bpy.types.Object]:
    # Get all recursive childs of a object
    # include_self is True obj is index 0
    scene = bpy.context.scene
    if scene is None:
        return []
    
    view_layer = bpy.context.view_layer
    if view_layer is None:
        return []
    

    scene_objects = scene.objects

    save_objects: List[bpy.types.Object] = []

    # Get all direct childs of a object
    def get_obj_childs(obj: bpy.types.Object) -> List[bpy.types.Object]:
        # Get all direct childs of a object
        
        childs_obj: List[bpy.types.Object] = []
        for child_obj in scene_objects:
            if child_obj.name in view_layer.objects:
                # Export only objects that are not library linked.
                # Still work on overridden objects.
                if bfu_export_control.bfu_export_control_utils.is_auto_or_export_recursive(child_obj):
                    if check_valid_object(child_obj):
                        if child_obj.library is None:  # type: ignore
                            if child_obj.parent is not None:
                                if child_obj.parent.name == obj.name:
                                    childs_obj.append(child_obj)

        return childs_obj

    for newobj in get_obj_childs(obj):
        for childs in get_recursive_obj_childs(newobj):
            if check_valid_object(childs):
                save_objects.append(childs)
        if check_valid_object(newobj):
            save_objects.append(newobj)
    return save_objects

def get_exportable_objects(obj: bpy.types.Object) -> List[bpy.types.Object]:
    # Found all exportable children of the object
    # Include the object itself

    desired_obj_list: List[bpy.types.Object] = [obj]
    desired_obj_list.extend(get_recursive_obj_childs(obj))
    return desired_obj_list

def get_obj_import_location(obj: bpy.types.Object) -> Path:
    """Get the path to import an object into Unreal Engine."""
    
    export_folder_name = bfu_base_obj_props.get_object_export_folder_name(obj)
    return bfu_export_nomenclature.bfu_export_nomenclature_utils.get_import_location() / bfu_basics.valid_folder_name(export_folder_name)

def get_obj_export_folder(obj: bpy.types.Object) -> str:
    """Get the export folder name for an object."""
    
    export_folder_name = bfu_base_obj_props.get_object_export_folder_name(obj)
    return bfu_basics.valid_folder_name(export_folder_name)

