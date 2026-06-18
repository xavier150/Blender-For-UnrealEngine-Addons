# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Any, Optional, List
from . import bfu_asset_manager_type
from . import bfu_asset_manager_registred_assets

def get_all_supported_asset_class(data: Any, details: Any = None) -> List[bfu_asset_manager_type.BFU_BaseAssetClass]:
    """
    Returns a list of all asset classes that support the given data and details.
    :param data: The data to check for supported asset classes.
    :param details: Additional details that may affect asset class support.
    :return: A list of supported asset classes.
    """

    supported_classes: List[bfu_asset_manager_type.BFU_BaseAssetClass] = []
    for asset in bfu_asset_manager_registred_assets.get_registred_asset_class():
        if asset.support_asset_type(data, details):
            pass
            if asset.can_export_asset(data):
                supported_classes.append(asset)
    return supported_classes

def get_custom_type_supported_asset_class(custom_type: str, data: Any, details: Any = None) -> List[bfu_asset_manager_type.BFU_BaseAssetClass]:
    supported_classes: List[bfu_asset_manager_type.BFU_BaseAssetClass] = []
    for asset in bfu_asset_manager_registred_assets.get_registred_asset_class_by_type(custom_type):
        if asset.support_asset_type(data, details):
            pass
            if asset.can_export_asset(data):
                supported_classes.append(asset)
    return supported_classes

def get_primary_supported_asset_class(data: Any, details: Any = None) -> Optional[bfu_asset_manager_type.BFU_BaseAssetClass]:
    for asset in bfu_asset_manager_registred_assets.get_registred_asset_class():
        asset: bfu_asset_manager_type.BFU_BaseAssetClass
        if asset.support_asset_type(data, details):
            return asset
    return None

def get_asset_type(data: Any, details: Any = None) -> bfu_asset_manager_type.AssetType:
    asset_class = get_primary_supported_asset_class(data, details)
    if asset_class:
        return asset_class.get_asset_type(data)
    else:
        return bfu_asset_manager_type.AssetType.UNKNOWN

def get_all_asset_class():
    return bfu_asset_manager_registred_assets.get_registred_asset_class()

