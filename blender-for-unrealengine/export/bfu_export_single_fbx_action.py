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
from bpy_extras.io_utils import axis_conversion
from . import bfu_export_utils
from .. import bfu_basics
from .. import bfu_utils
from .. import bbpl
from ..fbxio import export_fbx_bin

if "bpy" in locals():
    import importlib
    if "bfu_export_utils" in locals():
        importlib.reload(bfu_export_utils)
    if "bbpl" in locals():
        importlib.reload(bbpl)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "export_fbx_bin" in locals():
        importlib.reload(export_fbx_bin)


def ProcessActionExport(op, obj, action, action_curve_scale):
    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    dirpath = os.path.join(bfu_utils.GetObjExportDir(obj), scene.anim_subfolder_name)

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.skeleton_name = obj.name
    MyAsset.asset_name = bfu_utils.GetActionExportFileName(obj, action, "")
    MyAsset.asset_global_scale = obj.exportGlobalScale
    MyAsset.folder_name = obj.bfu_export_folder_name
    MyAsset.asset_type = bfu_utils.GetActionType(action)

    MyAsset.StartAssetExport()

    filename = bfu_utils.GetActionExportFileName(obj, action)
    action_curve_scale = ExportSingleFbxAction(op, scene, dirpath, filename, obj, action, action_curve_scale)

    file = MyAsset.files.add()
    file.name = filename
    file.path = dirpath
    file.type = "FBX"

    MyAsset.EndAssetExport(True)
    return action_curve_scale


def ExportSingleFbxAction(
        op,
        originalScene,
        dirpath,
        filename,
        obj,
        targetAction,
        action_curve_scale
        ):

    '''
    #####################################################
            #SKELETAL ACTION
    #####################################################
    '''
    # Export a single action like a animation or pose

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    export_as_proxy = bfu_utils.GetExportAsProxy(obj)
    export_proxy_child = bfu_utils.GetExportProxyChild(obj)

    if obj.animation_data is None:
        obj.animation_data_create()
    userAction = obj.animation_data.action  # Save current action
    userAction_extrapolation = obj.animation_data.action_extrapolation
    userAction_blend_type = obj.animation_data.action_blend_type
    userAction_influence = obj.animation_data.action_influence

    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectParentAndDesiredChilds(obj)
    asset_name = bfu_export_utils.PrepareExportName(obj, True)
    if export_as_proxy is False:
        duplicate_data = bfu_export_utils.DuplicateSelectForExport()
        bfu_export_utils.SetDuplicateNameForExport(duplicate_data)

    if export_as_proxy is False:
        bfu_export_utils.MakeSelectVisualReal()

    BaseTransform = obj.matrix_world.copy()
    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active
    if export_as_proxy:
        bfu_export_utils.ApplyProxyData(active)

    scene.frame_start = bfu_utils.GetDesiredActionStartEndTime(active, targetAction)[0]
    scene.frame_end = bfu_utils.GetDesiredActionStartEndTime(active, targetAction)[1]

    if export_as_proxy:
        if export_proxy_child is not None:
            obj.animation_data.action = targetAction  # Apply desired action
        bfu_utils.RemoveSocketFromSelectForProxyArmature()

    active.animation_data.action = targetAction  # Apply desired action
    export_procedure = active.bfu_export_procedure

    if addon_prefs.bakeArmatureAction:
        bfu_export_utils.BakeArmatureAnimation(active, scene.frame_start, scene.frame_end)

    bfu_utils.ApplyExportTransform(active, "Action")  # Apply export transform before rescale

    # This will rescale the rig and unit scale to get a root bone egal to 1
    ShouldRescaleRig = bfu_export_utils.GetShouldRescaleRig(active)
    if ShouldRescaleRig:

        rrf = bfu_export_utils.GetRescaleRigFactor()  # rigRescaleFactor
        my_scene_unit_settings = bfu_utils.SceneUnitSettings(bpy.context.scene)
        my_scene_unit_settings.SetUnitForUnrealEngineExport()
        my_skeletal_export_scale = bfu_utils.SkeletalExportScale(active)
        my_skeletal_export_scale.ApplySkeletalExportScale(rrf, is_a_proxy=export_as_proxy)
        if not action_curve_scale:
            action_curve_scale = bfu_utils.ActionCurveScale(rrf*active.scale.z)
            action_curve_scale.ResacleForUnrealEngine()
        my_shape_keys_curve_scale = bfu_utils.ShapeKeysCurveScale(rrf, is_a_proxy=export_as_proxy)
        my_shape_keys_curve_scale.ResacleForUnrealEngine()

        bfu_utils.RescaleSelectCurveHook(1/rrf)
        bbpl.anim_utils.reset_armature_pose(active)
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

    if (export_procedure == "ue-standard"):
        export_fbx_bin.save(
            operator=op,
            context=bpy.context,
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            animation_only=True,
            global_matrix=axis_conversion(to_forward=active.exportAxisForward, to_up=active.exportAxisUp).to_4x4(),
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            use_custom_curves=True,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.exportDeformOnly,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_utils.GetAnimSample(active),
            bake_anim_simplify_factor=active.SimplifyAnimForExport,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=addon_prefs.exportWithMetaData,
            primary_bone_axis=active.exportPrimaryBoneAxis,
            secondary_bone_axis=active.exportSecondaryBoneAxis,
            mirror_symmetry_right_side_bones=active.bfu_mirror_symmetry_right_side_bones,
            use_ue_mannequin_bone_alignment=active.bfu_use_ue_mannequin_bone_alignment,
            disable_free_scale_animation=active.bfu_disable_free_scale_animation,
            axis_forward=active.exportAxisForward,
            axis_up=active.exportAxisUp,
            bake_space_transform=False
            )
    elif (export_procedure == "blender-standard"):
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(active),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            use_armature_deform_only=active.exportDeformOnly,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_utils.GetAnimSample(active),
            bake_anim_simplify_factor=active.SimplifyAnimForExport,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=addon_prefs.exportWithMetaData,
            primary_bone_axis=active.exportPrimaryBoneAxis,
            secondary_bone_axis=active.exportSecondaryBoneAxis,
            axis_forward=active.exportAxisForward,
            axis_up=active.exportAxisUp,
            bake_space_transform=False
            )
    elif (export_procedure == "auto-rig-pro"):

        # Rename Action name for export
        TempName = "ActionAutoRigProTempExportNameForUnreal"
        OriginalActionName = active.animation_data.action.name
        active.animation_data.action.name = TempName

        export_fbx_bin.save(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            # export_rig_name=GetDesiredExportArmatureName(active),
            bake_anim=True,
            anim_export_name_string=active.animation_data.action.name,
            mesh_smooth_type="FACE",
            arp_simplify_fac=active.SimplifyAnimForExport
            )

        # Reset Action name
        active.animation_data.action.name = OriginalActionName

    asset_name.ResetNames()

    bbpl.anim_utils.reset_armature_pose(obj)

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
        my_shape_keys_curve_scale.ResetScaleAfterExport()

    if export_as_proxy is False:
        bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
        for data in duplicate_data.data_to_remove:
            data.RemoveData()

        bfu_export_utils.ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)

    return action_curve_scale
