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
from .. import bfu_naming
from .. import bfu_export_logs
from .. import bfu_assets_manager




def ProcessAlembicAnimationExport(obj):
    scene = bpy.context.scene
    
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
    dirpath = asset_class.get_obj_export_directory_path(obj, True)
    file_name = asset_class.get_obj_file_name(obj, obj.name, "")

    MyAsset: bfu_export_logs.BFU_OT_UnrealExportedAsset = scene.UnrealExportedAssetsList.add()
    MyAsset.object = obj
    MyAsset.asset_name = obj.name
    MyAsset.asset_global_scale = obj.bfu_export_global_scale
    MyAsset.folder_name = obj.bfu_export_folder_name
    MyAsset.asset_type = "Alembic"
    MyAsset.animation_start_frame = scene.frame_start + obj.bfu_anim_action_start_frame_offset
    MyAsset.animation_end_frame = scene.frame_end + obj.bfu_anim_action_end_frame_offset

    file: bfu_export_logs.BFU_OT_FileExport = MyAsset.files.add()
    file.file_name = file_name
    file.file_extension = "abc"
    file.file_path = dirpath
    file.file_type = "ABC"

    MyAsset.StartAssetExport()
    ExportSingleAlembicAnimation(dirpath, file.GetFileWithExtension(), obj)

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

    alembic_animation_export_procedure = obj.bfu_alembic_export_procedure

    # Export
    if (alembic_animation_export_procedure == "blender-standard"):
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
