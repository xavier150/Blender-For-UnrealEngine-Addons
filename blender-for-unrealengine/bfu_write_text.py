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
from math import degrees, radians, tan
from mathutils import Matrix
import json
from . import languages
from .languages import *


if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_write_import_asset_script" in locals():
        importlib.reload(bfu_write_import_asset_script)
    if "bfu_write_import_sequencer_script" in locals():
        importlib.reload(bfu_write_import_sequencer_script)
    if "languages" in locals():
        importlib.reload(languages)

from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_write_import_asset_script
from . import bfu_write_import_sequencer_script


def ExportSingleText(text, dirpath, filename):
    # Export single text

    s = CounterStart()

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, "w") as file:
        file.write(text)

    exportTime = CounterEnd(s)
    # This return [AssetName , AssetType , ExportPath, ExportTime]
    return([filename, "TextFile", absdirpath, exportTime])


def ExportSingleConfigParser(config_data, dirpath, filename):
    # Export single ConfigParser

    s = CounterStart()

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, "w") as config_file:
        config_data.write(config_file)

    exportTime = CounterEnd(s)
    # This return [AssetName , AssetType , ExportPath, ExportTime]
    return([filename, "TextFile", absdirpath, exportTime])


def ExportSingleJson(json_data, dirpath, filename):
    # Export single ConfigParser

    s = CounterStart()

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, 'w') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, sort_keys=False, indent=4)

    exportTime = CounterEnd(s)
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

    # Get number per asset type
    for assets in scene.UnrealExportedAssetsList:
        if assets.asset_type == "StaticMesh":
            StaticNum += 1
        if assets.asset_type == "SkeletalMesh":
            SkeletalNum += 1
        if assets.asset_type == "Alembic":
            AlembicNum += 1
        if GetIsAnimation(assets.asset_type):
            AnimNum += 1
        if assets.asset_type == "Camera":
            CameraNum += 1

    asset_number = len(scene.UnrealExportedAssetsList)
    exported_assets = StaticNum+SkeletalNum+AlembicNum+AnimNum+CameraNum

    OtherNum = asset_number - exported_assets

    # Asset number string
    AssetNumberByType = str(StaticNum)+" StaticMesh(s) | "
    AssetNumberByType += str(SkeletalNum)+" SkeletalMesh(s) | "
    AssetNumberByType += str(AlembicNum)+" Alembic(s) | "
    AssetNumberByType += str(AnimNum)+" Animation(s) | "
    AssetNumberByType += str(CameraNum)+" Camera(s) | "
    AssetNumberByType += str(OtherNum)+" Other(s)" + "\n"

    ExportLog = ""
    ExportLog += AssetNumberByType
    ExportLog += "\n"
    for asset in scene.UnrealExportedAssetsList:

        if (asset.asset_type == "NlAnim"):
            primaryInfo = "Animation (NLA)"
        elif (asset.asset_type == "Action"):
            primaryInfo = "Animation (Action)"
        elif (asset.asset_type == "Pose"):
            primaryInfo = "Animation (Pose)"
        else:
            if asset.object.ExportAsLod:
                primaryInfo = asset.asset_type+" (LOD)"
            else:
                primaryInfo = asset.asset_type

        ExportLog += (
            asset.asset_name+" ["+primaryInfo+"] EXPORTED IN " + str(round(asset.export_time, 2))+"s\r\n")
        for file in asset.files:
            ExportLog += (file.path + "\\" + file.name + "\n")
        ExportLog += "\n"

    return ExportLog


def WriteExportedAssetsDetail():
    # Generate a config file for import assets in Ue4
    scene = bpy.context.scene
    config = configparser.ConfigParser(allow_no_value=True)

    def getSectionNameByAsset(asset):
        # GetObjExportFileName(asset.object, "")
        return "ASSET_" + GetObjExportFileName(asset.object, "")

    def completeAssetSection(config, asset):
        # Complete the section of an asset

        obj = asset.object
        AssetSectionName = getSectionNameByAsset(asset)
        if (not config.has_section(AssetSectionName)):
            config.add_section(AssetSectionName)

        config.set(
            AssetSectionName,
            'name',
            GetObjExportFileName(asset.object, "")
            )
        config.set(
            AssetSectionName,
            'mesh_import_path',
            os.path.join(obj.exportFolderName)
            )

        # Mesh only
        if (asset.asset_type == "StaticMesh" or asset.asset_type == "SkeletalMesh"):
            fbx_path = (os.path.join(asset.export_path, asset.file_name))
            config.set(AssetSectionName, 'lod0_fbx_path', fbx_path)
            config.set(AssetSectionName, 'asset_type', asset.asset_type)
            config.set(AssetSectionName, 'material_search_location', obj.MaterialSearchLocation)
            config.set(AssetSectionName, 'generate_lightmap_uvs', str(obj.GenerateLightmapUVs))
            config.set(AssetSectionName, 'create_physics_asset', str(obj.CreatePhysicsAsset))
            if (obj.UseStaticMeshLODGroup):
                config.set(AssetSectionName, 'static_mesh_lod_group', obj.StaticMeshLODGroup)
            if (ExportCompuntedLightMapValue(obj)):
                config.set(AssetSectionName, 'light_map_resolution', str(GetCompuntedLightMap(obj)))

        # Anim only
        if GetIsAnimation(asset.asset_type):
            actionIndex = 0
            animOption = "anim"+str(actionIndex)
            while config.has_option(AssetSectionName, animOption+'_fbx_path'):
                actionIndex += 1
                animOption = "anim"+str(actionIndex)

            fbx_path = (os.path.join(asset.export_path, asset.file_name))
            config.set(AssetSectionName, animOption+'_fbx_path', fbx_path)
            config.set(AssetSectionName, animOption+'_import_path', os.path.join(obj.exportFolderName, scene.anim_subfolder_name))

    AssetForImport = []
    for asset in scene.UnrealExportedAssetsList:
        if (asset.asset_type == "StaticMesh" or asset.asset_type == "SkeletalMesh" or GetIsAnimation(asset.asset_type)):
            AssetForImport.append(asset)

    # Comment
    config.add_section('Comment')
    config.set('Comment', '; '+ti(write_text_additional_track_start))

    config.add_section('Defaultsettings')
    config.set('Defaultsettings', 'unreal_import_location', r'/Game/'+scene.unreal_import_location)

    for asset in AssetForImport:
        completeAssetSection(config, asset)

    # Import asset
    return config


def WriteCameraAnimationTracks(obj):
    # Write as json file

    def getCameraFocusDistance(Camera, Target):
        transA = Camera.matrix_world.copy()
        transB = Target.matrix_world.copy()
        transA.invert()
        distance = (transA @ transB).translation.z  # Z is the Fosrward
        if distance < 0:
            distance *= -1
        return distance

    def getAllCamDistKeys(Camera, Target):
        scene = bpy.context.scene
        saveFrame = scene.frame_current  # Save current frame
        keys = []
        for frame in range(scene.frame_start, scene.frame_end+1):
            scene.frame_set(frame)
            v = getCameraFocusDistance(Camera, Target)
            keys.append((frame, v))
        scene.frame_set(saveFrame)  # Resets previous start frame
        return keys

    def getAllKeysByMatrix(obj):
        scene = bpy.context.scene
        saveFrame = scene.frame_current  # Save current frame
        keys = []
        for frame in range(scene.frame_start, scene.frame_end+1):
            scene.frame_set(frame)
            v = obj.matrix_world*1
            keys.append((frame, v))
        scene.frame_set(saveFrame)  # Resets previous start frame
        return keys

    def getOneKeysByFcurves(obj, DataPath, DataValue, Frame, IsData=True):
        scene = bpy.context.scene
        if IsData:
            if obj.data.animation_data is not None:
                if obj.data.animation_data.action is not None:
                    f = obj.data.animation_data.action.fcurves.find(DataPath)
                    if f is not None:
                        return f.evaluate(Frame)
        else:
            if obj.animation_data is not None:
                if obj.animation_data.action is not None:
                    f = obj.animation_data.action.fcurves.find(DataPath)
                    if f is not None:
                        return f.evaluate(Frame)
        return DataValue

    def getAllKeysByFcurves(obj, DataPath, DataValue, IsData=True):
        scene = bpy.context.scene
        keys = []
        f = None
        if IsData:
            if obj.data.animation_data is not None:
                if obj.data.animation_data.action is not None:
                    f = obj.data.animation_data.action.fcurves.find(DataPath)
        else:
            if obj.animation_data is not None:
                if obj.animation_data.action is not None:
                    f = obj.animation_data.action.fcurves.find(DataPath)

        if f is not None:
            for frame in range(scene.frame_start, scene.frame_end+1):
                v = f.evaluate(frame)
                keys.append((frame, v))
            return keys
        return[(scene.frame_start, DataValue)]

    class CameraDataAtFrame():

        def __init__(self):
            scene = bpy.context.scene
            self.transform_track = {}
            self.lens = {}
            self.sensor_width = {}
            self.sensor_height = {}
            self.focus_distance = {}
            self.aperture_fstop = {}
            self.hide_viewport = {}

        def EvaluateTracks(self, camera, frame_start, frame_end):

            saveFrame = scene.frame_current
            for frame in range(frame_start, frame_end+1):
                scene.frame_set(frame)

                # Get Transfrom
                matrix = camera.matrix_world @ Matrix.Rotation(radians(90.0), 4, 'Y') @ Matrix.Rotation(radians(-90.0), 4, 'X')
                loc, rot, scale = obj.matrix_world.decompose()
                loc = loc * 100 * bpy.context.scene.unit_settings.scale_length

                array_location = [loc[0], loc[1]*-1, loc[2]]
                array_rotation = [degrees(rot[0]), degrees(rot[1])*-1, degrees(rot[2])*-1]
                array_scale = [scale[0], scale[1], scale[2]]

                transform = {}
                transform["location_x"] = array_location[0]
                transform["location_y"] = array_location[1]
                transform["location_z"] = array_location[2]
                transform["rotation_x"] = array_rotation[0]
                transform["rotation_y"] = array_rotation[1]
                transform["rotation_z"] = array_rotation[2]
                transform["scale_x"] = array_scale[0]
                transform["scale_y"] = array_scale[1]
                transform["scale_z"] = array_scale[2]
                self.transform_track[frame] = transform

                # Get FocalLength SensorWidth SensorHeight
                self.lens[frame] = getOneKeysByFcurves(camera, "lens", camera.data.lens, frame)
                self.sensor_width[frame] = getOneKeysByFcurves(camera, "sensor_width", camera.data.sensor_width, frame)
                self.sensor_height[frame] = getOneKeysByFcurves(camera, "sensor_height", camera.data.sensor_height, frame)

                # Get FocusDistance
                if camera.data.dof.focus_object is not None:
                    key = getCameraFocusDistance(camera, camera.data.dof.focus_object) * 100

                else:
                    key = getOneKeysByFcurves(camera, "dof.focus_distance", camera.data.dof.focus_distance, frame) * 100

                if key > 0:
                    self.focus_distance[frame] = key
                else:
                    self.focus_distance[frame] = 100000  # 100000 is default value in ue4

                # Write Aperture (Depth of Field) keys
                if scene.render.engine == "BLENDER_EEVEE" or scene.render.engine == "CYCLES" or scene.render.engine == "BLENDER_WORKBENCH":
                    self.aperture_fstop[frame] = getOneKeysByFcurves(camera, "dof.aperture_fstop", camera.data.dof.aperture_fstop, frame)
                else:
                    self.aperture_fstop[frame] = 21  # 21 is default value in ue4

                boolKey = getOneKeysByFcurves(camera, "hide_viewport", camera.hide_viewport, frame, False)
                self.hide_viewport = (boolKey < 1)  # Inversed for convert hide to spawn
            scene.frame_set(saveFrame)

        pass

    scene = bpy.context.scene
    data = {}
    data['Info'] = []
    data['Info'].append({
        'Info 1': ti('write_text_additional_track_start'),
        'Info 2': ti('write_text_additional_track_camera'),
        'Info 3': ti('write_text_additional_track_end'),
    })

    data['Frames'] = []
    data['Frames'].append({
        'frame_start': scene.frame_start,
        'frame_end': scene.frame_end,
    })

    camera_tracks = CameraDataAtFrame()
    camera_tracks.EvaluateTracks(obj, scene.frame_start, scene.frame_end)

    data['Camera transform'] = []
    data['Camera transform'].append(camera_tracks.transform_track)

    data['Camera FocalLength'] = []
    data['Camera FocalLength'].append(camera_tracks.lens)

    data['Camera SensorWidth'] = []
    data['Camera SensorWidth'].append(camera_tracks.sensor_width)

    data['Camera SensorHeight'] = []
    data['Camera SensorHeight'].append(camera_tracks.sensor_height)

    data['Camera FocusDistance'] = []
    data['Camera FocusDistance'].append(camera_tracks.focus_distance)

    data['Camera Aperture'] = []
    data['Camera Aperture'].append(camera_tracks.aperture_fstop)

    data['Camera Spawned'] = []
    data['Camera Spawned'].append(camera_tracks.hide_viewport)

    return data


def WriteSingleMeshAdditionalParameter(obj):

    scene = bpy.context.scene
    config = configparser.ConfigParser(allow_no_value=True)
    sockets = []
    for socket in GetSocketDesiredChild(obj):
        sockets.append(socket)

    # Comment
    config.add_section('Comment')
    config.set('Comment', '; This file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons')
    config.set('Comment', '; This file contains Additional StaticMesh and SkeletalMesh parameters informations that is not supported with .fbx files')
    config.set('Comment', '; The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python')

    # Defaultsettings
    config.add_section('DefaultSettings')
    # config.set('Defaultsettings', 'SocketNumber', str(len(sockets)))

    # Level of detail
    config.add_section("LevelOfDetail")
    if obj.Ue4Lod1 is not None:
        loc = os.path.join(GetObjExportDir(obj.Ue4Lod1, True), GetObjExportFileName(obj.Ue4Lod1))
        config.set('LevelOfDetail', 'lod_1', str(loc))
    if obj.Ue4Lod2 is not None:
        loc = os.path.join(GetObjExportDir(obj.Ue4Lod2, True), GetObjExportFileName(obj.Ue4Lod2))
        config.set('LevelOfDetail', 'lod_2', str(loc))
    if obj.Ue4Lod3 is not None:
        loc = os.path.join(GetObjExportDir(obj.Ue4Lod3, True), GetObjExportFileName(obj.Ue4Lod3))
        config.set('LevelOfDetail', 'lod_3', str(loc))
    if obj.Ue4Lod4 is not None:
        loc = os.path.join(GetObjExportDir(obj.Ue4Lod4, True), GetObjExportFileName(obj.Ue4Lod4))
        config.set('LevelOfDetail', 'lod_4', str(loc))
    if obj.Ue4Lod5 is not None:
        loc = os.path.join(GetObjExportDir(obj.Ue4Lod5, True), GetObjExportFileName(obj.Ue4Lod5))
        config.set('LevelOfDetail', 'lod_5', str(loc))

    # Sockets
    if GetAssetType(obj) == "SkeletalMesh":

        config.add_section('Sockets')
        config.set('Sockets', '; SocketName, BoneName, Location, Rotation, Scale')
        addon_prefs = bpy.context.preferences.addons[__package__].preferences

        for i, socket in enumerate(sockets):
            if socket.name.startswith("SOCKET_"):
                SocketName = socket.name[7:]
            else:
                socket.name

            if socket.parent.exportDeformOnly:
                b = getFirstDeformBoneParent(socket.parent.data.bones[socket.parent_bone])
            else:
                b = socket.parent.data.bones[socket.parent_bone]

            ResetArmaturePose(socket.parent)
            # GetRelativePostion
            bml = b.matrix_local  # Bone
            am = socket.parent.matrix_world  # Armature
            em = socket.matrix_world  # Socket
            RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
            t = RelativeMatrix.to_translation()
            r = RelativeMatrix.to_euler()
            s = socket.scale*addon_prefs.skeletalSocketsImportedSize

            # Convet to array for configparser and convert value for Unreal
            array_location = [t[0], t[1]*-1, t[2]]
            array_rotation = [degrees(r[0]), degrees(r[1])*-1, degrees(r[2])*-1]
            array_scale = [s[0], s[1], s[2]]

            MySocket = [SocketName, b.name.replace('.', '_'), array_location, array_rotation, array_scale]
            config.set('Sockets', 'socket_'+str(i), str(MySocket))

    return config


def WriteAllTextFiles():

    scene = bpy.context.scene
    if scene.text_ExportLog:
        Text = ti("write_text_additional_track_start") + "\n"
        Text += "" + "\n"
        Text += WriteExportLog()
        if Text is not None:
            Filename = ValidFilename(scene.file_export_log_name)
            ExportSingleText(Text, scene.export_other_file_path, Filename)

    # Import script
    if scene.text_ImportAssetScript:
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        Text = bfu_write_import_asset_script.WriteImportAssetScript()
        if Text is not None:
            Filename = ValidFilename(scene.file_import_asset_script_name)
            ExportSingleText(Text, scene.export_other_file_path, Filename)

    if scene.text_ImportSequenceScript:
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        Text = bfu_write_import_sequencer_script.WriteImportSequencerScript()
        if Text is not None:
            Filename = ValidFilename(scene.file_import_sequencer_script_name)
            ExportSingleText(Text, scene.export_other_file_path, Filename)

    # ConfigParser
    '''
    if scene.text_ImportAssetScript:
        Text = WriteExportedAssetsDetail()
        if Text is not None:
            Filename = "ExportedAssetsDetail.ini"
            ExportSingleConfigParser(
                Text,
                scene.export_other_file_path,
                Filename)

    if scene.text_ImportSequenceScript:
        Text = WriteSequencerDetail()
        if Text is not None:
            Filename = "SequencerDetail.ini"
            ExportSingleConfigParser(
                Text,
                scene.export_other_file_path,
                Filename)
    '''
