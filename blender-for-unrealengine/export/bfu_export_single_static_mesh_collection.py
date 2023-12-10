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

def ProcessCollectionExport(op, col):

    addon_prefs = bfu_basics.GetAddonPrefs()
    dirpath = bfu_utils.GetCollectionExportDir(bpy.data.collections[col.name])
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset: bfu_export_logs.BFU_OT_UnrealExportedAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.asset_name = col.name
    MyAsset.asset_global_scale = 1.0 #col.bfu_export_global_scale
    MyAsset.collection = col
    MyAsset.asset_type = bfu_utils.GetCollectionType(col)
    MyAsset.folder_name = col.bfu_export_folder_name

    file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
    file.file_name = bfu_naming.get_collection_file_name(col, col.name, "")
    file.file_extension = "fbx"
    file.file_path = dirpath
    file.file_type = "FBX"

    MyAsset.StartAssetExport()
    ExportSingleStaticMeshCollection(op, dirpath, file.GetFileWithExtension(), col.name)

    if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
        
        file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
        file.file_name = bfu_naming.get_collection_file_name(col, col.name+"_AdditionalTrack", "")
        file.file_extension = "json"
        file.file_path = dirpath
        file.file_type = "AdditionalTrack"
        bfu_export_utils.ExportAdditionalParameter(absdirpath, file.GetFileWithExtension(), MyAsset)

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleStaticMeshCollection(
        op,
        dirpath,
        filename,
        collection_name
        ):

    '''
    #####################################################
            #COLLECTION
    #####################################################
    '''
    # Export a single collection

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    col = bpy.data.collections[collection_name]

    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectCollectionObjects(col)
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

    bfu_check_potential_error.UpdateNameHierarchy(
        bfu_utils.GetAllCollisionAndSocketsObj(bpy.context.selected_objects)
        )
    
    static_export_procedure = col.bfu_collection_export_procedure

    if (static_export_procedure == "ue-standard"):
        export_fbx_bin.save(
            operator=op,
            context=bpy.context,
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_scale=1,
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            use_custom_curves=True,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            # use_armature_deform_only=active.bfu_export_deform_only,
            bake_anim=False,
            use_metadata=addon_prefs.exportWithMetaData,
            # primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(obj),
            # secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(obj),
            # axis_forward=bfu_export_utils.get_export_axis_forward(obj),
            # axis_up=bfu_export_utils.get_export_axis_up(obj),
            bake_space_transform=False
            )
    elif (static_export_procedure == "blender-standard"):
        bpy.ops.export_scene.fbx(
            filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
            check_existing=False,
            use_selection=True,
            global_scale=1,
            object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
            use_custom_props=addon_prefs.exportWithCustomProps,
            mesh_smooth_type="FACE",
            add_leaf_bones=False,
            # use_armature_deform_only=active.bfu_export_deform_only,
            bake_anim=False,
            use_metadata=addon_prefs.exportWithMetaData,
            # primary_bone_axis=bfu_export_utils.get_final_export_primary_bone_axis(obj),
            # secondary_bone_axis=bfu_export_utils.get_final_export_secondary_bone_axis(obj),
            # axis_forward=bfu_export_utils.get_export_axis_forward(obj),
            # axis_up=bfu_export_utils.get_export_axis_up(obj),
            bake_space_transform=False
            )
    
    for obj in bpy.context.selected_objects:
        bfu_export_utils.ClearVertexColorForUnrealExport(obj)
        bfu_export_utils.ResetSocketsExportName(obj)
        bfu_export_utils.ResetSocketsTransform(obj)

    bfu_utils.CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    bfu_export_utils.ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)


def CleanSingleStaticMeshCollection(obj):
    # Remove the created collection
    bbpl.utils.select_specific_object(obj)
