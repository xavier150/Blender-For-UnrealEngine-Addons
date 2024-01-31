# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import os
import bpy
from .. import bfu_utils

def display_asset_type_filter(obj, filter):
    """
    Check if the asset type of an object matches a given filter.

    Args:
        obj (bpy.types.Object): The object to check.
        filter (str or list of str): The filter to apply. Can be a string or a list of strings.

    Returns:
        bool: True if the asset type matches the filter, False otherwise.

    Raises:
        ValueError: If the filter is neither a string nor a list of strings.
    """
    filter_list = []
    
    if isinstance(filter, str):  # If it's a single string
        filter_list = [filter]
    elif isinstance(filter, list) and all(isinstance(item, str) for item in filter):  # If it's a list of strings
        filter_list = filter
    else:
        raise ValueError("Filter must be a string or a list of strings")

    if obj:
        asset_type = bfu_utils.GetAssetType(obj)
        if asset_type in filter_list:
            return True
    return False

def DisplayPropertyFilter(active_tab, active_sub_tab):
    # Define more easily the options which must be displayed or not

    scene = bpy.context.scene
    if scene.bfu_active_tab == active_tab == "OBJECT":
        if scene.bfu_active_object_tab == active_sub_tab or scene.bfu_active_object_tab == "ALL":
            return True

    if scene.bfu_active_tab == active_tab == "SCENE":
        if scene.bfu_active_scene_tab == active_sub_tab or scene.bfu_active_scene_tab == "ALL":
            return True
    return False



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

