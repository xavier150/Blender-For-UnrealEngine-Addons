# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import unreal
from .. import import_module_unreal_utils
from .. import import_module_tasks_class
from .. import import_module_utils
from ..asset_types import ExportAssetType


def import_static_lod(asset: unreal.StaticMesh, asset_options, asset_additional_data, lod_name, lod_number):

    import_module_utils.print_debug_step(f"Start Import Lod_{str(lod_number)} ({lod_name})")
    if "level_of_details" in asset_additional_data:
        if lod_name in asset_additional_data["level_of_details"]:
            lodTask = unreal.AssetImportTask()
            lodTask.filename = asset_additional_data["level_of_details"][lod_name]

            # Get Lod0 destination_path
            asset_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(asset)
            destination_path = unreal.Paths.get_path(asset_path)
            lodTask.destination_path = destination_path
            lodTask.automated = True
            lodTask.replace_existing = True

            if asset_options:
                lodTask.set_editor_property('options', asset_options)
            else:
                # Replicate asset import settings when asset_options is None
                lodTask.set_editor_property('options', asset.get_editor_property('asset_import_data'))


            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])
            if len(lodTask.imported_object_paths) > 0:
                lodAsset = import_module_unreal_utils.load_asset(lodTask.imported_object_paths[0])
                slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, lod_number, lodAsset, 0, True)
                unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])


def import_skeletal_lod(asset: unreal.SkeletalMesh, asset_options, asset_additional_data, lod_name, lod_number):
    if "level_of_details" in asset_additional_data:
        if lod_name in asset_additional_data["level_of_details"]:
            # Unreal python no longer support Skeletal mesh LODS import.
            pass

def set_static_mesh_lods(asset: unreal.StaticMesh, asset_options, asset_additional_data):
    import_module_utils.print_debug_step("Process Static Lods")
    # Import the StaticMesh lod(s)
    unreal.EditorStaticMeshLibrary.remove_lods(asset)  
    import_static_lod(asset, asset_options, asset_additional_data, "lod_1", 1)
    import_static_lod(asset, asset_options, asset_additional_data, "lod_2", 2)
    import_static_lod(asset, asset_options, asset_additional_data, "lod_3", 3)
    import_static_lod(asset, asset_options, asset_additional_data, "lod_4", 4)
    import_static_lod(asset, asset_options, asset_additional_data, "lod_5", 5)


def set_skeletal_mesh_lods(asset: unreal.SkeletalMesh, asset_options, asset_additional_data):
    import_module_utils.print_debug_step("Process Skeletal Lods")
    # Import the SkeletalMesh lod(s)
    import_skeletal_lod(asset, asset_options, asset_additional_data, "lod_1", 1)
    import_skeletal_lod(asset, asset_options, asset_additional_data, "lod_2", 2)
    import_skeletal_lod(asset, asset_options, asset_additional_data, "lod_3", 3)
    import_skeletal_lod(asset, asset_options, asset_additional_data, "lod_4", 4)
    import_skeletal_lod(asset, asset_options, asset_additional_data, "lod_5", 5)

def apply_import_settings(itask: import_module_tasks_class.ImportTask, asset_data: dict, asset_additional_data: dict) -> None:
    """Applies lods and lod group import settings to StaticMesh and SkeletalMesh assets."""
    import_module_utils.print_debug_step("Set Lods import settings.")
    
    # Set lod group in import settings before import.
    asset_type = ExportAssetType.get_asset_type_from_string(asset_data.get("asset_type"))

    if asset_type.value == ExportAssetType.STATIC_MESH.value:

        if "static_mesh_lod_group" in asset_additional_data:
            desired_lod_group = asset_additional_data["static_mesh_lod_group"]
            # Bug ? Unreal never apply the lod_group that set in import settings!
            # And if I set lod_group after the import it not apply because that the same name.
            # So I set a None group name set the correct one after import.
            # desired_lod_group = asset_additional_data["static_mesh_lod_group"]
            desired_lod_group = "None"

            if hasattr(unreal, 'InterchangeGenericAssetsPipeline') and isinstance(itask.task_option, unreal.InterchangeGenericAssetsPipeline):
                itask.get_igap_mesh().set_editor_property('lod_group', desired_lod_group)
            else:
                itask.get_static_mesh_import_data().set_editor_property('static_mesh_lod_group', desired_lod_group)

def apply_asset_settings(itask: import_module_tasks_class.ImportTask, asset_additional_data: dict) -> None:
    """Applies lods and lod group import settings to StaticMesh and SkeletalMesh assets."""
    import_module_utils.print_debug_step("Set Lods import settings.")
    static_mesh = itask.get_imported_static_mesh()
    skeletal_mesh = itask.get_imported_skeletal_mesh()

    if static_mesh is not None:
        # Import custom static mesh lods
        set_static_mesh_lods(static_mesh, itask.get_task_options(), asset_additional_data)

        # Set Lod Group mesh   
        if static_mesh is not None:
            if "static_mesh_lod_group" in asset_additional_data:
                if asset_additional_data["static_mesh_lod_group"]:
                    desired_lod_group = asset_additional_data["static_mesh_lod_group"]
                    if import_module_unreal_utils.get_unreal_version() > (5,4,0):
                        static_mesh.set_editor_property('lod_group', desired_lod_group)
                    else:
                        # Lod group don't auto apply on older Unreal version.
                        static_mesh.set_editor_property('lod_group', "") # Set to empty string to force Unreal to apply the new LOD group
                        static_mesh.set_editor_property('lod_group', desired_lod_group)
                    #print(f"Set Lod Group to '{desired_lod_group}' for StaticMesh '{static_mesh.get_name()}'")

    elif skeletal_mesh is not None:
        # Import custom skeletal mesh lods
        set_skeletal_mesh_lods(skeletal_mesh, itask.get_task_options(), asset_additional_data)