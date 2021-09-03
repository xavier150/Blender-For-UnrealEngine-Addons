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
import time
import math

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)
    if "bfu_export_utils" in locals():
        importlib.reload(bfu_export_utils)


from .. import bfu_write_text
from .. import bfu_basics
from ..bfu_basics import *
from .. import bfu_utils
from ..bfu_utils import *
from .. import bfu_check_potential_error

from . import bfu_export_utils
from .bfu_export_utils import *


def ProcessCameraExport(obj):
    addon_prefs = GetAddonPrefs()
    counter = CounterTimer()
    dirpath = GetObjExportDir(obj)
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.StartAssetExport(obj)

    if obj.bfu_export_fbx_camera:
        ExportSingleFbxCamera(
            dirpath,
            GetObjExportFileName(obj),
            obj
            )
        file = MyAsset.files.add()
        file.name = GetObjExportFileName(obj)
        file.path = dirpath
        file.type = "FBX"

    if obj.ExportAsLod is False:
        if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
            ExportSingleAdditionalTrackCamera(
                dirpath,
                GetObjExportFileName(obj, "_AdditionalTrack.json"),
                obj
                )
            file = MyAsset.files.add()
            file.name = GetObjExportFileName(obj, "_AdditionalTrack.json")
            file.path = dirpath
            file.type = "AdditionalTrack"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleFbxCamera(
        dirpath,
        filename,
        obj
        ):

    '''
    #####################################################
            #CAMERA
    #####################################################
    '''
    # Export single camera

    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()

    filename = ValidFilename(filename)
    if obj.type != 'CAMERA':
        return

    SafeModeSet('OBJECT')

    # Select and rescale camera for export
    bpy.ops.object.select_all(action='DESELECT')
    SelectSpecificObject(obj)

    obj.delta_scale *= 0.01
    if obj.animation_data is not None:
        action = obj.animation_data.action
        scene.frame_start = GetDesiredActionStartEndTime(obj, action)[0]
        scene.frame_end = GetDesiredActionStartEndTime(obj, action)[1]

    ExportCameraAsFBX = addon_prefs.exportCameraAsFBX
    if ExportCameraAsFBX:
        bpy.ops.export_scene.fbx(
            filepath=GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_scale=GetObjExportScale(obj),
            object_types={'CAMERA'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            add_leaf_bones=False,
            use_armature_deform_only=obj.exportDeformOnly,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=GetAnimSample(obj),
            bake_anim_simplify_factor=obj.SimplifyAnimForExport,
            use_metadata=addon_prefs.exportWithMetaData,
            primary_bone_axis=obj.exportPrimaryBaneAxis,
            secondary_bone_axis=obj.exporSecondaryBoneAxis,
            axis_forward=obj.exportAxisForward,
            axis_up=obj.exportAxisUp,
            bake_space_transform=False
            )

    # Reset camera scale
    obj.delta_scale *= 100

    for obj in scene.objects:
        ClearAllBFUTempVars(obj)