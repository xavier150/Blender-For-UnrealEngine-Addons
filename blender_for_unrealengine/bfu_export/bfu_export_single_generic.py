# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List
from . import bfu_export_utils
from .. import bfu_export_logs
from ..bfu_export_logs.bfu_process_time_logs_types import SafeTimeGroup
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToExport, AssetPackage
from .. import bfu_utils

def prepare_scene_for_package_export(package: AssetPackage):    
    scene = bpy.context.scene
    if scene is None:
        return

    export_objects_list: List[bpy.types.Object] = package.objects

    if package.collection:
        objs = bfu_utils.get_export_collection_objects(package.collection)
        export_objects_list.extend(objs)

    for obj in scene.objects:
        if obj in export_objects_list:
            if obj.hide_viewport is True:
                obj.hide_viewport = False
        else:
            if obj.hide_viewport is False:
                obj.hide_viewport = True



def process_generic_export_from_asset(
    op: bpy.types.Operator,
    asset: AssetToExport
) -> bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog:


    new_log = bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog(asset)
    new_log.start_asset_export()
    for package in asset.asset_packages:
        new_log.start_package_export(package)

        my_timer_group = SafeTimeGroup()
        my_timer_group.start_timer(f"Preparing scene for package export: {package.name}")
        prepare_scene_for_package_export(package)
        my_timer_group.end_last_timer()

        # Check folder before export
        if package.file:
            result = bfu_utils.check_and_make_export_path(package.file.get_full_path())
            if not result:
                new_log.end_package_export(package, False)
                continue


        if package.export_function:
            my_timer_group.start_timer(f"Exporting package: {package.name}")
            result = package.export_function(op, package)
            my_timer_group.end_last_timer()

            if result:
                new_log.end_package_export(package, True)
            else:
                new_log.end_package_export(package, False)
        else:
            new_log.end_package_export(package, False)

    if asset.additional_data and asset.additional_data.file:
        bfu_export_utils.export_additional_data(asset.additional_data.file.get_full_path(), asset.additional_data.data)

    new_log.end_asset_export(True)
    return new_log

