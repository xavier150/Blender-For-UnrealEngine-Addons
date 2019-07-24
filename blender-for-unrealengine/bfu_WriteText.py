#====================== BEGIN GPL LICENSE BLOCK ============================
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
#======================= END GPL LICENSE BLOCK =============================


import bpy
import time
import configparser
from math import degrees, radians
from mathutils import Matrix


import importlib
from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *

from . import bfu_Utils
importlib.reload(bfu_Utils)
from .bfu_Utils import *

from . import bfu_WriteImportAssetScript
importlib.reload(bfu_WriteImportAssetScript)

from . import bfu_WriteImportSequencerScript
importlib.reload(bfu_WriteImportSequencerScript)


def ExportSingleText(text, dirpath, filename):
	#Export single text

	filename = ValidFilename(filename)
	curr_time = time.process_time()

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	with open(fullpath, "w") as file:
		file.write(text)

	exportTime = time.process_time()-curr_time
	return([filename,"TextFile",absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]

def ExportSingleConfigParser(config, dirpath, filename):
	#Export single ConfigParser

	filename = ValidFilename(filename)
	curr_time = time.process_time()

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	with open(fullpath, "w") as configfile:
		config.write(configfile)

	exportTime = time.process_time()-curr_time
	return([filename,"TextFile",absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]

def WriteExportLog():
	#Write Export log with exported assets in scene.UnrealExportedAssetsList

	scene = bpy.context.scene
	StaticNum = 0
	SkeletalNum = 0
	AlembicNum = 0
	AnimNum = 0
	CameraNum = 0

	for assets in scene.UnrealExportedAssetsList:
		if assets.assetType == "StaticMesh":
			StaticNum+=1
		if assets.assetType == "SkeletalMesh":
			SkeletalNum+=1
		if assets.assetType == "Alembic":
			AlembicNum+=1
		if GetIsAnimation(assets.assetType):
			AnimNum+=1
		if assets.assetType == "Camera":
			CameraNum+=1

	OtherNum = len(scene.UnrealExportedAssetsList)-(StaticNum+SkeletalNum+AlembicNum+AnimNum+CameraNum)

	AssetNumberByType = str(StaticNum)+" StaticMesh(s) | "
	AssetNumberByType += str(SkeletalNum)+" SkeletalMesh(s) | "
	AssetNumberByType += str(AlembicNum)+" Alembic(s) | "
	AssetNumberByType += str(AnimNum)+" Animation(s) | "
	AssetNumberByType += str(CameraNum)+" Camera(s) | "
	AssetNumberByType += str(OtherNum)+" Other(s)" + "\n"

	ExportLog = "..." + "\n"
	ExportLog += AssetNumberByType
	ExportLog += "\n"
	for asset in scene.UnrealExportedAssetsList:

		if (asset.assetType == "NlAnim"):
			primaryInfo = "Animation"
			secondaryInfo = "(NLA)"
		elif (asset.assetType == "Action"):
			primaryInfo = "Animation"
			secondaryInfo = "(Action)"
		elif (asset.assetType == "Pose"):
			primaryInfo = "Animation"
			secondaryInfo = "(Pose)"
		else:
			primaryInfo = asset.assetType
			secondaryInfo = " (LOD)" if asset.object.ExportAsLod == True else ""

		ExportLog +=("["+primaryInfo+"]"+secondaryInfo+" -> "+"\""+asset.assetName+"\" exported in "+str(asset.exportTime)+" sec.\n")
		ExportLog +=(asset.exportPath + "\n")
		ExportLog += "\n"

	return ExportLog


def WriteImportPythonHeadComment(use20tab = False, useSequencer = False):

	scene = bpy.context.scene

	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	if useSequencer == True:
		ImportScript += "#It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose" + "\n"
	else:
		ImportScript += "#This script will import in unreal all camera in target sequencer" + "\n"
	if use20tab == True:
		ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	else:
		ImportScript += "#The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python" + "\n"
	if useSequencer == True:
		ImportScript += "#Use this command : " + GetImportSequencerScriptCommand() + "\n"
	else:
		ImportScript += "#Use this command : " + GetImportAssetScriptCommand() + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	return ImportScript

def WriteExportedAssetsDetail():
	#Generate a config file for import assets in Ue4
	scene = bpy.context.scene
	config = configparser.ConfigParser(allow_no_value=True)



	def getSectionNameByAsset(asset):
		#GetObjExportFileName(asset.object, "")
		return "ASSET_" + GetObjExportFileName(asset.object, "")

	def completeAssetSection(config, asset):
		#Complete the section of an asset

		obj = asset.object
		AssetSectionName = getSectionNameByAsset(asset)
		if (config.has_section(AssetSectionName) == False):
			config.add_section(AssetSectionName)

		config.set(AssetSectionName, 'name', GetObjExportFileName(asset.object, ""))
		config.set(AssetSectionName, 'mesh_import_path', os.path.join(obj.exportFolderName) )

		#Mesh only
		if (asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh"):
			fbx_path = (os.path.join(asset.exportPath, asset.assetName))
			config.set(AssetSectionName, 'lod0_fbx_path', fbx_path)
			config.set(AssetSectionName, 'asset_type', asset.assetType)
			config.set(AssetSectionName, 'material_search_location', obj.MaterialSearchLocation)
			config.set(AssetSectionName, 'generate_lightmap_uvs', str(obj.GenerateLightmapUVs))
			config.set(AssetSectionName, 'create_physics_asset', str(obj.CreatePhysicsAsset))
			if (obj.UseStaticMeshLODGroup == True):
				config.set(AssetSectionName, 'static_mesh_lod_group', obj.StaticMeshLODGroup)
			if (obj.UseStaticMeshLightMapRes == True):
				config.set(AssetSectionName, 'light_map_resolution', str(obj.StaticMeshLightMapRes))



		#Anim only
		if GetIsAnimation(asset.assetType):
			actionIndex = 0
			animOption = "anim"+str(actionIndex)
			while config.has_option(AssetSectionName, animOption+'_fbx_path') == True:
				actionIndex += 1
				animOption = "anim"+str(actionIndex)

			fbx_path = (os.path.join(asset.exportPath, asset.assetName))
			config.set(AssetSectionName, animOption+'_fbx_path', fbx_path)
			config.set(AssetSectionName, animOption+'_import_path', os.path.join(obj.exportFolderName, scene.anim_subfolder_name) )


	AssetForImport = []
	for asset in scene.UnrealExportedAssetsList:
		if (asset.assetType == "StaticMesh"
		or asset.assetType == "SkeletalMesh"
		or GetIsAnimation(asset.assetType)):
			AssetForImport.append(asset)


	#Comment
	config.add_section('Comment')
	config.set('Comment', '; This config file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons')
	config.set('Comment', '; The config must be used in Unreal Engine Editor with the plugin BlenderImporter : ...')
	config.set('Comment', '; It used for import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose')

	config.add_section('Defaultsettings')
	config.set('Defaultsettings', 'unreal_import_location', r'/Game/'+scene.unreal_import_location)

	for asset in AssetForImport:
		completeAssetSection(config, asset)

	#Import asset
	return config

def WriteSingleCameraAdditionalTrack(obj):

	def getCameraFocusDistance(Camera, Target):
		transA = Camera.matrix_world.copy()
		transB = Target.matrix_world.copy()
		transA.invert()
		distance = (transA @ transB).translation.z #Z is the Fosrward
		if distance < 0:
			distance *= -1
		return distance

	def getAllCamDistKeys(Camera, Target):
		scene = bpy.context.scene
		saveFrame = scene.frame_current #Save current frame
		keys = []
		for frame in range(scene.frame_start, scene.frame_end+1):
			scene.frame_set(frame)
			v = getCameraFocusDistance(Camera, Target)
			keys.append((frame,v))
		scene.frame_set(saveFrame)	#Resets previous start frame
		return keys

	def getAllKeysByMatrix(obj):
		scene = bpy.context.scene
		saveFrame = scene.frame_current #Save current frame
		keys = []
		for frame in range(scene.frame_start, scene.frame_end+1):
			scene.frame_set(frame)
			v = obj.matrix_world*1
			keys.append((frame,v))
		scene.frame_set(saveFrame)	#Resets previous start frame
		return keys

	def getOneKeysByFcurves(obj,DataPath, DataValue, Frame, IsData = True):
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

	def getAllKeysByFcurves(obj,DataPath, DataValue, IsData = True):
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
				keys.append((frame,v))
			return keys
		return[(scene.frame_start,DataValue)]

	scene = bpy.context.scene
	ImportScript = ";This file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += ";This file contains additional Camera animation informations that is not supported with .fbx files" + "\n"
	ImportScript += ";The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "\n\n\n"

	#Write TransformMatrix keys
	ImportScript += "[Transform]" + "\n"
	for key in getAllKeysByMatrix(obj):
		#GetWorldPostion
		matrix = key[1] * Matrix.Rotation(radians(90.0), 4, 'Y') * Matrix.Rotation(radians(-90.0), 4, 'X')
		l = matrix.to_translation() * 100
		r = matrix.to_euler()
		s = matrix.to_scale()

		array_location = [l[0], l[1]*-1, l[2]]
		array_rotation = [degrees(r[0]), degrees(r[1])*-1, degrees(r[2])*-1]
		array_scale = [s[0], s[1], s[2]]


		transform = [array_location[0], array_location[1], array_location[2], array_rotation[0], array_rotation[1], array_rotation[2], array_scale[0], array_scale[1], array_scale[2]]
		strTransform = ""
		for t in transform:
			strTransform += str(t)+","
		ImportScript += str(key[0])+": " + strTransform + "\n"
	ImportScript += "\n\n\n"

	#Write FocalLength keys
	ImportScript += "[FocalLength]" + "\n"
	for key in getAllKeysByFcurves(obj,"lens",obj.data.lens):
		#Fov type return auto to lens
		ImportScript += str(key[0])+": "+str(key[1]) + "\n"
	ImportScript += "\n\n\n"

	#Write FocusDistance keys
	ImportScript += "[FocusDistance]" + "\n"
	if obj.data.dof_object is None:
		DataKeys = getAllKeysByFcurves(obj,"dof_distance",obj.data.dof_distance)
	else:
		DataKeys = getAllCamDistKeys(obj, obj.data.dof_object)
	for key in DataKeys:
		CorrectedValue = key[1]*100
		if CorrectedValue > 0:
			ImportScript += str(key[0])+": "+str(CorrectedValue) + "\n"
		else:
			ImportScript += str(key[0])+": "+str(100000) + "\n" #100000 is default value in ue4
	ImportScript += "\n\n\n"

	#Write Aperture (Depth of Field) keys
	ImportScript += "[Aperture]" + "\n"
	if scene.render.engine == 'CYCLES':
		if obj.data.cycles.aperture_type == 'FSTOP':
			DataKeys = getAllKeysByFcurves(obj,"cycles.aperture_fstop",obj.data.cycles.aperture_fstop)
		else:
			DataKeys = getAllKeysByFcurves(obj,"cycles.aperture_size",obj.data.cycles.aperture_size)
		for key in DataKeys:
			CorrectedValue = key[1]
			if obj.data.cycles.aperture_type == 'RADIUS':
				#Convert radius to Fstop
				FocalLength = getOneKeysByFcurves(obj,"lens",obj.data.lens,key[0])
				if CorrectedValue == 0:
					CorrectedValue = 64
				else:
					CorrectedValue = (FocalLength/(key[1]*2000))
			ImportScript += str(key[0])+": "+str(CorrectedValue) + "\n"

	else:
		ImportScript += "0: 21\n" #21 is default value in ue4
	ImportScript += "\n\n\n"

	#Write Spawned keys
	ImportScript += "[Spawned]" + "\n"
	lastKeyValue = None
	for key in getAllKeysByFcurves(obj,"hide",obj.hide, False):
		boolKey = (key[1] < 1) #Inversed for convert hide to spawn
		if lastKeyValue is None:
			ImportScript += str(key[0])+": "+str(boolKey) + "\n"
			lastKeyValue = boolKey
		else:
			if boolKey != lastKeyValue:
				ImportScript += str(key[0])+": "+str(boolKey) + "\n"
				lastKeyValue = boolKey
	ImportScript += "\n\n\n"

	return ImportScript

def WriteSingleMeshAdditionalParameter(obj):

	scene = bpy.context.scene
	config = configparser.ConfigParser(allow_no_value=True)
	sockets = []
	for socket in GetSocketDesiredChild(obj):
		sockets.append(socket)

	#Comment
	config.add_section('Comment')
	config.set('Comment', '; This file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons')
	config.set('Comment', '; This file contains Additional StaticMesh and SkeletalMesh parameters informations that is not supported with .fbx files')
	config.set('Comment', '; The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython')

	#Defaultsettings
	config.add_section('DefaultSettings')
	#config.set('Defaultsettings', 'SocketNumber', str(len(sockets)))

	#Level of detail
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

	#Sockets
	if GetAssetType(obj) == "SkeletalMesh":

		config.add_section('Sockets')
		config.set('Sockets', '; SocketName, BoneName, Location, Rotation, Scale')
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences

		for i, socket in enumerate(sockets):
			SocketName = socket.name[7:] if socket.name.startswith("SOCKET_") else socket.name

			if socket.parent.exportDeformOnly == True:
				b = getFirstDeformBoneParent(socket.parent.data.bones[socket.parent_bone])
			else:
				b = socket.parent.data.bones[socket.parent_bone]

			ResetArmaturePose(socket.parent)
			#GetRelativePostion
			bml = b.matrix_local #Bone
			am = socket.parent.matrix_world #Armature
			em = socket.matrix_world #Socket
			RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
			l = RelativeMatrix.to_translation()
			r = RelativeMatrix.to_euler()
			s = socket.scale*addon_prefs.SkeletalSocketsImportedSize

			#Convet to array for configparser and convert value for Unreal
			array_location = [l[0], l[1]*-1, l[2]]
			array_rotation = [degrees(r[0]), degrees(r[1])*-1, degrees(r[2])*-1]
			array_scale = [s[0], s[1], s[2]]

			MySocket = [SocketName, b.name.replace('.','_'), array_location, array_rotation, array_scale]
			config.set('Sockets', 'socket_'+str(i), str(MySocket))


	return config

def WriteAllTextFiles():

	scene = bpy.context.scene
	if scene.text_ExportLog:
		Text = WriteExportLog()
		if Text is not None:
			Filename = scene.file_export_log_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)

	#Import script
	if scene.text_ImportAssetScript:
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences
		Text = bfu_WriteImportAssetScript.WriteImportAssetScript(addon_prefs.Use20TabScript)
		if Text is not None:
			Filename = scene.file_import_asset_script_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)

	if scene.text_ImportSequenceScript:
		addon_prefs = bpy.context.user_preferences.addons["blender-for-unrealengine"].preferences
		Text = bfu_WriteImportSequencerScript.WriteImportSequencerScript(addon_prefs.Use20TabScript)
		if Text is not None:
			Filename = scene.file_import_sequencer_script_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)

	#ConfigParser
	'''
	if scene.text_ImportAssetScript:
		Text = WriteExportedAssetsDetail()
		if Text is not None:
			Filename = "ExportedAssetsDetail.ini"
			ExportSingleConfigParser(Text, scene.export_other_file_path, Filename)

	if scene.text_ImportSequenceScript:
		Text = WriteSequencerDetail()
		if Text is not None:
			Filename = "SequencerDetail.ini"
			ExportSingleConfigParser(Text, scene.export_other_file_path, Filename)
	'''
