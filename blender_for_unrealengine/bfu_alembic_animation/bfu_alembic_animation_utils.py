# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Tuple
from .. import bfu_assets_manager


def is_alembic_animation(obj: bpy.types.Object) -> bool:
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type(obj) == bfu_assets_manager.bfu_asset_manager_type.AssetType.ANIM_ALEMBIC:
            return True
    return False

def is_not_alembic_animation(obj: bpy.types.Object) -> bool:
    return not is_alembic_animation(obj)

def get_desired_alembic_start_end_range(obj: bpy.types.Object) -> Tuple[float, float]:
    # Returns desired alembic anim start/end time
    scene = bpy.context.scene
    if scene is None:
        raise Exception("No active scene found")
    
    return (scene.frame_start, scene.frame_end)