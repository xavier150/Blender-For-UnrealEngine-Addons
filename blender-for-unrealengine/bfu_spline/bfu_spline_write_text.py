import bpy

from . import bfu_spline_data
from .. import languages
from .. import bfu_write_utils

def WriteSplinePointsData(obj, pre_bake_spline: bfu_spline_data.BFU_SplinesList = None):
    # Write as data spline animation tracks

    scene = bpy.context.scene

    scene = bpy.context.scene
    data = {}
    data['comment'] = {
        '1/3': languages.ti('write_text_additional_track_start'),
        '2/3': languages.ti('write_text_additional_track_spline'),
        '3/3': languages.ti('write_text_additional_track_end'),
    }

    bfu_write_utils.add_generated_json_meta_data(data)

 
    if pre_bake_spline:
        spline_tracks = pre_bake_spline.get_spline_list_values_as_dict()
    else:
        multi_spline_tracks = bfu_spline_data.BFU_MultiSplineTracks()
        multi_spline_tracks.add_spline_to_evaluate(obj)
        multi_spline_tracks.evaluate_all_splines()
        spline_tracks = multi_spline_tracks.get_evaluate_spline_data_as_dict(obj)

    data.update(spline_tracks)

    return data

