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
import configparser
from math import degrees
from . import languages
from .languages import *

if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_write_utils" in locals():
        importlib.reload(bfu_write_utils)
    if "languages" in locals():
        importlib.reload(languages)

from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_write_utils
from .bfu_write_utils import *


def WriteImportAssetScript():
    # Generate a script for import assets in Ue4
    scene = bpy.context.scene

    data = {}
    data['Coment'] = {
        '1/3': ti('write_text_additional_track_start'),
        '2/3': ti('write_text_additional_track_camera'),
        '3/3': ti('write_text_additional_track_end'),
    }

    data['unreal_import_location'] = '/Game/' + scene.unreal_import_location

    # Import assets
    data['assets'] = []
    for asset in scene.UnrealExportedAssetsList:
        asset_data = {}
        asset_data["name"] = asset.object.name
        if GetIsAnimation(asset.asset_type):
            asset_data["type"] = "Animation"
        else:
            asset_data["type"] = asset.asset_type
        if asset.asset_type == "StaticMesh" or asset.asset_type == "SkeletalMesh":
            if asset.object.ExportAsLod:
                asset_data["lod"] = 1
            else:
                asset_data["lod"] = 0

        if GetIsAnimation(asset.asset_type):
            relative_import_path = os.path.join(asset.object.exportFolderName, scene.anim_subfolder_name)
        else:
            relative_import_path = asset.object.exportFolderName

        asset_data["full_import_path"] = "/Game/" + os.path.join(scene.unreal_import_location, relative_import_path).replace('\\','/').rstrip('/')

        if asset.GetFileByType("FBX"):
            asset_data["fbx_path"] = asset.GetFileByType("FBX").GetFullPath()
        else:
            asset_data["fbx_path"] = None

        if asset.GetFileByType("ABC"):
            asset_data["abc_path"] = asset.GetFileByType("ABC").GetFullPath()
        else:
            asset_data["abc_path"] = None

        if asset.GetFileByType("AdditionalTrack"):
            asset_data["additional_tracks_path"] = asset.GetFileByType("AdditionalTrack").GetFullPath()
        else:
            asset_data["additional_tracks_path"] = None

        if GetIsAnimation(asset.asset_type):
            if(asset.object.bfu_skeleton_search_mode) == "auto":
                customName = scene.skeletal_prefix_export_name+ValidUnrealAssetename(asset.object.name)+"_Skeleton"
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join(asset.object.exportFolderName, SkeletonName)
                asset_data["animation_skeleton_path"] = os.path.join(scene.unreal_import_location, SkeletonLoc).replace('\\','/')

            elif(asset.object.bfu_skeleton_search_mode) == "custom_name":
                customName = ValidUnrealAssetename(asset.object.bfu_target_skeleton_custom_name)
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join(asset.object.exportFolderName, SkeletonName)
                asset_data["animation_skeleton_path"] = os.path.join(scene.unreal_import_location, SkeletonLoc).replace('\\','/')

            elif(asset.object.bfu_skeleton_search_mode) == "custom_path_name":
                customName = ValidUnrealAssetename(asset.object.bfu_target_skeleton_custom_name)
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join(asset.object.bfu_target_skeleton_custom_path, SkeletonName)
                asset_data["animation_skeleton_path"] = SkeletonLoc.replace('\\','/')

            elif(asset.object.bfu_skeleton_search_mode) == "custom_reference":
                asset_data["animation_skeleton_path"] = asset.object.bfu_target_skeleton_custom_ref.replace('\\','/')

        asset_data["create_physics_asset"] = asset.object.CreatePhysicsAsset
        asset_data["material_search_location"] = asset.object.MaterialSearchLocation

        asset_data["auto_generate_collision"] = asset.object.AutoGenerateCollision
        if (asset.object.UseStaticMeshLODGroup):
            asset_data["static_mesh_lod_group"] = asset.object.StaticMeshLODGroup
        else:
            asset_data["static_mesh_lod_group"] = None
        asset_data["generate_lightmap_u_vs"] = asset.object.GenerateLightmapUVs

        asset_data["custom_light_map_resolution"] = ExportCompuntedLightMapValue(asset.object)
        asset_data["light_map_resolution"] = GetCompuntedLightMap(asset.object)
        asset_data["collision_trace_flag"] = asset.object.CollisionTraceFlag
        asset_data["vertex_color_import_option"] = asset.object.VertexColorImportOption
        data['assets'].append(asset_data)

    return data
