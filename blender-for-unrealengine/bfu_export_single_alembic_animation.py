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
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)

from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_export_utils
from .bfu_export_utils import *
from . import bfu_check_potential_error


def ExportSingleAlembicAnimation(
        originalScene,
        dirpath,
        filename,
        obj
        ):

    '''
    #####################################################
            #ALEMBIC ANIMATION
    #####################################################
    '''
    # Export a single alembic animation

    scene = bpy.context.scene
    counter = CounterTimer()
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    SelectParentAndDesiredChilds(obj)

    scene.frame_start += obj.StartFramesOffset
    scene.frame_end += obj.EndFramesOffset
    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    # Export
    bpy.ops.wm.alembic_export(
        filepath=fullpath,
        check_existing=False,
        selected=True,
        triangulate=False,
        )

    scene.frame_start -= obj.StartFramesOffset
    scene.frame_end -= obj.EndFramesOffset
    exportTime = counter.GetTime()

    MyAsset = originalScene.UnrealExportedAssetsList.add()
    MyAsset.asset_type = "Alembic"
    MyAsset.object = obj
    file = MyAsset.files.add()
    file.name = filename
    file.path = absdirpath
    file.type = "FBX"
    return MyAsset
