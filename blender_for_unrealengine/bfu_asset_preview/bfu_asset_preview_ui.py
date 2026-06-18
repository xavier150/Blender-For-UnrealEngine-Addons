# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List
from .. import bfu_cached_assets
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToSearch, AssetToExport, AssetDataSearchMode, AssetType, AssetPackage
from .. import bpl
from .. import bfu_debug_settings

def get_asset_title_text(asset_count: int, asset_to_search: AssetToSearch) -> str:
    return asset_to_search.get_asset_title_text(asset_count)

def draw_asset_preview_bar(
    layout: bpy.types.UILayout, 
    context: bpy.types.Context,
    asset_to_search: AssetToSearch = AssetToSearch.ALL_ASSETS
) -> None:

    events = bfu_debug_settings.root_events
    events.new_event("Draw Asset Preview Bar")
    events.add_sub_event("Get asset list")
    final_asset_cache = bfu_cached_assets.bfu_cached_assets_blender_class.get_final_asset_cache()
    final_asset_list_to_export = final_asset_cache.get_final_asset_list(asset_to_search, AssetDataSearchMode.ASSET_NUMBER, force_cache_update=False)

    events.stop_last_and_start_new_event("Get asset count")
    asset_count = len(final_asset_list_to_export)
    asset_info_ui = layout.row().box().split(factor=0.75)
    asset_info_text = get_asset_title_text(asset_count, asset_to_search)
    asset_info_ui.label(text=asset_info_text)
    asset_info_ui.operator("object.showasset", text="Show Assets").asset_to_search_str = asset_to_search.value
    events.stop_last_event()
    events.stop_last_event()

def draw_asset_content_line(
    layout: bpy.types.UILayout, 
    context: bpy.types.Context,
) -> bpy.types.UILayout:

    package_row = layout.row()
    package_row.alignment = "EXPAND"
    package_content_col = package_row.column()
    package_content_col.alignment = "EXPAND"
    package_content_col.scale_y = 0.8
    return package_content_col

def draw_asset_package(
    asset: AssetToExport,
    package: AssetPackage, 
    layout: bpy.types.UILayout, 
    context: bpy.types.Context
) -> None:
    
    scene = context.scene
    if scene is None:
        return
    
    package_line = draw_asset_content_line(layout, context)

    # Package name and details
    package_content_details_row = package_line.row()
    package_content_details_row.alignment = "LEFT"

    # package Title
    package_title = f"{package.name}"
    package_content_details_row.label(text=package_title)

    # Package details
    if package.details:
        package_details = f"({', '.join(package.details)})"
    else:
        package_details = ""
    package_content_details_row.label(text=f"{package_details}")

    # Package resource count
    if asset.asset_type.can_contain_objects():
        if len(package.objects) == 0:
            package_resource = "[No objects in this package]"
        elif len(package.objects) == 1:
            package_resource = f"[1 object: {package.objects[0].name}]"
        else:
            object_names = ", ".join(obj.name for obj in package.objects)
            package_resource = f"[{len(package.objects)} objects: {object_names}]"
        package_content_details_row.label(text=package_resource)

    # Package animation details
    if asset.asset_type.can_use_frame_range():
        frame_range = package.frame_range
        if frame_range is not None:
            if asset.asset_type == AssetType.ANIM_POSE:
                pose_frame_text = f"Frame: {frame_range[0]}"
                package_content_details_row.label(text=pose_frame_text)
            else:
                frame_range_text = f"Frames: {frame_range[0]}-{frame_range[1]}"
                frame_count = frame_range[1] - frame_range[0] + 1
                fps = scene.render.fps / scene.render.fps_base
                animation_duration = frame_count / fps
                animation_duration_text = bpl.utils.get_formatted_time_as_seconds(time_in_seconds=animation_duration, compact=True, min_decimals=2)
                package_content_details_row.label(text=f"{frame_range_text} ({frame_count}, {animation_duration_text}) FPS: {fps}")  # type: ignore
        else:
            package_content_details_row.label(text="No frame range set.")

    # Package file path
    package_content_file_row = package_line.row()
    package_content_file_row.alignment = "EXPAND"
    if package.file is not None:
        str_path = str(package.file.get_full_path())
        package_content_file_row.label(icon='FILE', text=str_path)
    else:
        package_content_file_row.label(icon='FILE', text="No file set for this package.")

def draw_additional_data(
    asset: AssetToExport,
    layout: bpy.types.UILayout,
    context: bpy.types.Context
) -> None:

    if asset.additional_data is not None:
        additional_data_line = draw_asset_content_line(layout, context)
        additional_data_row = additional_data_line.row()
        additional_data_row.alignment = "EXPAND"
        if asset.additional_data.file is not None:
            str_path = str(asset.additional_data.file.get_full_path())
            additional_data_row.label(icon='FILE', text=str_path)
        else:
            additional_data_row.label(icon='FILE', text="No file set for additional data.")

def draw_asset(
    asset: AssetToExport, 
    layout: bpy.types.UILayout, 
    context: bpy.types.Context
) -> None:

    asset_box = layout.box()
    asset_box.alignment = 'LEFT'
    asset_row = asset_box.row()
    asset_row.alignment = 'EXPAND'
    asset_row.scale_y = 0.8

    # Asset name and type
    asset_info = asset_row.row()
    asset_info.alignment = 'LEFT'
    asset_name = f"- {asset.name} ({asset.asset_type.get_friendly_name()})"
    asset_info.label(text=asset_name)

    # Asset Pakages
    asset_col = asset_row.column()
    asset_col.alignment = 'EXPAND'
    for package in asset.asset_packages:
        draw_asset_package(asset, package, asset_col, context)
    draw_additional_data(asset, asset_col, context)

def draw_assets_list(
    layout: bpy.types.UILayout, 
    context: bpy.types.Context, 
    asset_to_count: AssetToSearch,
    final_asset_list_to_export: List[AssetToExport]
) -> None:

    # Popup title
    popup_title = get_asset_title_text(len(final_asset_list_to_export), asset_to_count)
    layout.label(text=popup_title, icon='PACKAGE')

    for asset in final_asset_list_to_export:
        draw_asset(asset, layout, context)


        '''
        if asset.obj is not None:

            
            if asset.action is not None:
                if (type(asset.action) is bpy.types.Action):
                    # Action name
                    action = asset.action.name
                elif (type(asset.action) is bpy.types.AnimData):
                    # Nonlinear name
                    action = asset.obj.bfu_anim_nla_export_name
                else:
                    action = "..."
                row.label(
                    text="- ["+asset.name+"] --> " +
                    action+" ("+asset.asset_type.get_friendly_name()+")")
            else:
                if asset.asset_type != "Collection StaticMesh":
                    row.label(
                        text="- "+asset.name +
                        " ("+asset.asset_type.get_friendly_name()+")")
                else:
                    row.label(
                        text="- "+asset.obj.name +
                        " ("+asset.asset_type.get_friendly_name()+")")
            
        else:
            row.label(text="- ("+asset.asset_type.get_friendly_name()+")")
        '''