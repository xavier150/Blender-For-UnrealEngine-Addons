import bpy

from . import bfu_spline_write_text
from . import bfu_spline_data
from .. import bfu_basics
from .. import bfu_write_text

def ExportSingleAdditionalTrackspline(dirpath, filename, obj, pre_bake_spline: bfu_spline_data.BFU_SplineTracks = None):
    # Export additional spline track for Unreal Engine
    # FocalLength
    # FocusDistance
    # Aperture

    absdirpath = bpy.path.abspath(dirpath)
    bfu_basics.VerifiDirs(absdirpath)
    AdditionalTrack = bfu_spline_write_text.WritesplineAnimationTracks(obj, pre_bake_spline=pre_bake_spline)
    return bfu_write_text.ExportSingleJson(
        AdditionalTrack,
        absdirpath,
        filename
        )