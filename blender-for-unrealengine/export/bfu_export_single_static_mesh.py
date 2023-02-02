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


def ProcessStaticMeshExport(obj):
    addon_prefs = GetAddonPrefs()
    dirpath = GetObjExportDir(obj)
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.asset_name = obj.name
    MyAsset.folder_name = obj.exportFolderName
    MyAsset.asset_type = bfu_utils.GetAssetType(obj)
    MyAsset.StartAssetExport()

    ExportSingleStaticMesh(dirpath, GetObjExportFileName(obj), obj)
    file = MyAsset.files.add()
    file.name = GetObjExportFileName(obj)
    file.path = dirpath
    file.type = "FBX"

    if not obj.ExportAsLod:
        if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):
            ExportAdditionalParameter(absdirpath, MyAsset)
            file = MyAsset.files.add()
            file.name = GetObjExportFileName(obj, "_AdditionalTrack.json")
            file.path = dirpath
            file.type = "AdditionalTrack"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleStaticMesh(
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
    addon_prefs = GetAddonPrefs()

    bbpl.utils.SafeModeSet('OBJECT')

    SelectParentAndDesiredChilds(obj)
    asset_name = PrepareExportName(obj, False)
    duplicate_data = DuplicateSelectForExport()
    SetDuplicateNameForExport(duplicate_data)

    MakeSelectVisualReal()

    ApplyNeededModifierToSelect()

    active = bpy.context.view_layer.objects.active
    asset_name.target_object = active

    ConvertGeometryNodeAttributeToUV(active)
    CorrectExtremUVAtExport(active)

    ApplyExportTransform(active, "Object")

    meshType = GetAssetType(active)
    SetSocketsExportTransform(active)
    SetSocketsExportName(active)

    bfu_check_potential_error.UpdateNameHierarchy(
        GetAllCollisionAndSocketsObj(bpy.context.selected_objects)
        )

    SetVertexColorForUnrealExport(active)

    asset_name.SetExportName()

    bpy.ops.export_scene.fbx(
        filepath=GetExportFullpath(dirpath, filename),
        check_existing=False,
        use_selection=True,
        global_scale=GetObjExportScale(active),
        object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
        use_custom_props=addon_prefs.exportWithCustomProps,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        use_armature_deform_only=active.exportDeformOnly,
        bake_anim=False,
        use_metadata=addon_prefs.exportWithMetaData,
        primary_bone_axis=active.exportPrimaryBaneAxis,
        secondary_bone_axis=active.exporSecondaryBoneAxis,
        axis_forward=active.exportAxisForward,
        axis_up=active.exportAxisUp,
        bake_space_transform=False
        )

    asset_name.ResetNames()

    ClearVertexColorForUnrealExport(active)
    ResetSocketsExportName(active)
    ResetSocketsTransform(active)
    CleanDeleteObjects(bpy.context.selected_objects)
    for data in duplicate_data.data_to_remove:
        data.RemoveData()

    ResetDuplicateNameAfterExport(duplicate_data)

    for obj in scene.objects:
        ClearAllBFUTempVars(obj)
