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
from . import bfu_export_utils
from .. import bbpl
from .. import bfu_utils




def ProcessAlembicExport(obj):
    scene = bpy.context.scene
    dirpath = bfu_utils.GetObjExportDir(obj)

    MyAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.asset_name = obj.name
    MyAsset.asset_global_scale = obj.bfu_export_global_scale
    MyAsset.folder_name = obj.bfu_export_folder_name
    MyAsset.asset_type = "Alembic"
    MyAsset.StartAssetExport()

    ExportSingleAlembicAnimation(dirpath, bfu_utils.GetObjExportFileName(obj, ".abc"), obj)
    file = MyAsset.files.add()
    file.name = bfu_utils.GetObjExportFileName(obj, ".abc")
    file.path = dirpath
    file.type = "ABC"

    MyAsset.EndAssetExport(True)
    return MyAsset


def ExportSingleAlembicAnimation(
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
    bbpl.utils.safe_mode_set('OBJECT')

    bfu_utils.SelectParentAndDesiredChilds(obj)

    scene.frame_start += obj.bfu_anim_action_start_frame_offset
    scene.frame_end += obj.bfu_anim_action_end_frame_offset

    # Export
    bpy.ops.wm.alembic_export(
        filepath=bfu_export_utils.GetExportFullpath(dirpath, filename),
        check_existing=False,
        selected=True,
        triangulate=True,
        global_scale=1,
        )

    scene.frame_start -= obj.bfu_anim_action_start_frame_offset
    scene.frame_end -= obj.bfu_anim_action_end_frame_offset

    for obj in scene.objects:
        bfu_utils.ClearAllBFUTempVars(obj)
