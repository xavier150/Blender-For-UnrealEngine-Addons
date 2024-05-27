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
from bpy_extras.io_utils import axis_conversion
from . import bfu_export_utils
from .. import bfu_camera
from .. import bps
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_naming
from .. import bfu_export_logs
from .. import bfu_assets_manager
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


def ProcessCameraExport(op, obj, pre_bake_camera: bfu_camera.bfu_camera_data.BFU_CameraTracks = None):
    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()

    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
    asset_type = asset_class.get_asset_type_name(obj)
    dirpath = asset_class.get_obj_export_directory_path(obj)
    file_name = asset_class.get_obj_file_name(obj, obj.name, "")
    file_name_at = asset_class.get_obj_file_name(obj, obj.name+"_AdditionalTrack", "") 

    MyAsset: bfu_export_logs.BFU_OT_UnrealExportedAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.asset_name = obj.name
    MyAsset.asset_global_scale = obj.bfu_export_global_scale
    MyAsset.folder_name = obj.bfu_export_folder_name
    MyAsset.asset_type = asset_type
    MyAsset.animation_start_frame = scene.frame_start
    MyAsset.animation_end_frame = scene.frame_end+1
    MyAsset.StartAssetExport()

    if obj.bfu_export_fbx_camera:
        file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
        file.file_name = file_name
        file.file_extension = "fbx"
        file.file_path = dirpath
        file.file_type = "FBX"

        ExportSingleFbxCamera(op, dirpath, file.GetFileWithExtension(), obj)

    if scene.text_AdditionalData and addon_prefs.useGeneratedScripts:

        file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
        file.file_name = file_name_at
        file.file_extension = "json"
        file.file_path = dirpath
        file.file_type = "AdditionalTrack"
        bfu_camera.bfu_camera_export_utils.ExportSingleAdditionalTrackCamera(dirpath, file.GetFileWithExtension(), obj, pre_bake_camera)

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleFbxCamera(
        op,
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
    addon_prefs = bfu_basics.GetAddonPrefs()

    filename = bfu_basics.ValidFilename(filename)
    if obj.type != 'CAMERA':
        return

    bbpl.utils.safe_mode_set('OBJECT')

    # Select and rescale camera for export
    bpy.ops.object.select_all(action='DESELECT')
    bbpl.utils.select_specific_object(obj)

    obj.delta_scale *= 0.01
    if obj.animation_data is not None:
        action = obj.animation_data.action
        scene.frame_start = bfu_utils.GetDesiredActionStartEndTime(obj, action)[0]
        scene.frame_end = bfu_utils.GetDesiredActionStartEndTime(obj, action)[1]

    export_fbx_camera = obj.bfu_export_fbx_camera
    camera_export_procedure = obj.bfu_camera_export_procedure

    if (camera_export_procedure == "ue-standard") and export_fbx_camera:
        export_fbx_bin.save(
            op,
            bpy.context,
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_matrix=axis_conversion(to_forward=obj.bfu_export_axis_forward, to_up=obj.bfu_export_axis_up).to_4x4(),
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(obj),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'CAMERA'},
            use_custom_props=obj.bfu_export_with_custom_props,
            add_leaf_bones=False,
            use_armature_deform_only=obj.bfu_export_deform_only,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_utils.GetAnimSample(obj),
            bake_anim_simplify_factor=obj.bfu_simplify_anim_for_export,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=obj.bfu_export_with_meta_data,
            primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(obj),
            secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(obj),
            mirror_symmetry_right_side_bones=obj.bfu_mirror_symmetry_right_side_bones,
            use_ue_mannequin_bone_alignment=obj.bfu_use_ue_mannequin_bone_alignment,
            disable_free_scale_animation=obj.bfu_disable_free_scale_animation,
            use_space_transform=bfu_export_utils.get_static_export_use_space_transform(obj),
            axis_forward=bfu_export_utils.get_static_export_axis_forward(obj),
            axis_up=bfu_export_utils.get_static_export_axis_up(obj),
            bake_space_transform=False
            )
    elif (camera_export_procedure == "blender-standard") and export_fbx_camera:
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            apply_unit_scale=True,
            global_scale=bfu_utils.GetObjExportScale(obj),
            apply_scale_options='FBX_SCALE_NONE',
            object_types={'CAMERA'},
            use_custom_props=obj.bfu_export_with_custom_props,
            add_leaf_bones=False,
            use_armature_deform_only=obj.bfu_export_deform_only,
            bake_anim=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=bfu_utils.GetAnimSample(obj),
            bake_anim_simplify_factor=obj.bfu_simplify_anim_for_export,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=obj.bfu_export_with_meta_data,
            primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(obj),
            secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(obj),
            use_space_transform=bfu_export_utils.get_static_export_use_space_transform(obj),
            axis_forward=bfu_export_utils.get_static_export_axis_forward(obj),
            axis_up=bfu_export_utils.get_static_export_axis_up(obj),
            bake_space_transform=False
            )

    # Reset camera scale
    obj.delta_scale *= 100

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)
