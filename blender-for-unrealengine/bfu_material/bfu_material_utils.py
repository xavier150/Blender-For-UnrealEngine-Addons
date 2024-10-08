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
import fnmatch
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_unreal_utils
from .. import bfu_export_logs

def get_material_asset_data(asset: bfu_export_logs.BFU_OT_UnrealExportedAsset):
    asset_data = {}
    if asset.object:
        if asset.asset_type in ["StaticMesh", "SkeletalMesh"]:
            asset_data["import_materials"] = asset.object.bfu_import_materials
            asset_data["import_textures"] = asset.object.bfu_import_textures
            asset_data["flip_normal_map_green_channel"] = asset.object.bfu_flip_normal_map_green_channel
            asset_data["reorder_material_to_fbx_order"] = asset.object.bfu_reorder_material_to_fbx_order
            asset_data["material_search_location"] = asset.object.bfu_material_search_location
    return asset_data