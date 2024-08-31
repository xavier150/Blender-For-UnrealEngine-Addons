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
from .. import bfu_utils
from .. import bfu_basics

class BFU_BaseAssetClass:
    def __init__(self):
        self.use_lods = False
        self.use_materials = False
        self.use_sockets = False

    def support_asset_type(self, obj, details = None):
        return False

    def get_asset_type_name(self, obj):
        return None

    def get_obj_export_name(self, obj):
        return bfu_basics.ValidFilename(obj.name)
    
    def get_obj_file_name(self, obj, desired_name="", fileType=".fbx"):
        return ""
    
    def get_obj_export_directory_path(self, obj, absolute = True):
        return ""

    def can_export_asset(self):
        return False

    def can_export_obj_asset(self, obj):
        return False
    