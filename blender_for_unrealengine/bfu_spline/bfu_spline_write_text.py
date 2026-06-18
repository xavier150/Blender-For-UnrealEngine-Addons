# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Any, Optional, Dict
from . import bfu_spline_data
from .. import bfu_export_text_files

def write_spline_points_data(obj: bpy.types.Object, pre_bake_spline: Optional[bfu_spline_data.BFU_SplinesList] = None) -> Dict[str, Any]:
    # Write as data spline animation tracks


    data: Dict[str, Any] = {}
    bfu_export_text_files.bfu_export_text_files_utils.add_generated_json_header(data, bpy.app.translations.pgettext("This file contains additional Spline data informations that is not supported with .fbx files", "interface.write_text_additional_track_spline"))
    bfu_export_text_files.bfu_export_text_files_utils.add_generated_json_meta_data(data)

 
    if pre_bake_spline:
        spline_tracks = pre_bake_spline.get_spline_list_values_as_dict()
    else:
        multi_spline_tracks = bfu_spline_data.BFU_MultiSplineTracks()
        multi_spline_tracks.add_spline_to_evaluate(obj)
        multi_spline_tracks.evaluate_all_splines()
        spline_tracks = multi_spline_tracks.get_evaluate_spline_data_as_dict(obj)
    data.update(spline_tracks)

    bfu_export_text_files.bfu_export_text_files_utils.add_generated_json_footer(data)
    return data

