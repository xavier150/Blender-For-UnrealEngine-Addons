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
import time
from math import degrees
from . import languages
from .languages import *

if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_write_utils" in locals():
        importlib.reload(bfu_write_utils)
    if "languages" in locals():
        importlib.reload(languages)

from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_write_utils
from .bfu_write_utils import *


def WriteImportSequencerTracks():
    scene = bpy.context.scene

    data = {}
    data['Coment'] = {
        '1/3': ti('write_text_additional_track_start'),
        '2/3': ti('write_text_additional_track_camera'),
        '3/3': ti('write_text_additional_track_end'),
    }
    data['spawnable_camera'] = True  # Default but open for change
    data['startFrame'] = scene.frame_start
    data['endFrame'] = scene.frame_end
    data['frameRateDenominator'] = scene.render.fps_base
    data['frameRateNumerator'] = scene.render.fps
    data['pixel_aspect_x'] = bpy.context.scene.render.pixel_aspect_x
    data['pixel_aspect_y'] = bpy.context.scene.render.pixel_aspect_y
    data['render_resolution_x'] = bpy.context.scene.render.resolution_x
    data['render_resolution_y'] = bpy.context.scene.render.resolution_y
    data['secureCrop'] = 0.0001  # add end crop for avoid section overlay
    data['unreal_import_location'] = "/" + scene.unreal_import_module + "/" + scene.unreal_import_location

    # Import camera
    data['cameras'] = []
    for asset in scene.UnrealExportedAssetsList:
        if (asset.asset_type == "Camera"):
            camera = asset.object

            camera_data = {}
            camera_data["name"] = camera.name
            camera_data["additional_tracks_path"] = asset.GetFileByType("AdditionalTrack").GetAbsolutePath()
            data['cameras'].append(camera_data)

    def getMarkerSceneSections():
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
    for section in getMarkerSceneSections():
        marker_sections = {}
        marker_sections["start_time"] = section[0]
        marker_sections["end_time"] = section[1]
        if section[2]:
            if section[2].ExportEnum == "export_recursive" or section[2].ExportEnum == "auto":
                marker_sections["has_camera"] = True
                marker_sections["camera_name"] = section[2].name
            else:
                marker_sections["has_camera"] = False
                marker_sections["camera_name"] = ""
        else:
            marker_sections["has_camera"] = False
            marker_sections["camera_name"] = ""

        data['marker_sections'].append(marker_sections)

    return data
