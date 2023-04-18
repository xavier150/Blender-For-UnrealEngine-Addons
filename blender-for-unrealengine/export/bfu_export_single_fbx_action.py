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


def ProcessActionExport(obj, action):
    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()
    dirpath = os.path.join(GetObjExportDir(obj), scene.anim_subfolder_name)

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.skeleton_name = obj.name
    MyAsset.asset_name = bfu_utils.GetActionExportFileName(obj, action, "")
    MyAsset.folder_name = obj.exportFolderName
    MyAsset.asset_type = bfu_utils.GetActionType(action)

    MyAsset.StartAssetExport()

    ExportSingleFbxAction(scene, dirpath, GetActionExportFileName(obj, action), obj, action)
    file = MyAsset.files.add()
    file.name = GetActionExportFileName(obj, action)
    file.path = dirpath
    file.type = "FBX"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleFbxAction(
        originalScene,
        dirpath,
        filename,
        obj,
        targetAction
        ):

    '''
    #####################################################
            #SKELETAL ACTION
    #####################################################
    '''
    # Export a single action like a animation or pose

    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()
    export_as_proxy = GetExportAsProxy(obj)
    export_proxy_child = GetExportProxyChild(obj)

    if obj.animation_data is None:
        obj.animation_data_create()
    userAction = obj.animation_data.action  # Save current action
    userAction_extrapolation = obj.animation_data.action_extrapolation
    userAction_blend_type = obj.animation_data.action_blend_type
    userAction_influence = obj.animation_data.action_influence

    bbpl.utils.SafeModeSet('OBJECT')

    SelectParentAndDesiredChilds(obj)
    asset_name = PrepareExportName(obj, True)
    if export_as_proxy is False:
        duplicate_data = DuplicateSelectForExport()
        SetDuplicateNameForExport(duplicate_data)

    if export_as_proxy is False:
        MakeSelectVisualReal()

    BaseTransform = obj.matrix_world.copy()
    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active
    if export_as_proxy:
        ApplyProxyData(active)

    scene.frame_start = GetDesiredActionStartEndTime(active, targetAction)[0]
    scene.frame_end = GetDesiredActionStartEndTime(active, targetAction)[1]

    if export_as_proxy:
        if export_proxy_child is not None:
            obj.animation_data.action = targetAction  # Apply desired action
        RemoveSocketFromSelectForProxyArmature()

    active.animation_data.action = targetAction  # Apply desired action
    export_procedure = active.bfu_export_procedure

    if addon_prefs.bakeArmatureAction:
        BakeArmatureAnimation(active, scene.frame_start, scene.frame_end)

    ApplyExportTransform(active, "Action")  # Apply export transform before rescale

    # This will rescale the rig and unit scale to get a root bone egal to 1
    ShouldRescaleRig = GetShouldRescaleRig(active)
    if ShouldRescaleRig:

        rrf = GetRescaleRigFactor()  # rigRescaleFactor
        my_scene_unit_settings = bfu_utils.SceneUnitSettings(bpy.context.scene)

        my_skeletal_export_scale = bfu_utils.SkeletalExportScale(active)
        my_skeletal_export_scale.ApplySkeletalExportScale(rrf, is_a_proxy=export_as_proxy)
        my_action_curve_scale = bfu_utils.ActionCurveScale(rrf*active.scale.z)
        my_action_curve_scale.ResacleForUnrealEngine()
        my_shape_keys_curve_scale = bfu_utils.ShapeKeysCurveScale(rrf, is_a_proxy=export_as_proxy)
        my_shape_keys_curve_scale.ResacleForUnrealEngine()

        RescaleSelectCurveHook(1/rrf)
        ResetArmaturePose(active)
        my_rig_consraints_scale = bfu_utils.RigConsraintScale(active, rrf)
        my_rig_consraints_scale.RescaleRigConsraintForUnrealEngine()

    # animation_data.action is ReadOnly with tweakmode in 2.8
    if (scene.is_nla_tweakmode):
        active.animation_data.use_tweak_mode = False

    if addon_prefs.ignoreNLAForAction:  # Reset NLA
        active.animation_data.action_extrapolation = 'HOLD'
        active.animation_data.action_blend_type = 'REPLACE'
        active.animation_data.action_influence = 1

    asset_name.SetExportName()

    if (export_procedure == "normal"):
        bpy.ops.export_scene.fbx(
            filepath=GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_scale=GetObjExportScale(active),
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.exportDeformOnly,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=GetAnimSample(active),
            bake_anim_simplify_factor=active.SimplifyAnimForExport,
            use_metadata=addon_prefs.exportWithMetaData,
            primary_bone_axis=active.exportPrimaryBaneAxis,
            secondary_bone_axis=active.exporSecondaryBoneAxis,
            axis_forward=active.exportAxisForward,
            axis_up=active.exportAxisUp,
            bake_space_transform=False
            )

    elif (export_procedure == "auto-rig-pro"):

        # Rename Action name for export
        TempName = "ActionAutoRigProTempExportNameForUnreal"
        OriginalActionName = active.animation_data.action.name
        active.animation_data.action.name = TempName

        ExportAutoProRig(
            filepath=GetExportFullpath(dirpath, filename),
            # export_rig_name=GetDesiredExportArmatureName(active),
            bake_anim=True,
            anim_export_name_string=active.animation_data.action.name,
            mesh_smooth_type="FACE",
            arp_simplify_fac=active.SimplifyAnimForExport
            )

        # Reset Action name
        active.animation_data.action.name = OriginalActionName

    asset_name.ResetNames()

    ResetArmaturePose(obj)

    obj.animation_data.action = userAction  # Resets previous action and NLA
    if addon_prefs.ignoreNLAForAction:
        obj.animation_data.action_extrapolation = userAction_extrapolation
        obj.animation_data.action_blend_type = userAction_blend_type
        obj.animation_data.action_influence = userAction_influence

    # Reset Transform
    obj.matrix_world = BaseTransform

    # This will rescale the rig and unit scale to get a root bone egal to 1
    if ShouldRescaleRig:
        my_rig_consraints_scale.ResetScaleAfterExport()
        my_skeletal_export_scale.ResetSkeletalExportScale()
        my_scene_unit_settings.ResetUnit()
        my_action_curve_scale.ResetScaleAfterExport()
        my_shape_keys_curve_scale.ResetScaleAfterExport()

    if export_as_proxy is False:
        CleanDeleteObjects(bpy.context.selected_objects)
        for data in duplicate_data.data_to_remove:
            data.RemoveData()

        ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        ClearAllBFUTempVars(obj)
