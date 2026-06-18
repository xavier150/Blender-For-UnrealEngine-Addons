# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Dict, List, Any, Union, Optional
from .. import bfu_export_logs
from .. import bfu_utils
from .. import bfu_export_control
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType
from . import bfu_export_text_files_utils



def write_sequencer_tracks_data(exported_asset_log: List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog]) -> Dict[str, Any]:    
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    data: Dict[str, Any] = {}
    bfu_export_text_files_utils.add_generated_json_header(data, bpy.app.translations.pgettext("It used for import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation, Pose, Camera, [...]", "interface.write_text_additional_track_all"))
    bfu_export_text_files_utils.add_generated_json_meta_data(data)

    data['spawnable_camera'] = True  # Default but open for change
    data['sequencer_frame_start'] = scene.frame_start
    data['sequencer_frame_end'] = scene.frame_end
    data['sequencer_frame_rate_denominator'] = scene.render.fps_base
    data['sequencer_frame_rate_numerator'] = scene.render.fps
    
    render = scene.render
    if render: 
        data['pixel_aspect_x'] = render.pixel_aspect_x
        data['pixel_aspect_y'] = render.pixel_aspect_y
        data['render_resolution_x'] = render.resolution_x
        data['render_resolution_y'] = render.resolution_y
    data['secure_crop'] = 0.0001  # add end crop for avoid section overlay
    data['unreal_import_location'] = bfu_utils.get_unreal_import_location()

    # Import camera
    cameras: List[Dict[str, Any]] = []
    for unreal_exported_asset in exported_asset_log:
        asset_type = unreal_exported_asset.exported_asset.asset_type
        if asset_type == AssetType.CAMERA:
            cameras.append(write_single_asset_camera_data(unreal_exported_asset))
    data['cameras'] = cameras

    def get_marker_scene_sections():
        scene = bpy.context.scene
        markersOrderly = []
        firstMarkersFrame = scene.frame_start
        lastMarkersFrame = scene.frame_end+1

        # If the scene don't use marker
        if len(bpy.context.scene.timeline_markers) < 1:
            return ([[scene.frame_start, scene.frame_end+1, bpy.context.scene.camera]])

        for marker in scene.timeline_markers:
            # Re set first frame
            if marker.frame < firstMarkersFrame:
                firstMarkersFrame = marker.frame

        for x in range(firstMarkersFrame, lastMarkersFrame):
            for marker in scene.timeline_markers:
                if marker.frame == x:
                    markersOrderly.append(marker)
        # ---
        sectionCuts = []
        for x in range(len(markersOrderly)):
            if scene.frame_end+1 > markersOrderly[x].frame:
                startTime = markersOrderly[x].frame
                if x+1 != len(markersOrderly):
                    EndTime = markersOrderly[x+1].frame
                else:
                    EndTime = scene.frame_end+1
                sectionCuts.append([startTime, EndTime, markersOrderly[x].camera])

        return sectionCuts

    data['marker_sections'] = []
    for section in get_marker_scene_sections():
        marker_sections = {}
        marker_sections["start_time"] = section[0]
        marker_sections["end_time"] = section[1]
        if section[2]:

            if bfu_export_control.bfu_export_control_utils.is_auto_or_export_recursive(section[2]):
                marker_sections["has_camera"] = True
                marker_sections["camera_name"] = section[2].name
            else:
                marker_sections["has_camera"] = False
                marker_sections["camera_name"] = ""
        else:
            marker_sections["has_camera"] = False
            marker_sections["camera_name"] = ""

        data['marker_sections'].append(marker_sections)

    bfu_export_text_files_utils.add_generated_json_footer(data)
    return data

def write_single_asset_camera_data(unreal_exported_asset: bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog) -> Dict[str, Union[str, bool, float, List[Any]]]:
    camera_data: Dict[str, Any] = {}
    camera_data["asset_name"] = unreal_exported_asset.exported_asset.name
    camera_data["files"] = unreal_exported_asset.exported_asset.get_asset_files_as_data()

    return camera_data