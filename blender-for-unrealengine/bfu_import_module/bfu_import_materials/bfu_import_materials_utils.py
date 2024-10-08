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

def apply_import_settings(itask: import_module_tasks_class.ImportTaks, asset_data):
    print("Mat S0")
    asset_type = asset_data["asset_type"]
    if asset_type not in ["StaticMesh", "SkeletalMesh"]:
        # Only for Static and Skeletal Mesh
        return

    print("Mat S1")
    # Mat and texture use
    if itask.use_interchange:
        if "import_materials" in asset_data:
            itask.GetIGAP_Mat().set_editor_property('import_materials', asset_data["import_materials"])

        if "import_textures" in asset_data:
            itask.GetIGAP_Tex().set_editor_property('import_textures', asset_data["import_textures"])
    else:
        fbx_import_ui = itask.GetFbxImportUI()
        if "import_materials" in asset_data:
            fbx_import_ui.set_editor_property('import_materials', asset_data["import_materials"])

        if "import_textures" in asset_data:
            fbx_import_ui.set_editor_property('import_textures', asset_data["import_textures"])

    print("Mat S2")
    # Mat search and normal map green chanel
    if itask.use_interchange:
        if "material_search_location" in asset_data:
            if asset_data["material_search_location"] == "Local":
                itask.GetIGAP_Mat().set_editor_property('search_location', unreal.InterchangeMaterialSearchLocation.LOCAL)
            if asset_data["material_search_location"] == "UnderParent":
                itask.GetIGAP_Mat().set_editor_property('search_location', unreal.InterchangeMaterialSearchLocation.UNDER_PARENT)
            if asset_data["material_search_location"] == "UnderRoot":
                itask.GetIGAP_Mat().set_editor_property('search_location', unreal.InterchangeMaterialSearchLocation.UNDER_ROOT)
            if asset_data["material_search_location"] == "AllAssets":
                itask.GetIGAP_Mat().set_editor_property('search_location', unreal.InterchangeMaterialSearchLocation.ALL_ASSETS)

        if "flip_normal_map_green_channel" in asset_data:
            itask.GetIGAP_Tex().set_editor_property('flip_normal_map_green_channel', asset_data["flip_normal_map_green_channel"])

    else:
        if "material_search_location" in asset_data:
            if asset_data["material_search_location"] == "Local":
                itask.GetTextureImportData().set_editor_property('material_search_location', unreal.MaterialSearchLocation.LOCAL)
            if asset_data["material_search_location"] == "UnderParent":
                itask.GetTextureImportData().set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_PARENT)
            if asset_data["material_search_location"] == "UnderRoot":
                itask.GetTextureImportData().set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_ROOT)
            if asset_data["material_search_location"] == "AllAssets":
                itask.GetTextureImportData().set_editor_property('material_search_location', unreal.MaterialSearchLocation.ALL_ASSETS)

        if "flip_normal_map_green_channel" in asset_data:
            itask.GetTextureImportData().set_editor_property('invert_normal_maps', asset_data["flip_normal_map_green_channel"])

    print("Mat S3")
    # Mat order
    if itask.use_interchange:
        # @TODO reorder_material_to_fbx_order Removed with InterchangeGenericAssetsPipeline? 
        # I yes need also remove reorder_material_to_fbx_order from the addon propertys.
        pass
    else:
        if asset_type =="StaticMesh":
            if "reorder_material_to_fbx_order" in asset_data:
                itask.GetStaticMeshImportData().set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])

        elif asset_type == "SkeletalMesh":
            if "reorder_material_to_fbx_order" in asset_data:
                itask.GetSkeletalMeshImportData().set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])