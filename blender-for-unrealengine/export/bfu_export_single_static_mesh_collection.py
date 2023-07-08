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
    if "bfu_export_single_static_mesh" in locals():
        importlib.reload(bfu_export_single_static_mesh)


from .. import bfu_write_text
from .. import bfu_basics
from ..bfu_basics import *
from .. import bfu_utils
from ..bfu_utils import *
from .. import bfu_check_potential_error

from . import bfu_export_utils
from .bfu_export_utils import *
from . import bfu_export_single_static_mesh
from .bfu_export_single_static_mesh import *


def ProcessCollectionExport(col):

    addon_prefs = GetAddonPrefs()
    dirpath = GetCollectionExportDir(bpy.data.collections[col.name])
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.asset_name = col.name
    MyAsset.collection = col
    MyAsset.asset_type = bfu_utils.GetCollectionType(col)
    MyAsset.folder_name = col.exportFolderName
    MyAsset.StartAssetExport()

    ExportSingleStaticMeshCollection(dirpath, GetCollectionExportFileName(col.name), col.name)

    file = MyAsset.files.add()
    file.name = GetCollectionExportFileName(col.name)
    file.path = dirpath
    file.type = "FBX"

    if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):

        ExportAdditionalParameter(absdirpath, MyAsset)
        file = MyAsset.files.add()
        file.name = GetCollectionExportFileName(col.name, "_AdditionalTrack.json")
        file.path = dirpath
        file.type = "AdditionalTrack"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleStaticMeshCollection(
        dirpath,
        filename,
        collectionName
        ):

    '''
    #####################################################
            #COLLECTION
    #####################################################
    '''
    # Export a single collection

    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()
    collection = bpy.data.collections[collectionName]

    bbpl.utils.safe_mode_set('OBJECT')

    SelectCollectionObjects(collection)
    duplicate_data = DuplicateSelectForExport()
    SetDuplicateNameForExport(duplicate_data)

    MakeSelectVisualReal()

    ApplyNeededModifierToSelect()
    for obj in bpy.context.selected_objects:
        SetVertexColorForUnrealExport(obj)
        ConvertGeometryNodeAttributeToUV(obj)
        CorrectExtremUVAtExport(obj)
        SetSocketsExportTransform(obj)
        SetSocketsExportName(obj)

    bfu_check_potential_error.UpdateNameHierarchy(
        GetAllCollisionAndSocketsObj(bpy.context.selected_objects)
        )

    bpy.ops.export_scene.fbx(
        filepath=GetExportFullpath(dirpath, filename),
        check_existing=False,
        use_selection=True,
        global_scale=1,
        object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
        use_custom_props=addon_prefs.exportWithCustomProps,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        # use_armature_deform_only=active.exportDeformOnly,
        bake_anim=False,
        use_metadata=addon_prefs.exportWithMetaData,
        # primary_bone_axis=active.exportPrimaryBaneAxis,
        # secondary_bone_axis=active.exporSecondaryBoneAxis,
        # axis_forward=active.exportAxisForward,
        # axis_up=active.exportAxisUp,
        bake_space_transform=False
        )
    for obj in bpy.context.selected_objects:
        ClearVertexColorForUnrealExport(obj)
        ResetSocketsExportName(obj)
        ResetSocketsTransform(obj)

    CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        ClearAllBFUTempVars(obj)


def CleanSingleStaticMeshCollection(obj):
    # Remove the created collection
    SelectSpecificObject(obj)
