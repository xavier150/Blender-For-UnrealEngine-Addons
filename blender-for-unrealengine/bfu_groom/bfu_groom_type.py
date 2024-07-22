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

import os
import bpy
import fnmatch
from . import bfu_groom_config
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_assets_manager


class BFU_Groom(bfu_assets_manager.bfu_asset_manager_type.BFU_BaseAssetClass):
    def __init__(self):
        super().__init__()
        pass

    def support_asset_type(self, obj):
        if obj.bfu_export_as_groom_simulation:
            return True
        return False

    def get_asset_type_name(self, obj):
        return bfu_groom_config.asset_type_name
    
    def get_obj_file_name(self, obj, desired_name="", fileType=".fbx"):
        # Generate assset file name for skeletal mesh
        scene = bpy.context.scene
        if obj.bfu_use_custom_export_name:
            if obj.bfu_custom_export_name:
                return obj.bfu_custom_export_name
        if desired_name:
            return bfu_basics.ValidFilename(scene.bfu_groom_simulation_prefix_export_name+desired_name+fileType)
        return bfu_basics.ValidFilename(scene.bfu_groom_simulation_prefix_export_name+obj.name+fileType)
    
    def get_obj_export_directory_path(self, obj):
        folder_name = bfu_utils.get_export_folder_name(obj)
        scene = bpy.context.scene
        dirpath = os.path.join(scene.bfu_export_groom_file_path, folder_name)
        return dirpath
    
    def can_export_asset(self):
        scene = bpy.context.scene
        return scene.groom_simulation_export

    def can_export_obj_asset(self, obj):
        return self.can_export_asset()
    
def register():
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(BFU_Groom())

def unregister():
    pass

