# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import os
from typing import List, Optional, Union, TYPE_CHECKING, TypeVar, Type
import unreal
from . import import_module_unreal_utils

# Type variable for Unreal Engine objects
T = TypeVar('T', bound=unreal.Object)

class ImportTask():

    def __init__(self) -> None:
        self.task: unreal.AssetImportTask = unreal.AssetImportTask() 
        if hasattr(unreal, 'InterchangeGenericAssetsPipeline'):
            self.task_option: Optional[Union[unreal.FbxImportUI, unreal.InterchangeGenericAssetsPipeline]] = None  # Type hint for task_option, can be FbxImportUI or InterchangeGenericAssetsPipeline
        else:
            self.task_option: Optional[unreal.FbxImportUI] = None

    def get_preview_import_refs(self) -> str:
        if TYPE_CHECKING:
            filename: str = ""
            destination_path: str = ""
        else:
            filename: str = self.task.get_editor_property('filename')
            destination_path: str = self.task.get_editor_property('destination_path')

        filename_without_ext: str = os.path.splitext(os.path.basename(filename))[0]
        assetname = import_module_unreal_utils.clean_filename_for_unreal(filename_without_ext)
        return destination_path+"/"+assetname+"."+assetname

    if hasattr(unreal, 'InterchangeGenericAssetsPipeline'):
        def set_task_option(self, new_task_option: Union[unreal.FbxImportUI, unreal.InterchangeGenericAssetsPipeline]):
            self.task_option = new_task_option
    else:
        def set_task_option(self, new_task_option: unreal.FbxImportUI):
            self.task_option = new_task_option

    def get_task(self) -> unreal.AssetImportTask:
        return self.task
    
    def set_filename(self, filename: str):
        self.task.set_editor_property('filename', filename)
    
    def get_fbx_import_ui(self) -> unreal.FbxImportUI:
        return self.task_option
    
    if import_module_unreal_utils.alembic_importer_active():
        # Add the function only if alembic importer is active
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



    if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and hasattr(unreal, 'InterchangeGenericMeshPipeline'):
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

    def get_imported_object_paths(self) -> List[str]:
        return self.task.imported_object_paths

    def get_imported_assets(self) -> List[unreal.Object]:
        assets: List[unreal.Object] = []
        for path in self.get_imported_object_paths():
            search_asset = import_module_unreal_utils.load_asset(path)
            if search_asset:
                assets.append(search_asset)
        return assets

    def get_imported_assets_of_class(self, search_class: Type[T]) -> List[T]:
        assets: List[T] = []
        for path in self.get_imported_object_paths():
            search_asset: Optional[unreal.Object] = import_module_unreal_utils.load_asset(path)
            if search_asset and isinstance(search_asset, search_class):  # type: ignore
                assets.append(search_asset)  # Maintenant Pylance comprend que c'est de type T
        return assets

    def get_imported_asset_of_class(self, search_class: Type[T]) -> Optional[T]:
        for path in self.get_imported_object_paths():
            search_asset: Optional[unreal.Object] = import_module_unreal_utils.load_asset(path)
            if search_asset and isinstance(search_asset, search_class):  # type: ignore
                return search_asset  # Maintenant Pylance comprend que c'est de type T
        return None

    def get_imported_static_mesh(self) -> Optional[unreal.StaticMesh]:
        return self.get_imported_asset_of_class(unreal.StaticMesh)

    def get_imported_skeleton(self) -> Optional[unreal.Skeleton]:
        return self.get_imported_asset_of_class(unreal.Skeleton)

    def get_imported_skeletal_mesh(self) -> Optional[unreal.SkeletalMesh]:
        return self.get_imported_asset_of_class(unreal.SkeletalMesh)

    def get_imported_anim_sequence(self) -> Optional[unreal.AnimSequence]:
        return self.get_imported_asset_of_class(unreal.AnimSequence)

    def get_imported_anim_sequences(self) -> List[unreal.AnimSequence]:
        return self.get_imported_assets_of_class(unreal.AnimSequence)

    def import_asset_task(self):
        # InterchangePipelineStackOverride was added in Unreal Engine 5.2
        if hasattr(unreal, 'InterchangePipelineStackOverride') and isinstance(self.task_option, unreal.InterchangeGenericAssetsPipeline):
            self.task.set_editor_property('options', unreal.InterchangePipelineStackOverride())

            # unreal.InterchangePipelineStackOverride.add_pipeline was added in Unreal Engine 5.3
            if hasattr(unreal.InterchangePipelineStackOverride, 'add_pipeline'):
                self.task.get_editor_property('options').add_pipeline(self.task_option)
            else:
                # For older versions of Unreal Engine where add_pipeline is not available
                self.task.get_editor_property('options').get_editor_property('override_pipelines').append(self.task_option)
        else:
            self.task.set_editor_property('options', self.task_option)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self.task])
    
    def get_task_options(self):
        # InterchangePipelineStackOverride was added in Unreal Engine 5.2
        if hasattr(unreal, 'InterchangePipelineStackOverride') and isinstance(self.task_option, unreal.InterchangeGenericAssetsPipeline):
            new_option = unreal.InterchangePipelineStackOverride()

            # unreal.InterchangePipelineStackOverride.add_pipeline was added in Unreal Engine 5.3
            if hasattr(unreal.InterchangePipelineStackOverride, 'add_pipeline'):
                new_option.add_pipeline(self.task_option)
            else:
                new_option.get_editor_property('override_pipelines').append(self.task_option)
            return new_option
        else:
            return self.task_option