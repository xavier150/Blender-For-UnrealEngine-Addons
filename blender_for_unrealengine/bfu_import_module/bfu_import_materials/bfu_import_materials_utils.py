# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import unreal
from .. import import_module_tasks_class
from .. import import_module_utils
from ..asset_types import ExportAssetType 


def apply_import_settings(itask: import_module_tasks_class.ImportTask, asset_data: dict, asset_additional_data: dict) -> None:
    """Applies material and texture import settings to StaticMesh and SkeletalMesh assets."""
    import_module_utils.print_debug_step("Set Materials import settings.")
    
    asset_type = ExportAssetType.get_asset_type_from_string(asset_data.get("asset_type"))
    if asset_type not in [ExportAssetType.STATIC_MESH, ExportAssetType.SKELETAL_MESH]:
        # Only apply settings for StaticMesh and SkeletalMesh
        return

    # Material and texture import settings
    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        if "import_materials" in asset_additional_data:
            itask.get_igap_material().set_editor_property('import_materials', asset_additional_data["import_materials"])

        if "import_textures" in asset_additional_data:
            itask.get_igap_texture().set_editor_property('import_textures', asset_additional_data["import_textures"])
    else:
        if "import_materials" in asset_additional_data:
            itask.get_fbx_import_ui().set_editor_property('import_materials', asset_additional_data["import_materials"])

        if "import_textures" in asset_additional_data:
            itask.get_fbx_import_ui().set_editor_property('import_textures', asset_additional_data["import_textures"])

    # Material search location and normal map green channel flip
    
    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        # unreal.InterchangeGenericMaterialPipeline.search_location was added in Unreal Engine 5.4
        if hasattr(itask.get_igap_material(), 'search_location'):
            if "material_search_location" in asset_additional_data:
                search_location = asset_additional_data["material_search_location"]
                location_enum = {
                    "Local": unreal.InterchangeMaterialSearchLocation.LOCAL,
                    "UnderParent": unreal.InterchangeMaterialSearchLocation.UNDER_PARENT,
                    "UnderRoot": unreal.InterchangeMaterialSearchLocation.UNDER_ROOT,
                    "AllAssets": unreal.InterchangeMaterialSearchLocation.ALL_ASSETS
                }
                if search_location in location_enum:
                    itask.get_igap_material().set_editor_property('search_location', location_enum[search_location])

        if "flip_normal_map_green_channel" in asset_additional_data:
            itask.get_igap_texture().set_editor_property('flip_normal_map_green_channel', asset_additional_data["flip_normal_map_green_channel"])

    else:
        texture_import_data = itask.get_texture_import_data()
        
        if "material_search_location" in asset_additional_data:
            search_location = asset_additional_data["material_search_location"]
            location_enum = {
                "Local": unreal.MaterialSearchLocation.LOCAL,
                "UnderParent": unreal.MaterialSearchLocation.UNDER_PARENT,
                "UnderRoot": unreal.MaterialSearchLocation.UNDER_ROOT,
                "AllAssets": unreal.MaterialSearchLocation.ALL_ASSETS
            }
            if search_location in location_enum:
                texture_import_data.set_editor_property('material_search_location', location_enum[search_location])

        if "flip_normal_map_green_channel" in asset_additional_data:
            texture_import_data.set_editor_property('invert_normal_maps', asset_additional_data["flip_normal_map_green_channel"])
    
    # Mat order
    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
        # @TODO reorder_material_to_fbx_order Removed with InterchangeGenericAssetsPipeline? 
        # I yes need also remove reorder_material_to_fbx_order from the addon propertys.
        pass

    else:
        if asset_type == ExportAssetType.STATIC_MESH:
            if "reorder_material_to_fbx_order" in asset_additional_data:
                itask.get_static_mesh_import_data().set_editor_property('reorder_material_to_fbx_order', asset_additional_data["reorder_material_to_fbx_order"])

        elif asset_type == ExportAssetType.SKELETAL_MESH:
            if "reorder_material_to_fbx_order" in asset_additional_data:
                itask.get_skeletal_mesh_import_data().set_editor_property('reorder_material_to_fbx_order', asset_additional_data["reorder_material_to_fbx_order"])


def apply_asset_settings(itask: import_module_tasks_class.ImportTask, asset_additional_data: dict) -> None:
    # Empty for the momment
    pass
