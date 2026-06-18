# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List, Dict
from .bfu_asset_manager_type import BFU_BaseAssetClass

registred_asset_class: List[BFU_BaseAssetClass] = []
registred_asset_class_by_type: Dict[str, List[BFU_BaseAssetClass]] = {}

def register_asset_class(asset: BFU_BaseAssetClass, custom_type: str = ""):
    registred_asset_class.append(asset)
    if custom_type:
        if custom_type not in registred_asset_class_by_type:
            registred_asset_class_by_type[custom_type] = []
        registred_asset_class_by_type[custom_type].append(asset)

def get_registred_asset_class() -> List[BFU_BaseAssetClass]:
    return registred_asset_class

def get_registred_asset_class_by_type(asset_type: str) -> List[BFU_BaseAssetClass]:
    return registred_asset_class_by_type.get(asset_type, [])
