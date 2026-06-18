# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List, Dict
from .. import bpl
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType
from . import bfu_asset_export_logs_types


def get_export_asset_logs_details(exported_asset_log: List[bfu_asset_export_logs_types.ExportedAssetLog], console_use: bool = False) -> str:
    """
    Generate a detailed export log for assets exported in the scene.
    The log includes counts and details for each asset type.

    Returns:
        str: The formatted export log.
    """
    asset_counts: Dict[AssetType, int] = {}

    # Initialize variables
    for asset_type_key in AssetType:
        if asset_type_key != AssetType.UNKNOWN:
            asset_counts[asset_type_key] = 0

    # Count assets by type
    for asset in exported_asset_log:
        asset_type = asset.exported_asset.asset_type
        if asset_type in asset_counts:
            asset_counts[asset_type] += 1


    # Build asset type summary with color formatting
    def colorize_count(count: int, text: str) -> str:
        if console_use:
            if count == 0:
                return bpl.color_set.red(text)
            return bpl.color_set.green(text)
        else:
            return text

    asset_strings: List[str] = []
    for asset_type, count in asset_counts.items():
        asset_type_str = colorize_count(count, f"{count} {asset_type.get_friendly_name()}(s)")
        asset_strings.append(asset_type_str)
        
    asset_summary = " | ".join(asset_str for asset_str in asset_strings)


    # Build export log
    export_log = asset_summary + "\n\n"

    for asset in exported_asset_log:
        asset_name = asset.exported_asset.name
        asset_type = asset.exported_asset.asset_type
        # Determine primary information for the asset

        # Log asset
        export_time = bpl.utils.get_formatted_time(asset.get_asset_export_time())
        if console_use:
            export_time = bpl.color_set.yellow(export_time)
        export_log += f"ASSET [{asset_type.get_friendly_name()}] '{asset_name}' EXPORTED IN {export_time}\r\n"

        # Log asset packages
        for package in asset.exported_asset.asset_packages:
            if asset_type in [AssetType.ANIM_ACTION, AssetType.ANIM_POSE, AssetType.ANIM_NLA]:
                primary_info = f"Animation ({asset_type.get_friendly_name()})"
            elif asset_type == asset_type.COLLECTION_AS_STATIC_MESH:
                primary_info = f"Collection ({asset_type.get_friendly_name()})"
            else:
                export_as_lod: bool = package.objects[0].bfu_export_as_lod_mesh  # type: ignore[attr-defined]
                primary_info = f"{asset_type.get_friendly_name()} (LOD)" if package.objects[0] and export_as_lod else asset_type.get_friendly_name()

            export_time = bpl.utils.get_formatted_time(asset.get_package_export_time(package))
            if console_use:
                export_time = bpl.color_set.yellow(export_time)

            # Success status
            export_sucess = True if asset.get_package_export_success(package) else False
            if console_use:
                export_sucess_status = bpl.color_set.green("SUCCESS") if export_sucess else bpl.color_set.red("FAILED")
            else:
                export_sucess_status = "SUCCESS" if export_sucess else "FAILED"
            


            # Append asset details to the log
            export_log += f" -> Package [{primary_info}] '{package.name}' {export_sucess_status} ({export_time})\r\n"

            # Append file details
            if package.file:
                fullpath = str(package.file.get_full_path().resolve())
            else:
                fullpath = "No file path set"
            export_log += f"    {fullpath}\n"

    return export_log