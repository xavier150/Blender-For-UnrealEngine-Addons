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
from . import bfu_skeletal_mesh_config
from .. import bfu_assets_manager
from .. import bfu_utils
from .. import bfu_basics


class BFU_SkeletalMesh(bfu_assets_manager.bfu_asset_manager_type.BFU_BaseAssetClass):
    def __init__(self):
        super().__init__()
        self.use_materials = True

    def support_asset_type(self, obj):
        if obj.type == "ARMATURE" and not obj.bfu_export_skeletal_mesh_as_static_mesh:
            return True
        return False

    def get_asset_type_name(self, obj):
        return bfu_skeletal_mesh_config.asset_type_name

    def get_obj_export_name(self, obj):
        if bfu_utils.GetExportAsProxy(obj):
            proxy_child = bfu_utils.GetExportProxyChild(obj)
            if proxy_child is not None:
                return bfu_basics.ValidFilename(proxy_child.name)
        return super().get_obj_export_name(obj)
            
    def get_obj_file_name(self, obj, desired_name="", fileType=".fbx"):
        # Generate assset file name for skeletal mesh
        scene = bpy.context.scene
        if obj.bfu_use_custom_export_name:
            if obj.bfu_custom_export_name:
                return obj.bfu_custom_export_name
        if desired_name:
            return bfu_basics.ValidFilename(scene.bfu_skeletal_mesh_prefix_export_name+desired_name+fileType)
        return bfu_basics.ValidFilename(scene.bfu_skeletal_mesh_prefix_export_name+obj.name+fileType)
            
    def get_obj_export_directory_path(self, obj, absolute = True):
        folder_name = bfu_utils.get_export_folder_name(obj)
        scene = bpy.context.scene
        if(absolute):
            root_path = bpy.path.abspath(scene.bfu_export_skeletal_file_path)
        else:
            root_path = scene.bfu_export_skeletal_file_path
    
        if obj.bfu_create_sub_folder_with_skeletal_mesh_name:
            dirpath = os.path.join(root_path, folder_name, self.get_obj_export_name(obj))
        else:
            dirpath = os.path.join(root_path, folder_name)
        return dirpath
    
    def get_meshs_object_for_skeletal_mesh(self, obj):
        meshs = []
        if self.support_asset_type(obj):  # Skeleton /  Armature
            childs = bfu_utils.GetExportDesiredChilds(obj)
            for child in childs:
                if child.type == "MESH":
                    meshs.append(child)
        return meshs

    def can_export_asset(self):
        scene = bpy.context.scene
        return scene.skeletal_export

    def can_export_obj_asset(self, obj):
        if self.can_export_asset():
            if obj.bfu_skeleton_export_procedure == 'auto-rig-pro':
                if bfu_basics.CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            False

def register():
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(BFU_SkeletalMesh())

def unregister():
    pass