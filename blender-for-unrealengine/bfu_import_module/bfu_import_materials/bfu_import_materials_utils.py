# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

from .. import import_module_unreal_utils
from .. import import_module_tasks_class

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

def apply_import_settings(itask: import_module_tasks_class.ImportTaks, asset_data: dict) -> None:
    """Applies material and texture import settings to StaticMesh and SkeletalMesh assets."""
    
    print("Mat S0")
    
    asset_type = asset_data.get("asset_type")
    if asset_type not in ["StaticMesh", "SkeletalMesh"]:
        # Only apply settings for StaticMesh and SkeletalMesh
        return

    print("Mat S1")
    
    # Material and texture import settings
    if itask.use_interchange:
        if "import_materials" in asset_data:
            itask.get_igap_material().set_editor_property('import_materials', asset_data["import_materials"])

        if "import_textures" in asset_data:
            itask.get_igap_texture().set_editor_property('import_textures', asset_data["import_textures"])
    else:
        if "import_materials" in asset_data:
            itask.get_fbx_import_ui().set_editor_property('import_materials', asset_data["import_materials"])

        if "import_textures" in asset_data:
            itask.get_fbx_import_ui().set_editor_property('import_textures', asset_data["import_textures"])

    print("Mat S2")
    
    # Material search location and normal map green channel flip
    if itask.use_interchange:
        if "material_search_location" in asset_data:
            search_location = asset_data["material_search_location"]
            location_enum = {
                "Local": unreal.InterchangeMaterialSearchLocation.LOCAL,
                "UnderParent": unreal.InterchangeMaterialSearchLocation.UNDER_PARENT,
                "UnderRoot": unreal.InterchangeMaterialSearchLocation.UNDER_ROOT,
                "AllAssets": unreal.InterchangeMaterialSearchLocation.ALL_ASSETS
            }
            if search_location in location_enum:
                itask.get_igap_material().set_editor_property('search_location', location_enum[search_location])

        if "flip_normal_map_green_channel" in asset_data:
            itask.get_igap_texture().set_editor_property('flip_normal_map_green_channel', asset_data["flip_normal_map_green_channel"])

    else:
        texture_import_data = itask.get_texture_import_data()
        
        if "material_search_location" in asset_data:
            search_location = asset_data["material_search_location"]
            location_enum = {
                "Local": unreal.MaterialSearchLocation.LOCAL,
                "UnderParent": unreal.MaterialSearchLocation.UNDER_PARENT,
                "UnderRoot": unreal.MaterialSearchLocation.UNDER_ROOT,
                "AllAssets": unreal.MaterialSearchLocation.ALL_ASSETS
            }
            if search_location in location_enum:
                texture_import_data.set_editor_property('material_search_location', location_enum[search_location])

        if "flip_normal_map_green_channel" in asset_data:
            texture_import_data.set_editor_property('invert_normal_maps', asset_data["flip_normal_map_green_channel"])

    print("Mat S3")
    
    # Mat order
    if itask.use_interchange:
        # @TODO reorder_material_to_fbx_order Removed with InterchangeGenericAssetsPipeline? 
        # I yes need also remove reorder_material_to_fbx_order from the addon propertys.
        pass

    else:
        if asset_type =="StaticMesh":
            if "reorder_material_to_fbx_order" in asset_data:
                itask.get_static_mesh_import_data().set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])

        elif asset_type == "SkeletalMesh":
            if "reorder_material_to_fbx_order" in asset_data:
                itask.get_skeletal_mesh_import_data().set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])