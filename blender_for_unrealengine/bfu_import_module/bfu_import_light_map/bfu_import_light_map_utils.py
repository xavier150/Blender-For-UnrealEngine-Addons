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
    import_module_utils.print_debug_step("Set Light Map import settings.")

    asset_type = ExportAssetType.get_asset_type_from_string(asset_data.get("asset_type"))
    if asset_type not in [ExportAssetType.STATIC_MESH]:
        # Only apply settings for StaticMesh and SkeletalMesh
        return

    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        if asset_type == ExportAssetType.STATIC_MESH:
            if "generate_light_map_uvs" in asset_additional_data:
                itask.get_igap_mesh().set_editor_property('generate_lightmap_u_vs', asset_additional_data["generate_light_map_uvs"])
    else:
        if asset_type == ExportAssetType.STATIC_MESH:
            if "generate_light_map_uvs" in asset_additional_data:
                itask.get_static_mesh_import_data().set_editor_property('generate_lightmap_u_vs', asset_additional_data["generate_light_map_uvs"])


def apply_asset_settings(itask: import_module_tasks_class.ImportTask, asset_additional_data: Dict[str, Any]) -> None:
    import_module_utils.print_debug_step("Set Light Map post import settings.")

    # Check   
    static_mesh = itask.get_imported_static_mesh()
    if static_mesh is None:
        return
    
    if "use_custom_light_map_resolution" in asset_additional_data:
        if asset_additional_data["use_custom_light_map_resolution"]:
            if "light_map_resolution" in asset_additional_data:
                static_mesh.set_editor_property('light_map_resolution', asset_additional_data["light_map_resolution"])
                build_settings = unreal.EditorStaticMeshLibrary.get_lod_build_settings(static_mesh, 0)
                build_settings.min_lightmap_resolution = asset_additional_data["light_map_resolution"]
                unreal.EditorStaticMeshLibrary.set_lod_build_settings(static_mesh, 0, build_settings)

    asset_import_data = static_mesh.get_editor_property('asset_import_data')
    if "generate_light_map_uvs" in asset_additional_data:
        generate_light_map_uvs: bool = asset_additional_data["generate_light_map_uvs"]
        if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
            mesh_pipeline = asset_import_data.get_pipelines()[0].get_editor_property('mesh_pipeline')
            mesh_pipeline.set_editor_property('generate_lightmap_u_vs', generate_light_map_uvs)  # Import data
            unreal.EditorStaticMeshLibrary.set_generate_lightmap_uv(static_mesh, generate_light_map_uvs)  # Build settings at lod

        else:
            generate_light_map_uvs: bool = asset_additional_data["generate_light_map_uvs"]
            asset_import_data.set_editor_property('generate_lightmap_u_vs', generate_light_map_uvs)  # Import data
            unreal.EditorStaticMeshLibrary.set_generate_lightmap_uv(static_mesh, generate_light_map_uvs)  # Build settings at lod
