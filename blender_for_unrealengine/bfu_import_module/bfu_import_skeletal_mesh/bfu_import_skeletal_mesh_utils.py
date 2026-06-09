# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import Any, Dict, Optional, cast
import unreal
from .. import import_module_unreal_utils
from ..asset_types import ExportAssetType

def get_origin_skeleton_and_skeletal_mesh(
    asset_data: Dict[str, Any],
    asset_type: ExportAssetType,
) -> tuple[Optional[unreal.Skeleton], Optional[unreal.SkeletalMesh]]:

    if asset_type.is_skeletal():
        origin_skeleton: Optional[unreal.Skeleton] = None
        origin_skeletal_mesh: Optional[unreal.SkeletalMesh] = None


        if "target_skeleton_search_ref" in asset_data:
            find_sk_asset = import_module_unreal_utils.load_asset(asset_data["target_skeleton_search_ref"])
            if isinstance(find_sk_asset, unreal.SkeletalMesh):
                origin_skeleton = cast(Optional[unreal.Skeleton], getattr(find_sk_asset, "skeleton", None))
                origin_skeletal_mesh = find_sk_asset
            elif isinstance(find_sk_asset, unreal.Skeleton):
                origin_skeleton = find_sk_asset


        if "target_skeletal_mesh_search_ref" in asset_data:
            find_skm_asset = import_module_unreal_utils.load_asset(asset_data["target_skeletal_mesh_search_ref"])
            if isinstance(find_skm_asset, unreal.SkeletalMesh):
                origin_skeleton = cast(Optional[unreal.Skeleton], getattr(find_skm_asset, "skeleton", None))
                origin_skeletal_mesh = find_skm_asset
            elif isinstance(find_skm_asset, unreal.Skeleton):
                origin_skeleton = find_skm_asset
                
        if asset_type in [ExportAssetType.ANIM_ACTION, ExportAssetType.ANIM_POSE, ExportAssetType.ANIM_NLA]:
            skeleton_search_str = f'"target_skeleton_search_ref": {asset_data["target_skeleton_search_ref"]}'
            skeletal_mesh_search_str = f'"target_skeletal_mesh_search_ref": {asset_data["target_skeletal_mesh_search_ref"]}'
    
            if origin_skeleton:
                print(f'{skeleton_search_str} and "{skeletal_mesh_search_str} "was found for animation immport:" {str(origin_skeleton)}')
            else:
                message = "WARNING: Could not find skeleton for animation import." + "\n"
                message += f" -{skeleton_search_str}" + "\n"
                message += f" -{skeletal_mesh_search_str}" + "\n"
                import_module_unreal_utils.show_warning_message("Skeleton not found.", message)
       
        return origin_skeleton, origin_skeletal_mesh
    return None, None