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
from math import degrees, radians, tan
from mathutils import Matrix
import json
from . import languages
from .languages import *
from shutil import copyfile

from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_write_import_asset_script
from . import bfu_write_import_sequencer_script
from .export import bfu_export_get_info
from .export.bfu_export_get_info import *

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
    if "bfu_export_get_info" in locals():
        importlib.reload(bfu_export_get_info)


def ExportSingleText(text, dirpath, filename):
    # Export single text

    counter = CounterTimer()

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, "w") as file:
        file.write(text)

    exportTime = counter.GetTime()
    # This return [AssetName , AssetType , ExportPath, ExportTime]
    return([filename, "TextFile", absdirpath, exportTime])


def ExportSingleJson(json_data, dirpath, filename):
    # Export single Json

    counter = CounterTimer()

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    fullpath = os.path.join(absdirpath, filename)

    with open(fullpath, 'w') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, sort_keys=False, indent=4)

    exportTime = counter.GetTime()
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
            if asset.object:
                if asset.object.ExportAsLod:
                    primaryInfo = asset.asset_type+" (LOD)"
                else:
                    primaryInfo = asset.asset_type
            else:
                primaryInfo = asset.asset_type

        ExportLog += (
            asset.asset_name+" ["+primaryInfo+"] EXPORTED IN " + str(round(asset.GetExportTime(), 2))+"s\r\n")
        for file in asset.files:
            ExportLog += (file.path + "\\" + file.name + "\n")
        ExportLog += "\n"

    return ExportLog


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

        def EvaluateTracksAtFrame(self, camera, frame):
            scene.frame_set(frame)

            array_transform = EvaluateCameraPositionForUnreal(camera)
            array_location = array_transform[0]
            array_rotation = array_transform[1]
            array_scale = array_transform[2]

            # Fix axis flippings
            if frame-1 in self.transform_track:
                previous_rotation_z = self.transform_track[frame-1]["rotation_z"]
                diff = round((array_rotation[2] - previous_rotation_z) / 180.0) * 180.0
                array_rotation[2] = array_rotation[2] - diff

            transform = {}
            transform["location_x"] = array_location.x
            transform["location_y"] = array_location.y
            transform["location_z"] = array_location.z
            transform["rotation_x"] = array_rotation[0]
            transform["rotation_y"] = array_rotation[1]
            transform["rotation_z"] = array_rotation[2]
            transform["scale_x"] = array_scale.x
            transform["scale_y"] = array_scale.y
            transform["scale_z"] = array_scale.z
            self.transform_track[frame] = transform

            # Get FocalLength SensorWidth SensorHeight
            self.lens[frame] = getOneKeysByFcurves(camera, "lens", camera.data.lens, frame)
            self.sensor_width[frame] = getOneKeysByFcurves(camera, "sensor_width", camera.data.sensor_width, frame)
            self.sensor_height[frame] = getOneKeysByFcurves(camera, "sensor_height", camera.data.sensor_height, frame)

            # Get FocusDistance
            scale_length = bpy.context.scene.unit_settings.scale_length

            if camera.data.dof.focus_object is not None:
                key = getCameraFocusDistance(camera, camera.data.dof.focus_object)
                key = key * 100 * scale_length

            else:
                key = getOneKeysByFcurves(camera, "dof.focus_distance", camera.data.dof.focus_distance, frame)
                key = key * 100 * scale_length

            if key > 0:
                self.focus_distance[frame] = key
            else:
                self.focus_distance[frame] = 100000  # 100000 is default value in ue4

            # Write Aperture (Depth of Field) keys
            render_engine = scene.render.engine
            if render_engine == "BLENDER_EEVEE" or render_engine == "CYCLES" or render_engine == "BLENDER_WORKBENCH":
                key = getOneKeysByFcurves(camera, "dof.aperture_fstop", camera.data.dof.aperture_fstop, frame)
                self.aperture_fstop[frame] = key / scale_length
            else:
                self.aperture_fstop[frame] = 2.8  # 2.8 is default value in ue4

            boolKey = getOneKeysByFcurves(camera, "hide_viewport", camera.hide_viewport, frame, False)
            self.hide_viewport[frame] = (boolKey < 1)  # Inversed for convert hide to spawn

        def EvaluateTracks(self, camera, frame_start, frame_end):
            scene = bpy.context.scene
            addon_prefs = GetAddonPrefs()

            saveFrame = scene.frame_current
            if camera is None:
                return

            slms = TimelineMarkerSequence()
            for frame in range(frame_start, frame_end+1):
                if len(slms.marker_sequences) > 0 and addon_prefs.bakeOnlyKeyVisibleInCut:
                    marker_sequence = slms.GetMarkerSequenceAtFrame(frame)
                    if marker_sequence:
                        marker = marker_sequence.marker
                        if marker.camera == camera:
                            self.EvaluateTracksAtFrame(camera, frame)
                else:
                    self.EvaluateTracksAtFrame(camera, frame)

            scene.frame_set(saveFrame)

        pass

    scene = bpy.context.scene
    data = {}
    data['Coment'] = {
        '1/3': ti('write_text_additional_track_start'),
        '2/3': ti('write_text_additional_track_camera'),
        '3/3': ti('write_text_additional_track_end'),
    }

    data['Frames'] = []
    data['Frames'].append({
        'frame_start': scene.frame_start,
        'frame_end': scene.frame_end,
    })

    camera_tracks = CameraDataAtFrame()
    camera_tracks.EvaluateTracks(obj, scene.frame_start, scene.frame_end)

    data['Camera transform'] = camera_tracks.transform_track
    data['Camera FocalLength'] = camera_tracks.lens
    data['Camera SensorWidth'] = camera_tracks.sensor_width
    data['Camera SensorHeight'] = camera_tracks.sensor_height
    data['Camera FocusDistance'] = camera_tracks.focus_distance
    data['Camera Aperture'] = camera_tracks.aperture_fstop
    data['Camera Spawned'] = camera_tracks.hide_viewport

    return data


def WriteSingleMeshAdditionalParameter(unreal_exported_asset):

    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()
    obj = unreal_exported_asset.object

    data = {}

    # Comment
    data['Coment'] = {
        '1/3': ti('write_text_additional_track_start'),
        '2/3': ti('write_text_additional_track_all'),
        '3/3': ti('write_text_additional_track_end'),
    }

    # Defaultsettings
    data['DefaultSettings'] = {}
    # config.set('Defaultsettings', 'SocketNumber', str(len(sockets)))

    # Level of detail
    if obj:
        data['LevelOfDetail'] = {}
        if obj.Ue4Lod1 is not None:
            loc = os.path.join(GetObjExportDir(obj.Ue4Lod1, True), GetObjExportFileName(obj.Ue4Lod1))
            data['LevelOfDetail']['lod_1'] = loc
        if obj.Ue4Lod2 is not None:
            loc = os.path.join(GetObjExportDir(obj.Ue4Lod2, True), GetObjExportFileName(obj.Ue4Lod2))
            data['LevelOfDetail']['lod_2'] = loc
        if obj.Ue4Lod3 is not None:
            loc = os.path.join(GetObjExportDir(obj.Ue4Lod3, True), GetObjExportFileName(obj.Ue4Lod3))
            data['LevelOfDetail']['lod_3'] = loc
        if obj.Ue4Lod4 is not None:
            loc = os.path.join(GetObjExportDir(obj.Ue4Lod4, True), GetObjExportFileName(obj.Ue4Lod4))
            data['LevelOfDetail']['lod_4'] = loc
        if obj.Ue4Lod5 is not None:
            loc = os.path.join(GetObjExportDir(obj.Ue4Lod5, True), GetObjExportFileName(obj.Ue4Lod5))
            data['LevelOfDetail']['lod_5'] = loc

    # Sockets
    if obj:
        data['Sockets'] = GetSkeletalMeshSockets(obj)

    # Vertex Color
    if obj:
        if GetAssetType(obj) == "SkeletalMesh" or GetAssetType(obj) == "StaticMesh":
            vced = VertexColorExportData(obj)
            data["vertex_color_import_option"] = vced.export_type
            vertex_override_color = (
                vced.color[0],  # R
                vced.color[1],  # G
                vced.color[2]  # B
            )  # Color to Json
            data["vertex_override_color"] = vertex_override_color

    data["preview_import_path"] = unreal_exported_asset.GetFilename()
    return data


def WriteAllTextFiles():

    scene = bpy.context.scene
    addon_prefs = GetAddonPrefs()

    if scene.text_ExportLog:
        Text = ti("write_text_additional_track_start") + "\n"
        Text += "" + "\n"
        Text += WriteExportLog()
        if Text is not None:
            Filename = ValidFilename(scene.file_export_log_name)
            ExportSingleText(Text, scene.export_other_file_path, Filename)

    # Import script
    bfu_path = os.path.join("addons", "blender-for-unrealengine", "import")
    bfu_path_ref = os.path.join(bpy.utils.user_resource('SCRIPTS'), bfu_path)

    if scene.text_ImportAssetScript:
        json_data = bfu_write_import_asset_script.WriteImportAssetScript()
        ExportSingleJson(json_data, scene.export_other_file_path, "ImportAssetData.json")
        source = os.path.join(bfu_path_ref, "asset_import_script.py")
        filename = ValidFilename(scene.file_import_asset_script_name)
        destination = bpy.path.abspath(os.path.join(scene.export_other_file_path, filename))
        copyfile(source, destination)

    if scene.text_ImportSequenceScript:
        json_data = bfu_write_import_sequencer_script.WriteImportSequencerTracks()
        ExportSingleJson(json_data, scene.export_other_file_path, "ImportSequencerData.json")
        source = os.path.join(bfu_path_ref, "sequencer_import_script.py")
        filename = ValidFilename(scene.file_import_sequencer_script_name)
        destination = bpy.path.abspath(os.path.join(scene.export_other_file_path, filename))
        copyfile(source, destination)
