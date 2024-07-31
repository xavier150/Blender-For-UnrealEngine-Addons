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
import json
from shutil import copyfile
import bpy
import math

from . import bps
from . import bbpl
from . import languages
from . import bfu_basics
from . import bfu_utils
from . import bfu_naming
from . import bfu_export_logs
from . import bfu_write_import_asset_script
from . import bfu_write_import_sequencer_script
from . import bfu_vertex_color
from . import bfu_collision
from . import bfu_socket
from . import bfu_assets_manager
from . import bfu_static_mesh
from . import bfu_skeletal_mesh


def ExportSingleText(text, dirpath, filename):
    # Export single text

    counter = bps.utils.CounterTimer()

    absdirpath = bpy.path.abspath(dirpath)
    bfu_basics.VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, "w") as file:
        file.write(text)

    exportTime = counter.get_time()
    # This return [AssetName , AssetType , ExportPath, ExportTime]
    return([filename, "TextFile", absdirpath, exportTime])


def ExportSingleJson(json_data, dirpath, filename):
    # Export single Json

    counter = bps.utils.CounterTimer()

    absdirpath = bpy.path.abspath(dirpath)
    bfu_basics.VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, 'w') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, sort_keys=False, indent=4)

    exportTime = counter.get_time()
    # This return [AssetName , AssetType , ExportPath, ExportTime]
    return([filename, "TextFile", absdirpath, exportTime])


def WriteExportLog():
    # Write Export log with exported assets in scene.UnrealExportedAssetsList

    scene = bpy.context.scene
    StaticNum = 0
    SkeletalNum = 0
    AlembicNum = 0
    AnimNum = 0
    CameraNum = 0
    SplineNum = 0

    # Get number per asset type
    for assets in scene.UnrealExportedAssetsList:
        if assets.asset_type == "StaticMesh":
            StaticNum += 1
        if assets.asset_type == "SkeletalMesh":
            SkeletalNum += 1
        if assets.asset_type == "Alembic":
            AlembicNum += 1
        if bfu_utils.GetIsAnimation(assets.asset_type):
            AnimNum += 1
        if assets.asset_type == "Camera":
            CameraNum += 1
        if assets.asset_type == "Spline":
            SplineNum += 1

    asset_number = len(scene.UnrealExportedAssetsList)
    exported_assets = StaticNum+SkeletalNum+AlembicNum+AnimNum+CameraNum+SplineNum

    OtherNum = asset_number - exported_assets

    # Asset number string
    AssetNumberByType = str(StaticNum)+" StaticMesh(s) | "
    AssetNumberByType += str(SkeletalNum)+" SkeletalMesh(s) | "
    AssetNumberByType += str(AlembicNum)+" Alembic(s) | "
    AssetNumberByType += str(AnimNum)+" Animation(s) | "
    AssetNumberByType += str(CameraNum)+" Camera(s) | "
    AssetNumberByType += str(CameraNum)+" Spline(s) | "
    AssetNumberByType += str(OtherNum)+" Other(s)" + "\n"

    ExportLog = ""
    ExportLog += AssetNumberByType
    ExportLog += "\n"
    for asset in scene.UnrealExportedAssetsList:
        file: bfu_export_logs.BFU_OT_UnrealExportedAsset

        if (asset.asset_type == "NlAnim"):
            primaryInfo = "Animation (NLA)"
        elif (asset.asset_type == "Action"):
            primaryInfo = "Animation (Action)"
        elif (asset.asset_type == "Pose"):
            primaryInfo = "Animation (Pose)"
        else:
            if asset.object:
                if asset.object.bfu_export_as_lod_mesh:
                    primaryInfo = asset.asset_type+" (LOD)"
                else:
                    primaryInfo = asset.asset_type
            else:
                primaryInfo = asset.asset_type

        ExportLog += (
            asset.asset_name+" ["+primaryInfo+"] EXPORTED IN " + str(round(asset.GetExportTime(), 2))+"s\r\n")
        for file in asset.files:
            file: bfu_export_logs.BFU_OT_FileExport
            ExportLog += (file.file_path + "\\" + file.file_name + "\n")
        ExportLog += "\n"

    return ExportLog




def WriteSingleMeshAdditionalParameter(unreal_exported_asset):

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    obj = unreal_exported_asset.object

    data = {}

    # Comment
    data['Coment'] = {
        '1/3': languages.ti('write_text_additional_track_start'),
        '2/3': languages.ti('write_text_additional_track_all'),
        '3/3': languages.ti('write_text_additional_track_end'),
    }

    # Defaultsettings
    data['DefaultSettings'] = {}
    # config.set('Defaultsettings', 'SocketNumber', str(len(sockets)))

    # Level of detail
    if obj:
        data['LevelOfDetail'] = {}

        def GetLodPath(lod_obj):
            asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(lod_obj)
            if asset_class:
                directory_path = asset_class.get_obj_export_directory_path(lod_obj, True)
                file_name = asset_class.get_obj_file_name(lod_obj)
            return os.path.join(directory_path, file_name)

        if obj.bfu_lod_target1 is not None:
            data['LevelOfDetail']['lod_1'] = GetLodPath(obj.bfu_lod_target1)
        if obj.bfu_lod_target2 is not None:
            data['LevelOfDetail']['lod_2'] = GetLodPath(obj.bfu_lod_target2)
        if obj.bfu_lod_target3 is not None:
            data['LevelOfDetail']['lod_3'] = GetLodPath(obj.bfu_lod_target3)
        if obj.bfu_lod_target4 is not None:
            data['LevelOfDetail']['lod_4'] = GetLodPath(obj.bfu_lod_target4)
        if obj.bfu_lod_target5 is not None:
            data['LevelOfDetail']['lod_5'] = GetLodPath(obj.bfu_lod_target5)

    # Sockets
    if obj:
        data['Sockets'] = bfu_socket.bfu_socket_utils.get_skeletal_mesh_sockets(obj)

    # Vertex Color
    if obj:
        if bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj) or bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
            vced = bfu_vertex_color.bfu_vertex_color_utils.VertexColorExportData(obj)
            data["vertex_color_import_option"] = vced.export_type
            vertex_override_color = (
                vced.color[0],  # R
                vced.color[1],  # G
                vced.color[2]  # B
            )  # Color to Json
            data["vertex_override_color"] = vertex_override_color

    data["preview_import_path"] = unreal_exported_asset.GetFilenameWithExtension()
    return data


def WriteAllTextFiles():

    scene = bpy.context.scene
    addon_prefs = bfu_basics.GetAddonPrefs()
    
    root_dirpath = bpy.path.abspath(scene.bfu_export_other_file_path)
    if scene.text_ExportLog:
        Text = languages.ti("write_text_additional_track_start") + "\n"
        Text += "" + "\n"
        Text += WriteExportLog()
        if Text is not None:
            Filename = bfu_basics.ValidFilename(scene.bfu_file_export_log_name)
            ExportSingleText(Text, root_dirpath, Filename)

    # Import script
    if bpy.app.version >= (4, 2, 0):
        bfu_path = os.path.join(bbpl.blender_extension.extension_utils.get_package_path(), "bfu_import_module")
    else:
        bfu_path = os.path.join(bbpl.blender_addon.addon_utils.get_addon_path("Unreal Engine Assets Exporter"), "bfu_import_module")

    if scene.text_ImportAssetScript:
        json_data = bfu_write_import_asset_script.WriteImportAssetScript()
        ExportSingleJson(json_data, root_dirpath, "ImportAssetData.json")
        source = os.path.join(bfu_path, "asset_import_script.py")
        filename = bfu_basics.ValidFilename(scene.bfu_file_import_asset_script_name)
        destination = os.path.join(root_dirpath, filename)
        copyfile(source, destination)

    if scene.text_ImportSequenceScript:
        json_data = bfu_write_import_sequencer_script.WriteImportSequencerTracks()
        ExportSingleJson(json_data, root_dirpath, "ImportSequencerData.json")
        source = os.path.join(bfu_path, "sequencer_import_script.py")
        filename = bfu_basics.ValidFilename(scene.bfu_file_import_sequencer_script_name)
        destination = os.path.join(root_dirpath, filename)
        copyfile(source, destination)
