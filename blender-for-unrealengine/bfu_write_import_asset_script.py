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
from . import languages
from . import bfu_utils

def WriteImportAssetScript():
    # Generate a script for import assets in Ue4
    scene = bpy.context.scene

    data = {}
    data['Coment'] = {
        '1/3': languages.ti('write_text_additional_track_start'),
        '2/3': languages.ti('write_text_additional_track_camera'),
        '3/3': languages.ti('write_text_additional_track_end'),
    }

    data['unreal_import_location'] = '/' + scene.unreal_import_module + '/' + scene.unreal_import_location

    # Import assets
    data['assets'] = []
    for asset in scene.UnrealExportedAssetsList:
        asset_data = {}
        asset_data["scene_unit_scale"] = scene.unit_settings.scale_length

        asset_data["asset_name"] = asset.asset_name
        if bfu_utils.GetIsAnimation(asset.asset_type):
            asset_data["asset_type"] = "Animation"
        elif asset.asset_type == "Collection StaticMesh":
            asset_data["asset_type"] = "StaticMesh"
        else:
            asset_data["asset_type"] = asset.asset_type
        if asset.asset_type == "StaticMesh" or asset.asset_type == "SkeletalMesh":
            if asset.object.ExportAsLod:
                asset_data["lod"] = 1
            else:
                asset_data["lod"] = 0

        if bfu_utils.GetIsAnimation(asset.asset_type):
            relative_import_path = os.path.join(asset.folder_name, scene.anim_subfolder_name)
        else:
            relative_import_path = asset.folder_name

        full_import_path = "/" + scene.unreal_import_module + "/" + os.path.join(scene.unreal_import_location, relative_import_path)
        full_import_path = full_import_path.replace('\\', '/').rstrip('/')
        asset_data["full_import_path"] = full_import_path

        if asset.GetFileByType("FBX"):
            asset_data["fbx_path"] = asset.GetFileByType("FBX").GetAbsolutePath()
        else:
            asset_data["fbx_path"] = None

        if asset.GetFileByType("ABC"):
            asset_data["abc_path"] = asset.GetFileByType("ABC").GetAbsolutePath()
        else:
            asset_data["abc_path"] = None

        if asset.GetFileByType("AdditionalTrack"):
            asset_data["additional_tracks_path"] = asset.GetFileByType("AdditionalTrack").GetAbsolutePath()
        else:
            asset_data["additional_tracks_path"] = None

        if bfu_utils.GetIsAnimation(asset.asset_type) or asset.asset_type == "SkeletalMesh":
            if(asset.object.bfu_skeleton_search_mode) == "auto":
                customName = scene.skeleton_prefix_export_name+bfu_utils.ValidUnrealAssetsName(asset.skeleton_name)+"_Skeleton"
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join(asset.folder_name, SkeletonName)

                animation_skeleton_path = os.path.join("/" + scene.unreal_import_module + "/", scene.unreal_import_location, SkeletonLoc)
                animation_skeleton_path = animation_skeleton_path.replace('\\', '/')
                asset_data["animation_skeleton_path"] = animation_skeleton_path

            elif(asset.object.bfu_skeleton_search_mode) == "custom_name":
                customName = bfu_utils.ValidUnrealAssetsName(asset.object.bfu_target_skeleton_custom_name)
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join(asset.folder_name, SkeletonName)

                animation_skeleton_path = os.path.join("/" + scene.unreal_import_module + "/", scene.unreal_import_location, SkeletonLoc)
                animation_skeleton_path = animation_skeleton_path.replace('\\', '/')
                asset_data["animation_skeleton_path"] = animation_skeleton_path

            elif(asset.object.bfu_skeleton_search_mode) == "custom_path_name":
                customName = bfu_utils.ValidUnrealAssetsName(asset.object.bfu_target_skeleton_custom_name)
                SkeletonName = customName+"."+customName
                SkeletonLoc = os.path.join("/" + scene.unreal_import_module + "/", asset.object.bfu_target_skeleton_custom_path, SkeletonName)
                asset_data["animation_skeleton_path"] = SkeletonLoc.replace('\\', '/')

            elif(asset.object.bfu_skeleton_search_mode) == "custom_reference":
                asset_data["animation_skeleton_path"] = asset.object.bfu_target_skeleton_custom_ref.replace('\\', '/')

        if asset.object:
            asset_data["create_physics_asset"] = asset.object.CreatePhysicsAsset
            asset_data["material_search_location"] = asset.object.MaterialSearchLocation

            asset_data["auto_generate_collision"] = asset.object.AutoGenerateCollision
            if (asset.object.UseStaticMeshLODGroup):
                asset_data["static_mesh_lod_group"] = asset.object.StaticMeshLODGroup
            else:
                asset_data["static_mesh_lod_group"] = None
            asset_data["generate_lightmap_u_vs"] = asset.object.GenerateLightmapUVs

            asset_data["use_custom_light_map_resolution"] = bfu_utils.GetUseCustomLightMapResolution(asset.object)
            asset_data["light_map_resolution"] = bfu_utils.GetCompuntedLightMap(asset.object)
            asset_data["collision_trace_flag"] = asset.object.CollisionTraceFlag

        data['assets'].append(asset_data)

    return data
