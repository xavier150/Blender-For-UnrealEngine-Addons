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

def ExportSingleAlembicAnimation(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#ALEMBIC ANIMATION
	#####################################################
	'''
	#Export a single alembic animation

	scene = bpy.context.scene
	filename = ValidFilenameForUnreal(filename)
	s = CounterStart()
	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')

	SelectParentAndDesiredChilds(obj)

	scene.frame_start += obj.StartFramesOffset
	scene.frame_end += obj.EndFramesOffset
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	##Export
	bpy.ops.wm.alembic_export(
		filepath=fullpath,
		check_existing=False,
		selected=True,
		triangulate=False,
		)

	scene.frame_start -= obj.StartFramesOffset
	scene.frame_end -= obj.EndFramesOffset
	exportTime = CounterEnd(s)

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "Alembic"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset
