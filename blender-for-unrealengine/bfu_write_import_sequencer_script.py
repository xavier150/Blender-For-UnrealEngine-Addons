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

import bpy
from . import languages
from . import bfu_write_utils


def WriteImportSequencerTracks():
    scene = bpy.context.scene

    data = {}
    data['comment'] = {
        '1/3': languages.ti('write_text_additional_track_start'),
        '2/3': languages.ti('write_text_additional_track_all'),
        '3/3': languages.ti('write_text_additional_track_end'),
    }

    bfu_write_utils.add_generated_json_meta_data(data)

    data['spawnable_camera'] = True  # Default but open for change
    data['sequencer_frame_start'] = scene.frame_start
    data['sequencer_frame_end'] = scene.frame_end
    data['sequencer_frame_rate_denominator'] = scene.render.fps_base
    data['sequencer_frame_rate_numerator'] = scene.render.fps
    data['pixel_aspect_x'] = bpy.context.scene.render.pixel_aspect_x
    data['pixel_aspect_y'] = bpy.context.scene.render.pixel_aspect_y
    data['render_resolution_x'] = bpy.context.scene.render.resolution_x
    data['render_resolution_y'] = bpy.context.scene.render.resolution_y
    data['secureCrop'] = 0.0001  # add end crop for avoid section overlay
    data['bfu_unreal_import_location'] = "/" + scene.bfu_unreal_import_module + "/" + scene.bfu_unreal_import_location

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
            if section[2].bfu_export_type == "export_recursive" or section[2].bfu_export_type == "auto":
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
