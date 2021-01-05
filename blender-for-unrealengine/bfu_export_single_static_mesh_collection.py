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


def ExportSingleStaticMeshCollection(
        originalScene,
        dirpath,
        filename,
        collectionName
        ):

    '''
    #####################################################
            #COLLECTION
    #####################################################
    '''
    # create collection and export it
    obj = bpy.data.objects.new("EmptyCollectionForUnrealExport_Temp", None)
    bpy.context.scene.collection.objects.link(obj)
    obj.instance_type = 'COLLECTION'
    obj.instance_collection = bpy.data.collections[collectionName]
    ExportSingleStaticMesh(originalScene, dirpath, filename, obj)

    # Remove the created collection
    SelectSpecificObject(obj)
    CleanDeleteObjects(bpy.context.selected_objects)
