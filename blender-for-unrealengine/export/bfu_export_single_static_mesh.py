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
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_naming
from .. import bfu_check_potential_error
from .. import bfu_export_logs
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
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)
    if "export_fbx_bin" in locals():
        importlib.reload(export_fbx_bin)


def ProcessStaticMeshExport(op, obj, desired_name=""):
    addon_prefs = bfu_basics.GetAddonPrefs()
    dirpath = bfu_utils.GetObjExportDir(obj)
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene
    if desired_name:
        final_name = desired_name
    else:
        final_name = obj.name

    MyAsset: bfu_export_logs.BFU_OT_UnrealExportedAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.asset_name = obj.name
    MyAsset.asset_global_scale = obj.bfu_export_global_scale
    MyAsset.folder_name = obj.bfu_export_folder_name
    MyAsset.asset_type = bfu_utils.GetAssetType(obj)

    file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
    file.file_name = bfu_naming.get_static_mesh_file_name(obj, obj.name, "")
    file.file_extension = "fbx"
    file.file_path = dirpath
    file.file_type = "FBX"

    MyAsset.StartAssetExport()
    ExportSingleStaticMesh(op, dirpath, file.GetFileWithExtension(), obj)

    if not obj.bfu_export_as_lod_mesh:
        if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
            
            file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
            file.file_name = bfu_naming.get_static_mesh_file_name(obj, final_name+"_AdditionalTrack", "")
            file.file_extension = "json"
            file.file_path = dirpath
            file.file_type = "AdditionalTrack"
            bfu_export_utils.ExportAdditionalParameter(absdirpath, file.GetFileWithExtension(), MyAsset)

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleStaticMesh(
        op,
        dirpath,
        filename,
        obj
        ):

    '''
    #####################################################
            #STATIC MESH
    #####################################################
    '''
    # Export a single Mesh

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()

    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectParentAndDesiredChilds(obj)
    asset_name = bfu_export_utils.PrepareExportName(obj, False)
    duplicate_data = bfu_export_utils.DuplicateSelectForExport()
    bfu_export_utils.SetDuplicateNameForExport(duplicate_data)

    bfu_export_utils.MakeSelectVisualReal()

    bfu_utils.ApplyNeededModifierToSelect()
    for obj in bpy.context.selected_objects:
        bfu_export_utils.SetVertexColorForUnrealExport(obj)
        bfu_export_utils.ConvertGeometryNodeAttributeToUV(obj)
        bfu_export_utils.CorrectExtremUVAtExport(obj)
        bfu_export_utils.SetSocketsExportTransform(obj)
        bfu_export_utils.SetSocketsExportName(obj)

    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active

    bfu_utils.ApplyExportTransform(active, "Object")

    meshType = bfu_utils.GetAssetType(active)

    bfu_check_potential_error.UpdateNameHierarchy(
        bfu_utils.GetAllCollisionAndSocketsObj(bpy.context.selected_objects)
        )

    asset_name.SetExportName()

    export_fbx_bin.save(
        op,
        bpy.context,
        filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
        check_existing=False,
        use_selection=True,
        global_matrix=axis_conversion(to_forward=active.bfu_export_axis_forward, to_up=active.bfu_export_axis_up).to_4x4(),
        apply_unit_scale=True,
        global_scale=bfu_utils.GetObjExportScale(active),
        apply_scale_options='FBX_SCALE_NONE',
        object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
        use_custom_props=addon_prefs.exportWithCustomProps,
        use_custom_curves=True,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        use_armature_deform_only=active.bfu_export_deform_only,
        bake_anim=False,
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF',
        use_batch_own_dir=True,
        use_metadata=addon_prefs.exportWithMetaData,
        primary_bone_axis=active.bfu_export_primary_bone_axis,
        secondary_bone_axis=active.bfu_export_secondary_bone_axis,
        mirror_symmetry_right_side_bones=active.bfu_mirror_symmetry_right_side_bones,
        use_ue_mannequin_bone_alignment=active.bfu_use_ue_mannequin_bone_alignment,
        disable_free_scale_animation=active.bfu_disable_free_scale_animation,
        axis_forward=active.bfu_export_axis_forward,
        axis_up=active.bfu_export_axis_up,
        bake_space_transform=False
        )

    asset_name.ResetNames()

    bfu_export_utils.ClearVertexColorForUnrealExport(active)
    bfu_export_utils.ResetSocketsExportName(active)
    bfu_export_utils.ResetSocketsTransform(active)
    bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    bfu_export_utils.ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)
