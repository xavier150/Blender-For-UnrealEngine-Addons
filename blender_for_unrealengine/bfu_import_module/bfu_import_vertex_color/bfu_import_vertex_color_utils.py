# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import Optional, Union, Dict, Any, List
import unreal
from .. import import_module_tasks_class
from .. import import_module_utils
from ..asset_types import ExportAssetType



def get_vertex_override_color(asset_additional_data: Dict[str, Any]) -> Optional[unreal.LinearColor]:
    """Retrieves the vertex override color from the asset data, if available."""
    import_module_utils.print_debug_step("Set Vertex Color import settings.")

    if asset_additional_data is None:
        return None

    if "vertex_override_color" in asset_additional_data:
        return unreal.LinearColor(
            asset_additional_data["vertex_override_color"][0],
            asset_additional_data["vertex_override_color"][1],
            asset_additional_data["vertex_override_color"][2]
        )

    return None

if hasattr(unreal, 'InterchangeVertexColorImportOption'):
    def get_interchange_vertex_color_import_option(asset_additional_data: Dict[str, Any]) -> Optional[unreal.InterchangeVertexColorImportOption]:
        """Retrieves the vertex color import option based on the asset data and pipeline."""

        key = "vertex_color_import_option"
        if key in asset_additional_data:
            option_value = asset_additional_data.get(key)

            # For unreal.InterchangeGenericCommonMeshesProperties
            if option_value == "IGNORE":
                return unreal.InterchangeVertexColorImportOption.IVCIO_IGNORE
            elif option_value == "OVERRIDE":
                return unreal.InterchangeVertexColorImportOption.IVCIO_OVERRIDE
            elif option_value == "REPLACE":
                return unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE
            return unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE  # Default


def get_vertex_color_import_option(asset_additional_data: Dict[str, Any]) -> Optional[unreal.VertexColorImportOption]:
    """Retrieves the vertex color import option based on the asset data and pipeline."""

    key = "vertex_color_import_option"
    if key in asset_additional_data:
        option_value = asset_additional_data.get(key)

        # For unreal.FbxStaticMeshImportData
        if option_value == "IGNORE":
            return unreal.VertexColorImportOption.IGNORE
        elif option_value == "OVERRIDE":
            return unreal.VertexColorImportOption.OVERRIDE
        elif option_value == "REPLACE":
            return unreal.VertexColorImportOption.REPLACE
        return unreal.VertexColorImportOption.REPLACE  # Default
    


def apply_import_settings(itask: import_module_tasks_class.ImportTask, asset_data: Dict[str, Any], asset_additional_data: Dict[str, Any]) -> None:
    """Applies vertex color settings during the import process."""
    import_module_utils.print_debug_step("Set Vertex Color post import settings.")

    asset_type = ExportAssetType.get_asset_type_from_string(asset_data.get("asset_type"))
    if asset_type not in [ExportAssetType.STATIC_MESH, ExportAssetType.SKELETAL_MESH]:
        # Only apply settings for StaticMesh and SkeletalMesh
        return

    vertex_override_color = get_vertex_override_color(asset_additional_data)
    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        vertex_color_import_option = get_interchange_vertex_color_import_option(asset_additional_data)
    else:
        vertex_color_import_option = get_vertex_color_import_option(asset_additional_data)

    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        itask.get_igap_common_mesh().set_editor_property('vertex_color_import_option', vertex_color_import_option)
        if vertex_override_color:
            itask.get_igap_common_mesh().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())
    else:
        if asset_type.value == ExportAssetType.STATIC_MESH.value:
            itask.get_static_mesh_import_data().set_editor_property('vertex_color_import_option', vertex_color_import_option)
            if vertex_override_color:
                itask.get_static_mesh_import_data().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

        elif asset_type.value == ExportAssetType.SKELETAL_MESH.value:
            itask.get_skeletal_mesh_import_data().set_editor_property('vertex_color_import_option', vertex_color_import_option)
            if vertex_override_color:
                itask.get_skeletal_mesh_import_data().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())


def apply_asset_settings(itask: import_module_tasks_class.ImportTask, asset_additional_data: Dict[str, Any]) -> None:
    """Applies vertex color settings to an already imported asset."""

    # Check   
    static_mesh: unreal.StaticMesh = itask.get_imported_static_mesh()
    skeletal_mesh: unreal.SkeletalMesh = itask.get_imported_skeletal_mesh()

    # Loop for static and skeletal meshs
    skinned_assets: List[unreal.SkinnedAsset] = [static_mesh, skeletal_mesh]
    for asset in skinned_assets:
        if asset:
            apply_one_asset_settings(itask, asset, asset_additional_data)


def apply_one_asset_settings(itask: import_module_tasks_class.ImportTask, asset: unreal.Object, asset_additional_data: Dict[str, Any]) -> None:
    """Applies vertex color settings to an already imported asset."""

    vertex_override_color = get_vertex_override_color(asset_additional_data)
        
    asset_import_data = asset.get_editor_property('asset_import_data')
    asset_import_data: Union[unreal.FbxStaticMeshImportData, unreal.FbxSkeletalMeshImportData, unreal.InterchangeAssetImportData]
    
    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(asset_import_data, unreal.InterchangeAssetImportData):
        common_meshes_properties = asset_import_data.get_pipelines()[0].get_editor_property('common_meshes_properties')
        if vertex_override_color:
            common_meshes_properties.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

        vertex_color_import_option = get_interchange_vertex_color_import_option(asset_additional_data)
        if vertex_color_import_option:
            common_meshes_properties.set_editor_property('vertex_color_import_option', vertex_color_import_option)
    else:
        asset_import_data = asset.get_editor_property('asset_import_data')
        if vertex_override_color:
            asset_import_data.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())
            
        vertex_color_import_option = get_vertex_color_import_option(asset_additional_data)
        if vertex_color_import_option:
            asset_import_data.set_editor_property('vertex_color_import_option', vertex_color_import_option)