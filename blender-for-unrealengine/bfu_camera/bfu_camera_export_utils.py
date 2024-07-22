import bpy

from . import bfu_camera_write_text
from . import bfu_camera_data
from .. import bfu_basics
from .. import bfu_write_text

def ExportSingleAdditionalTrackCamera(dirpath, filename, obj: bpy.types.Object, pre_bake_camera: bfu_camera_data.BFU_CameraTracks = None):
    # Export additional camera track for Unreal Engine
    # FocalLength
    # FocusDistance
    # Aperture

    absdirpath = bpy.path.abspath(dirpath)
    bfu_basics.VerifiDirs(absdirpath)
    AdditionalTrack = bfu_camera_write_text.WriteCameraAnimationTracks(obj, pre_bake_camera=pre_bake_camera)
    return bfu_write_text.ExportSingleJson(
        AdditionalTrack,
        absdirpath,
        filename
        )

