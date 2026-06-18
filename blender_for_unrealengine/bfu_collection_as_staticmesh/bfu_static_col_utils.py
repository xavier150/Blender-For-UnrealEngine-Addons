# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import List
import bpy
from .. import bfu_export_filter
from .. import bfu_debug_settings
from . import bfu_static_col_props

def support_static_collection_export(scene: bpy.types.Scene) -> bool:
    return bfu_export_filter.bfu_export_filter_props.scene_use_static_collection_export(scene)

def optimized_collection_search(scene: bpy.types.Scene) -> List[bpy.types.Collection]:
    if not support_static_collection_export(scene):
        return []

    events = bfu_debug_settings.root_events
    collection_list: List[bpy.types.Collection] = []

    events.add_sub_event(f'Export Specific Collection List')
    for target_col in bfu_static_col_props.scene_static_collection_asset_list(scene):
        if target_col.use:
            # No need to check if not collection.library: because alredsy checked in scene_collection_asset_list
            if target_col.name in bpy.data.collections:
                collection_list.append(bpy.data.collections[target_col.name])
    events.stop_last_event()

    return collection_list

