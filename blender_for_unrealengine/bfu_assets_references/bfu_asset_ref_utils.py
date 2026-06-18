# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import os
from .. import bfu_unreal_utils
from .. import bfu_utils
from .. import bfu_assets_references
from ..bfu_assets_references.bfu_asset_ref_props import BFU_EngineRefSkeletalMeshSearchModeEnum, BFU_EngineRefSkeletonSearchModeEnum
from .. import bfu_export_nomenclature
from .. import bfu_base_object

def get_skeleton_search_ref(obj: bpy.types.Object) -> str:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found.")
   
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.AUTO.value:
        return bfu_unreal_utils.get_predicted_skeleton_ref(obj)

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_NAME.value:
        name = bfu_utils.clean_filename_for_unreal(bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_custom_name(obj))
        unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
        unreal_import_location = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_location(scene)
        export_folder_name = bfu_base_object.bfu_base_obj_props.get_object_export_folder_name(obj)
        target_ref = os.path.join("/" + unreal_import_module + "/", unreal_import_location, export_folder_name, name+"."+name)
        target_ref = target_ref.replace('\\', '/')
        return target_ref

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_PATH_NAME.value:
        name = bfu_utils.clean_filename_for_unreal(bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_custom_name(obj))
        unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
        engine_ref_skeleton_custom_path = bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_custom_path(obj)
        target_ref = os.path.join("/" + unreal_import_module + "/", engine_ref_skeleton_custom_path, name+"."+name)
        target_ref = target_ref.replace('\\', '/')
        return target_ref

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_search_mode(obj).value == BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_REFERENCE.value:
        target_ref = bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeleton_custom_ref(obj).replace('\\', '/')
        return target_ref
    else:
        raise ValueError(f"Unknown skeleton search mode for object '{obj.name}'")

def get_skeletal_mesh_search_ref(obj: bpy.types.Object):
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found.")
   
    if bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.AUTO.value:
        return bfu_unreal_utils.get_predicted_skeletal_mesh_ref(obj)

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_NAME.value:
        name = bfu_utils.clean_filename_for_unreal(bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_custom_name(obj))
        unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
        unreal_import_location = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_location(scene)
        engine_ref_skeleton_custom_path = bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_custom_path(obj)
        target_ref = os.path.join("/" + unreal_import_module + "/", unreal_import_location, engine_ref_skeleton_custom_path, name+"."+name)
        target_ref = target_ref.replace('\\', '/')
        return target_ref

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_PATH_NAME.value:
        name = bfu_utils.clean_filename_for_unreal(bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_custom_name(obj))
        unreal_import_module = bfu_export_nomenclature.bfu_export_nomenclature_props.get_unreal_import_module(scene)
        engine_ref_skeleton_custom_path = bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_custom_path(obj)
        target_ref = os.path.join("/" + unreal_import_module + "/", engine_ref_skeleton_custom_path, name+"."+name)
        target_ref = target_ref.replace('\\', '/')
        return target_ref

    elif bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_search_mode(obj).value == BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_REFERENCE.value:
        target_ref = bfu_assets_references.bfu_asset_ref_props.get_object_engine_ref_skeletal_mesh_custom_ref(obj).replace('\\', '/')
        return target_ref
    else:
        raise ValueError(f"Unknown skeletal mesh search mode for object '{obj.name}'")
