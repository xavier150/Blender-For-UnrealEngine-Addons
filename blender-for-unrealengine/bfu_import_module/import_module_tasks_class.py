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


from . import import_module_unreal_utils
from . import config

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

class ImportTaks():

    def __init__(self) -> None:
        self.task = unreal.AssetImportTask() 
        self.task_option = None

        if config.force_use_interchange == "Interchange":
            self.use_interchange = True

        elif config.force_use_interchange == "FBX":
            self.use_interchange = False

        else:
            if import_module_unreal_utils.is_unreal_version_greater_or_equal(5,5):
                # Set values inside unreal.InterchangeGenericAssetsPipeline (unreal.InterchangeGenericCommonMeshesProperties or ...)
                self.use_interchange = True
            else:
                # Set values inside unreal.FbxStaticMeshImportData or ...
                self.use_interchange = False

    def set_task_option(self, new_task_option):
        self.task_option = new_task_option

    def get_task(self):
        return self.task
    
    def get_fbx_import_ui(self) -> unreal.FbxImportUI:
        return self.task_option
    
    def get_abc_import_settings(self) -> unreal.AbcImportSettings:
        return self.task_option

    def get_static_mesh_import_data(self) -> unreal.FbxStaticMeshImportData:
        return self.task_option.static_mesh_import_data

    def get_skeletal_mesh_import_data(self) -> unreal.FbxSkeletalMeshImportData:
        return self.task_option.skeletal_mesh_import_data

    def get_animation_import_data(self) -> unreal.FbxAnimSequenceImportData:
        return self.task_option.anim_sequence_import_data
    
    def get_texture_import_data(self) -> unreal.FbxTextureImportData:
        return self.task_option.texture_import_data



    def get_igap(self) -> unreal.InterchangeGenericAssetsPipeline:
        # unreal.InterchangeGenericAssetsPipeline
        return self.task_option

    def get_igap_mesh(self) -> unreal.InterchangeGenericMeshPipeline:
        # unreal.InterchangeGenericMeshPipeline
        return self.task_option.get_editor_property('mesh_pipeline')

    def get_igap_skeletal_mesh(self) -> unreal.InterchangeGenericCommonSkeletalMeshesAndAnimationsProperties:
        # unreal.InterchangeGenericCommonSkeletalMeshesAndAnimationsProperties
        return self.task_option.get_editor_property('common_skeletal_meshes_and_animations_properties')

    def get_igap_common_mesh(self) -> unreal.InterchangeGenericCommonMeshesProperties:
        # unreal.InterchangeGenericCommonMeshesProperties
        return self.task_option.get_editor_property('common_meshes_properties')

    def get_igap_material(self) -> unreal.InterchangeGenericMaterialPipeline:
        # unreal.InterchangeGenericMaterialPipeline
        return self.task_option.get_editor_property('material_pipeline')

    def get_igap_texture(self) -> unreal.InterchangeGenericTexturePipeline:
        # unreal.InterchangeGenericTexturePipeline
        return self.task_option.get_editor_property('material_pipeline').get_editor_property('texture_pipeline')

    def get_igap_animation(self) -> unreal.InterchangeGenericAnimationPipeline:
        # unreal.InterchangeGenericAnimationPipeline
        return self.task_option.get_editor_property('animation_pipeline')
    
    def get_imported_assets(self) -> list[unreal.Object]:
        assets = []
        for path in self.task.imported_object_paths:
            search_asset = import_module_unreal_utils.load_asset(path)
            if search_asset:
                assets.append(search_asset)
        return assets

    def get_imported_static_mesh(self) -> unreal.StaticMesh | None:
        return next((asset for asset in self.get_imported_assets() if isinstance(asset, unreal.StaticMesh)), None)

    def get_imported_skeleton(self) -> unreal.Skeleton | None:
        return next((asset for asset in self.get_imported_assets() if isinstance(asset, unreal.Skeleton)), None)

    def get_imported_skeletal_mesh(self) -> unreal.SkeletalMesh | None:
        return next((asset for asset in self.get_imported_assets() if isinstance(asset, unreal.SkeletalMesh)), None)

    def get_imported_anim_sequence(self) -> unreal.AnimSequence | None:
        return next((asset for asset in self.get_imported_assets() if isinstance(asset, unreal.AnimSequence)), None)
    
    def import_asset_task(self):
        if self.use_interchange:
            self.task.set_editor_property('options', unreal.InterchangePipelineStackOverride())
            self.task.get_editor_property('options').add_pipeline(self.task_option)
        else:
            self.task.set_editor_property('options', self.task_option)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self.task])