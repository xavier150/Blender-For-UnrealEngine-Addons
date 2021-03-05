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
    if "bfu_export_utils" in locals():
        importlib.reload(bfu_export_utils)
    if "bfu_export_single_static_mesh" in locals():
        importlib.reload(bfu_export_single_static_mesh)
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)

from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_export_utils
from .bfu_export_utils import *
from . import bfu_export_single_static_mesh
from .bfu_export_single_static_mesh import *
from . import bfu_check_potential_error


def ProcessCollectionExport(col):

    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    dirpath = GetCollectionExportDir(bpy.data.collections[col])
    absdirpath = bpy.path.abspath(dirpath)
    scene = bpy.context.scene

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.StartAssetExport(collection=col)

    obj = ExportSingleStaticMeshCollection(dirpath, GetCollectionExportFileName(col), col)

    MyAsset.SetObjData(obj)

    file = MyAsset.files.add()
    file.name = GetCollectionExportFileName(col)
    file.path = dirpath
    file.type = "FBX"

    if (scene.text_AdditionalData and addon_prefs.useGeneratedScripts):

        ExportSingleAdditionalParameterMesh(absdirpath, GetCollectionExportFileName(col, "_AdditionalTrack.json"), obj)
        file = MyAsset.files.add()
        file.name = GetCollectionExportFileName(col, "_AdditionalTrack.json")
        file.path = dirpath
        file.type = "AdditionalTrack"

    CleanSingleStaticMeshCollection(obj)
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
    collection = bpy.data.collections[collectionName]

    # create collection and export it
    obj = bpy.data.objects.new("EmptyCollectionForUnrealExport_Temp", None)
    bpy.context.scene.collection.objects.link(obj)
    obj.instance_type = 'COLLECTION'
    obj.instance_collection = collection
    ExportSingleStaticMesh(dirpath, filename, obj)
    obj.exportFolderName = collection.exportFolderName
    return obj


def CleanSingleStaticMeshCollection(obj):
    # Remove the created collection
    SelectSpecificObject(obj)
    CleanDeleteObjects(bpy.context.selected_objects)
