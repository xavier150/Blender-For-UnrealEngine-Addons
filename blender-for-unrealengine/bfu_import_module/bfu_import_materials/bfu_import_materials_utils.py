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

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

def update_task_with_material_data(task: unreal.AssetImportTask, asset_data):

    if asset_data["asset_type"] in ["StaticMesh", "SkeletalMesh"]:

        fbx_import_ui = task.get_editor_property('options')
        fbx_import_ui: unreal.FbxTextureImportData

        if "import_materials" in asset_data:
            fbx_import_ui.set_editor_property('import_materials', asset_data["import_materials"])

        if "import_textures" in asset_data:
            fbx_import_ui.set_editor_property('import_textures', asset_data["import_textures"])


        fbx_texture_import_data = fbx_import_ui.texture_import_data
        fbx_texture_import_data: unreal.FbxTextureImportData

        if "material_search_location" in asset_data:
            if asset_data["material_search_location"] == "Local":
                fbx_texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.LOCAL)
            if asset_data["material_search_location"] == "UnderParent":
                fbx_texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_PARENT)
            if asset_data["material_search_location"] == "UnderRoot":
                fbx_texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_ROOT)
            if asset_data["material_search_location"] == "AllAssets":
                fbx_texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.ALL_ASSETS)

        if "invert_normal_maps" in asset_data:
            fbx_texture_import_data.set_editor_property('invert_normal_maps', asset_data["invert_normal_maps"])


        if asset_data["asset_type"] =="StaticMesh":
            static_mesh_import_data = fbx_import_ui.static_mesh_import_data 
            static_mesh_import_data: unreal.FbxSkeletalMeshImportData
            if "reorder_material_to_fbx_order" in asset_data:
                static_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])

        if asset_data["asset_type"] == "SkeletalMesh":
            skeletal_mesh_import_data = fbx_import_ui.skeletal_mesh_import_data  
            skeletal_mesh_import_data: unreal.FbxStaticMeshImportData
            if "reorder_material_to_fbx_order" in asset_data:
                skeletal_mesh_import_data.set_editor_property('reorder_material_to_fbx_order', asset_data["reorder_material_to_fbx_order"])