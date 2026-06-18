# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List
from .bfu_modular_skeletal_mesh_type import BFU_UI_ModularSkeletalSpecifiedPartsMeshs, BFU_UI_ModularSkeletalSpecifiedPartsMeshItem
from .. import bfu_export_control

def get_modular_skeletal_specified_parts_meshs_template(obj: bpy.types.Object) -> BFU_UI_ModularSkeletalSpecifiedPartsMeshs:
    return obj.bfu_modular_skeletal_specified_parts_meshs_template  # type: ignore[attr-defined]

def get_modular_objects_from_part(part: BFU_UI_ModularSkeletalSpecifiedPartsMeshItem) -> List[bpy.types.Object]:
    objects: List[bpy.types.Object] = []
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found in the current Blender context.")
    

    for skeletal_part in part.skeletal_parts.get_template_collection():
        if skeletal_part.enabled:

            if skeletal_part.target_type == 'OBJECT':
                # Object target
                if skeletal_part.obj:
                    if bfu_export_control.bfu_export_control_utils.is_auto_or_export_recursive(skeletal_part.obj):
                        if skeletal_part.obj.library is None: # type: ignore
                            objects.append(skeletal_part.obj)
                        else:
                            # When the object come from a linked library, get the scene reference
                            scene_obj = scene.objects.get(skeletal_part.obj.name)
                            if scene_obj:
                                objects.append(scene_obj)

            elif skeletal_part.target_type == 'COLLECTION':
                # Objects from collection target
                if skeletal_part.collection:
                    for collection_obj in skeletal_part.collection.objects:
                        if bfu_export_control.bfu_export_control_utils.is_auto_or_export_recursive(collection_obj):
                            if collection_obj.library is None: # type: ignore
                                objects.append(collection_obj)
                            else:
                                # When the object come from a linked library, get the scene reference
                                scene_obj = scene.objects.get(collection_obj.name)
                                if scene_obj:
                                    objects.append(scene_obj)
    return objects

def modular_mode_is_all_in_one(obj: bpy.types.Object) -> bool:
    return obj.bfu_modular_skeletal_mesh_mode == 'all_in_one'  # type: ignore[attr-defined]

def modular_mode_is_every_meshs(obj: bpy.types.Object) -> bool:
    return obj.bfu_modular_skeletal_mesh_mode == 'every_meshs'  # type: ignore[attr-defined]

def modular_mode_is_specified_parts(obj: bpy.types.Object) -> bool:
    return obj.bfu_modular_skeletal_mesh_mode == 'specified_parts'  # type: ignore[attr-defined]