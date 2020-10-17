#====================== BEGIN GPL LICENSE BLOCK ============================
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
#======================= END GPL LICENSE BLOCK =============================


import bpy
import time
import math

import importlib
from . import bfu_WriteText
importlib.reload(bfu_WriteText)

from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *

from . import bfu_Utils
importlib.reload(bfu_Utils)
from .bfu_Utils import *

from . import bfu_ExportUtils
importlib.reload(bfu_ExportUtils)
from .bfu_ExportUtils import *

from . import bfu_ExportSingleStaticMesh
importlib.reload(bfu_ExportSingleStaticMesh)
from .bfu_ExportSingleStaticMesh import *

def ExportSingleStaticMeshCollection(originalScene, dirpath, filename, collectionName):
	'''
	#####################################################
			#COLLECTION
	#####################################################
	'''
	#create collection and export it
	obj = bpy.data.objects.new( "EmptyCollectionForUnrealExport_Temp", None )
	bpy.context.scene.collection.objects.link( obj )
	obj.instance_type = 'COLLECTION'
	obj.instance_collection = bpy.data.collections[collectionName]
	ExportSingleStaticMesh(originalScene, dirpath, filename, obj)
	
	#Remove the created collection
	SelectSpecificObject(obj)
	CleanDeleteObjects(bpy.context.selected_objects)
