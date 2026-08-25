# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Dict, Any
import unreal
from .. import import_module_tasks_class
from .. import import_module_utils
from ..asset_types import ExportAssetType

def apply_import_settings(itask: import_module_tasks_class.ImportTask, asset_data: Dict[str, Any], asset_additional_data: Dict[str, Any]) -> None:
    import_module_utils.print_debug_step("Set Nanite import settings.")

    asset_type = ExportAssetType.get_asset_type_from_string(asset_data.get("asset_type"))
    if asset_type not in [ExportAssetType.STATIC_MESH, ExportAssetType.SKELETAL_MESH]:
        # Only apply settings for StaticMesh and SkeletalMesh
        return
    
    if "build_nanite" in asset_additional_data:
        build_nanite = asset_additional_data["build_nanite"]

        if isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
            if asset_type.value == ExportAssetType.STATIC_MESH.value:
                if "build_nanite" in asset_additional_data:
                    itask.get_igap_mesh().set_editor_property('build_nanite', build_nanite)
            if asset_type.value == ExportAssetType.SKELETAL_MESH.value:
                if "build_nanite" in asset_additional_data:
                    # Unreal Engine 5.5 support Nanite with Skeletal Mesh
                    # but that was not yet added in Python API.
                    pass
                    #itask.get_igap_mesh().set_editor_property('build_nanite', build_nanite)
        else:
            if asset_type.value == ExportAssetType.STATIC_MESH.value:
                if "build_nanite" in asset_additional_data:
                    itask.get_static_mesh_import_data().set_editor_property('build_nanite', build_nanite)
            if asset_type.value == ExportAssetType.SKELETAL_MESH.value:
                if "build_nanite" in asset_additional_data:
                    # Unreal Engine 5.5 support Nanite with Skeletal Mesh
                    # but that was not yet added in Python API.
                    pass
                    #itask.get_static_mesh_import_data().set_editor_property('build_nanite', build_nanite)


def apply_asset_settings(itask: import_module_tasks_class.ImportTask, asset_additional_data: Dict[str, Any]) -> None:
    import_module_utils.print_debug_step("Set Nanite post import settings.")

    # Check   
    static_mesh = itask.get_imported_static_mesh()
    skeletal_mesh = itask.get_imported_skeletal_mesh()

    # Loop for static and skeletal meshs
    for asset in [static_mesh, skeletal_mesh]:
        if asset:
            apply_one_asset_settings(itask, asset, asset_additional_data)


def apply_one_asset_settings(itask: import_module_tasks_class.ImportTask, asset: unreal.Object, asset_additional_data: Dict[str, Any]) -> None:
    """Applies vertex color settings to an already imported asset."""
    
    # Apply asset Nanite
    if "build_nanite" in asset_additional_data:
        build_nanite = asset_additional_data["build_nanite"]

        if isinstance(asset, unreal.StaticMesh): 
            nanite_settings = asset.get_editor_property("nanite_settings")
            nanite_settings.enabled = build_nanite
        
            # Apply changes
            static_mesh_subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            static_mesh_subsystem.set_nanite_settings(asset, nanite_settings, apply_changes=True)
            
        if isinstance(asset, unreal.SkeletalMesh): 
            # Unreal Engine 5.5 support Nanite with Skeletal Mesh 
            # but that was not yet added in Python API.
            pass
            '''
            nanite_settings = asset.get_editor_property("nanite_settings")
            nanite_settings.enabled = build_nanite
        
            # Apply changes
            skeletal_mesh_subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
            skeletal_mesh_subsystem.set_nanite_settings(asset, nanite_settings, apply_changes=True)
            '''