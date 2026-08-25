# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import Union
import unreal
from . import import_module_unreal_utils
from .asset_types import ExportAssetType, AssetFileTypeEnum
from . import config


if hasattr(unreal, 'InterchangeGenericAssetsPipeline'):
    def task_options_default_preset(use_interchange: bool = True) -> Union[unreal.FbxImportUI, unreal.InterchangeGenericAssetsPipeline]:
        """Returns default task options preset based on interchange usage and Unreal version."""
        if use_interchange:
            options = unreal.InterchangeGenericAssetsPipeline()
        else:
            options = unreal.FbxImportUI()
        return options

    def task_options_static_mesh_preset(use_interchange: bool = True) -> Union[unreal.InterchangeGenericAssetsPipeline, unreal.FbxImportUI]:
        """Returns static mesh task options preset based on interchange usage."""
        if use_interchange:
            options = unreal.InterchangeGenericAssetsPipeline()
        else:
            options = unreal.FbxImportUI()
        return options

    def task_options_skeletal_mesh_preset(use_interchange: bool = True) -> Union[unreal.InterchangeGenericAssetsPipeline, unreal.FbxImportUI]:
        """Returns skeletal mesh task options preset based on interchange usage."""
        if use_interchange:
            options = unreal.InterchangeGenericAssetsPipeline()
        else:
            options = unreal.FbxImportUI()
        return options

    def task_options_animation_preset(use_interchange: bool = True) -> Union[unreal.InterchangeGenericAssetsPipeline, unreal.FbxImportUI]:
        """Returns animation task options preset based on interchange usage."""
        if use_interchange:
            options = unreal.InterchangeGenericAssetsPipeline()
        else:
            options = unreal.FbxImportUI()
        return options
else:
    def task_options_default_preset(use_interchange: bool = True) -> unreal.FbxImportUI:
        """Returns default task options preset for Unreal Engine versions below 5, without interchange support."""
        return unreal.FbxImportUI()

    def task_options_static_mesh_preset(use_interchange: bool = True) -> unreal.FbxImportUI:
        """Returns static mesh task options preset without interchange support."""
        return unreal.FbxImportUI()

    def task_options_skeletal_mesh_preset(use_interchange: bool = True) -> unreal.FbxImportUI:
        """Returns skeletal mesh task options preset without interchange support."""
        return unreal.FbxImportUI()

    def task_options_animation_preset(use_interchange: bool = True) -> unreal.FbxImportUI:
        """Returns animation task options preset without interchange support."""
        return unreal.FbxImportUI()

if import_module_unreal_utils.alembic_importer_active():
    # Add the function only if alembic importer is active
    def task_options_alembic_preset(use_interchange: bool = True) -> unreal.AbcImportSettings:
        """Returns Alembic task options preset."""
        options = unreal.AbcImportSettings()
        return options

if hasattr(unreal, 'InterchangeGenericAssetsPipeline'):
    def init_options_data(asset_type: ExportAssetType, filetype: AssetFileTypeEnum):
        """Initializes task options based on asset type and interchange usage."""
        
        # For FBX file it better to not use interchange before UE 5.5.
        if config.force_use_interchange:
            use_interchange = True
        elif filetype.value == AssetFileTypeEnum.FBX.value and import_module_unreal_utils.get_unreal_version() < (5,5,0):
            use_interchange = False
        else:
            use_interchange = True


        # Add the function only if alembic importer is active
        if asset_type.value == ExportAssetType.ANIM_ALEMBIC.value and import_module_unreal_utils.alembic_importer_active():
            options = task_options_alembic_preset(use_interchange)

        elif asset_type.is_static_mesh():
            options = task_options_static_mesh_preset(use_interchange)

        elif asset_type.value == ExportAssetType.SKELETAL_MESH.value:
            options = task_options_skeletal_mesh_preset(use_interchange)

        elif asset_type.is_skeletal_animation():
            options = task_options_animation_preset(use_interchange)
            
        else:
            options = task_options_default_preset(use_interchange)
        
        return options
else:
    def init_options_data(asset_type: ExportAssetType, filetype: AssetFileTypeEnum):
        """Initializes task options based on asset type and interchange usage."""
        
        # Add the function only if alembic importer is active
        if asset_type.value == ExportAssetType.ANIM_ALEMBIC.value and import_module_unreal_utils.alembic_importer_active():
            options = task_options_alembic_preset(False)

        elif asset_type.is_static_mesh():
            options = task_options_static_mesh_preset(False)

        elif asset_type.value == ExportAssetType.SKELETAL_MESH.value:
            options = task_options_skeletal_mesh_preset(False)

        elif asset_type.is_skeletal_animation():
            options = task_options_animation_preset(False)
            
        else:
            options = task_options_default_preset(False)
        
        return options