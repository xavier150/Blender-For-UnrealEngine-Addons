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
from math import degrees


import importlib
from . import bfu_basics
importlib.reload(bfu_basics)
from .bfu_basics import *

from . import bfu_utils
importlib.reload(bfu_utils)
from .bfu_utils import *


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
	AnimNum = 0
	CameraNum = 0
	
	for assets in scene.UnrealExportedAssetsList:
		if assets.assetType == "StaticMesh":
			StaticNum+=1
		if assets.assetType == "SkeletalMesh":
			SkeletalNum+=1
		if GetIsAnimation(assets.assetType):
			AnimNum+=1
		if assets.assetType == "Camera":
			CameraNum+=1
	
	OtherNum = len(scene.UnrealExportedAssetsList)-(StaticNum+SkeletalNum+AnimNum+CameraNum)
	
	AssetNumberByType = str(StaticNum)+" StaticMesh(s) | "
	AssetNumberByType += str(SkeletalNum)+" SkeletalMesh(s) | "
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

def WriteImportAssetScript():
	#Generate a script for import assets in Ue4
	scene = bpy.context.scene

	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += "#It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose" + "\n"
	ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "#Use this command : " + GetImportAssetScriptCommand() + "\n"
	ImportScript += "\n"
	ImportScript += "import os.path" + "\n"
	ImportScript += "import configparser" + "\n"
	ImportScript += "import ast" + "\n"
	ImportScript += "import unreal_engine as ue" + "\n"
	ImportScript += "from unreal_engine.classes import PyFbxFactory, StaticMesh, Skeleton, SkeletalMeshSocket" + "\n"
	ImportScript += "from unreal_engine.enums import EFBXImportType, EMaterialSearchLocation" + "\n"
	ImportScript += "from unreal_engine.structs import StaticMeshSourceModel, MeshBuildSettings" + "\n"
	ImportScript += "from unreal_engine import FVector, FRotator" + "\n"
	ImportScript += "\n"
		
	#Prepare var and def
	ImportScript += "#Prepare var and def" + "\n"
	ImportScript += "UnrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
	ImportScript += "ImportedAsset = []" + "\n"
	ImportScript += "\n"
	
	
	ImportScript += "def GetOptionByIniFile(FileLoc, OptionName, literal = False):" + "\n"
	ImportScript += "\t" + "Config = configparser.ConfigParser()" + "\n"
	ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t" + "Options = []" + "\n"
	ImportScript += "\t" + 'for option in Config.options(OptionName):' + "\n"
	ImportScript += "\t\t" + 'if (literal == True):' + "\n"
	ImportScript += "\t\t\t" + 'Options.append(ast.literal_eval(Config.get(OptionName, option)))' + "\n"
	ImportScript += "\t\t" + 'else:' + "\n"
	ImportScript += "\t\t\t" + 'Options.append(Config.get(OptionName, option))' + "\n"
	ImportScript += "\t" + "return Options" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	#Process import
	ImportScript += "#Process import" + "\n"
	ImportScript += "print('========================= Import started ! =========================')" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	#Import asset
	for asset in scene.UnrealExportedAssetsList:		
		if (asset.object.ExportAsLod == False and 
		(asset.assetType == "StaticMesh" 
		or asset.assetType == "SkeletalMesh"
		or GetIsAnimation(asset.assetType))
		):		
			
			obj = asset.object
			MeshRelatifImportLoc = obj.exportFolderName
			AnimRelatifImportLoc = os.path.join( obj.exportFolderName, scene.anim_subfolder_name )
			FbxLoc = (os.path.join(asset.exportPath, asset.assetName))
			AdditionalParameterLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalParameter.ini")))
			ImportScript += "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"			
			
			
			#StaticMesh and skeletalMesh
			ImportScript += "fbx_factory = PyFbxFactory()" + "\n"
			ImportScript += "fbx_factory.ImportUI.bImportMaterials = True" + "\n"
			ImportScript += "fbx_factory.ImportUI.bImportTextures = False" + "\n"
			ImportScript += "fbx_factory.ImportUI.TextureImportData.MaterialSearchLocation = EMaterialSearchLocation." + obj.MaterialSearchLocation + "\n"
			if asset.assetType == "StaticMesh":
				ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bCombineMeshes = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bAutoGenerateCollision = "+ str(obj.AutoGenerateCollision) + "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.StaticMeshLODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
					ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bGenerateLightmapUVs = " + str(obj.GenerateLightmapUVs) + "\n"
	
			if asset.assetType == "SkeletalMesh":
				ImportScript += "fbx_factory.ImportUI.bImportAnimations = False" + "\n"
				ImportScript += "fbx_factory.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.bCreatePhysicsAsset = " + str(obj.CreatePhysicsAsset) + "\n"

			ImportScript += "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"			
			ImportScript += "AdditionalParameterLoc = os.path.join(r'"+AdditionalParameterLoc+"')" + "\n"	
			ImportScript += "AssetImportLocation = (os.path.join(UnrealImportLocation, r'"+MeshRelatifImportLoc+r"').replace('\\','/')).rstrip('/')" + "\n"




			#Animation				
			if GetIsAnimation(asset.assetType):
				SkeletonName = scene.skeletal_prefix_export_name+obj.name+"_Skeleton."+scene.skeletal_prefix_export_name+obj.name+"_Skeleton"
				SkeletonLoc = os.path.join(obj.exportFolderName,SkeletonName)
				ImportScript += "SkeletonLocation = os.path.join(UnrealImportLocation, r'" + SkeletonLoc + r"').replace('\\','/')" + "\n"
				ImportScript += "OriginSkeleton = ue.find_asset(SkeletonLocation)" + "\n"
				ImportScript += "if OriginSkeleton:" + "\n"
				ImportScript += "\t" + "fbx_factory = PyFbxFactory()" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.bImportMesh = False" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.bCreatePhysicsAsset = False" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.Skeleton = OriginSkeleton" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.bImportAnimations = True" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.MeshTypeToImport = EFBXImportType.FBXIT_Animation" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
				ImportScript += "\t" + "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"			
				ImportScript += "\t" + r"AssetImportLocation = (os.path.join(UnrealImportLocation, r'"+AnimRelatifImportLoc+r"').replace('\\','/')).rstrip('/')" + "\n"
				#-----------Import
				ImportScript += "\t" + "try:" + "\n"

				#Import report
				ImportScript += "\t\t" + "asset.save_package()" + "\n"
				ImportScript += "\t\t" + "asset.post_edit_change()" + "\n"
				ImportScript += "\t\t" + "asset = fbx_factory.factory_import_object(FbxLoc, AssetImportLocation)" + "\n"
				ImportScript += "\t\t" + "ImportedAsset.append(asset)" + "\n"
				ImportScript += "\t" + "except:" + "\n"
				ImportScript += "\t\t" + "ImportedAsset.append('Import error for asset named \""+obj.name+"\" ')" + "\n"
				ImportScript += "else:" + "\n"
				ImportScript += "\t" + "ImportedAsset.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"

			#Static and skeletal	
			else:
				#-----------Import
				ImportScript += "try:" + "\n"
				ImportScript += "\t" + "asset = fbx_factory.factory_import_object(FbxLoc, AssetImportLocation)" + "\n"
				if asset.assetType == "StaticMesh":
					if (obj.UseStaticMeshLODGroup == True):
						ImportScript += "\t" "asset.LODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
					if (obj.UseStaticMeshLightMapRes == True):
						ImportScript += "\t" "asset.LightMapResolution = " + str(obj.StaticMeshLightMapRes) + "\n"
				if asset.assetType == "SkeletalMesh":
					ImportScript += "\t" + "skeleton = asset.skeleton" + "\n"
					ImportScript += "\t" + "if skeleton.is_a(Skeleton):" + "\n"
					#Sockets
					ImportScript += "\t\t" + "current_sockets = skeleton.Sockets" + "\n"
					ImportScript += "\t\t" + "new_sockets = []" + "\n"
					ImportScript += "\t\t" + "sockets_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'Sockets', True)" + "\n"
					ImportScript += "\t\t" + "for socket in sockets_to_add :" + "\n"

					#Create socket
					ImportScript += "\t\t\t" + "#Create socket" + "\n"
					ImportScript += "\t\t\t" + "new_socket = SkeletalMeshSocket('', skeleton)" + "\n"
					ImportScript += "\t\t\t" + "new_socket.SocketName = socket[0]" + "\n"
					ImportScript += "\t\t\t" + "print(socket[0])" + "\n"
					ImportScript += "\t\t\t" + "new_socket.BoneName = socket[1]" + "\n"
					ImportScript += "\t\t\t" + "l = socket[2]" + "\n"
					ImportScript += "\t\t\t" + "r = socket[3]" + "\n"
					ImportScript += "\t\t\t" + "s = socket[4]" + "\n"
					ImportScript += "\t\t\t" + "new_socket.RelativeLocation = FVector(l[0], l[1], l[2])" + "\n"
					ImportScript += "\t\t\t" + "new_socket.RelativeRotation = FRotator(r[0], r[1], r[2])" + "\n"
					ImportScript += "\t\t\t" + "new_socket.RelativeScale = FVector(s[0], s[1], s[2])" + "\n"
					ImportScript += "\t\t\t" + "new_sockets.append(new_socket)" + "\n"

					#Save socket
					#ImportScript += "\t\t" + "skeleton.Sockets = current_sockets + new_sockets" + "\n"
					ImportScript += "\t\t" + "skeleton.Sockets = new_sockets" + "\n"
					ImportScript += "\t\t" + "\n"		
				
				#Lod
				if asset.assetType == "StaticMesh": 
					ImportScript += "\t" + "lods_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'LevelOfDetail')" + "\n"
					ImportScript += "\t" + "for x, lod in enumerate(lods_to_add):" + "\n"
					ImportScript += "\t\t" + "asset.static_mesh_import_lod(lod, x+1)" + "\n"
				#if asset.assetType == "SkeletalMesh": 
					#ImportScript += "\t\t" + "#asset.skeletal_mesh_import_lod(lod, x+1)" + "\n"
				
				#Import report
				ImportScript += "\t" + "asset.save_package()" + "\n"
				ImportScript += "\t" + "asset.post_edit_change()" + "\n"		
				ImportScript += "\t" + "ImportedAsset.append(asset)" + "\n"
				ImportScript += "except:" + "\n"
				ImportScript += "\t" + "ImportedAsset.append('Import error for asset named \""+obj.name+"\" ')" + "\n"


			ImportScript += "\n"
			ImportScript += "\n"
			ImportScript += "\n"
	
	#import result
	ImportScript += "print('========================= Imports completed ! =========================')" + "\n"
	ImportScript += "\n"
	ImportScript += "for asset in ImportedAsset:" + "\n"
	ImportScript += "\t" + "print(asset)" + "\n"
	ImportScript += "\n"
	ImportScript += "print('=========================')" + "\n"
	
	return ImportScript
	
def WriteImportSequencerScript():
	#Generate a config file for import camera in Ue4 sequencer
	scene = bpy.context.scene
	
	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += "#This script will import in unreal all camera in target sequencer" + "\n"
	ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "#Use this command : " + GetImportSequencerScriptCommand() + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	#Import
	ImportScript += "import os.path" + "\n"
	ImportScript += "import time" + "\n"
	ImportScript += "import configparser" + "\n"
	ImportScript += "import unreal_engine as ue" + "\n"
	ImportScript += "from unreal_engine.classes import MovieSceneCameraCutTrack, MovieScene3DTransformSection, MovieScene3DTransformTrack, MovieSceneAudioTrack, CineCameraActor, LevelSequenceFactoryNew" + "\n"
	ImportScript += "if ue.ENGINE_MINOR_VERSION >= 20:" + "\n"
	ImportScript += "\t" + "from unreal_engine.structs import FloatRange, FloatRangeBound, MovieSceneObjectBindingID, FrameRate" + "\n"
	ImportScript += "else:" + "\n"
	ImportScript += "\t" + "from unreal_engine.structs import FloatRange, FloatRangeBound, MovieSceneObjectBindingID" + "\n"
	ImportScript += "from unreal_engine import FTransform, FVector, FColor" + "\n"
	ImportScript += "from unreal_engine.enums import EMovieSceneObjectBindingSpace" + "\n"
	ImportScript += "from unreal_engine.structs import MovieSceneObjectBindingID" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	
	#Prepare var	
	ImportScript += "seqLocation = r'"+os.path.join(r"/Game/",scene.unreal_levelsequence_import_location)+"'" + "\n"
	ImportScript += "seqName = r'"+scene.unreal_levelsequence_name+"'" + "\n"
	ImportScript += "seqTempName = r'"+scene.unreal_levelsequence_name+"'+str(time.time())" + "\n"
	ImportScript += "mustBeReplace = False" + "\n"
	ImportScript += "startFrame = " + str(scene.frame_start) + "\n"
	ImportScript += "endFrame = " + str(scene.frame_end+1) + "\n"
	ImportScript += "frameRateDenominator = " + str(scene.render.fps_base) + "\n"
	ImportScript += "frameRateNumerator = " + str(scene.render.fps) + "\n"
	ImportScript += "secureCrop = 0.0001 #add end crop for avoid section overlay" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	
	#Prepare def	
	ImportScript += "def AddSequencerSectionFloatKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	ImportScript += "\t" + "Config = configparser.ConfigParser()" + "\n"
	ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t" + "frame = float(option)/frameRateNumerator #FrameRate" + "\n"
	ImportScript += "\t\t" + "value = float(Config.get(SectionFileName, option))" + "\n"
	ImportScript += "\t\t" + "SequencerSection.sequencer_section_add_key(frame,value)" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	ImportScript += "def AddSequencerSectionBoolKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	ImportScript += "\t" + "Config = configparser.ConfigParser()" + "\n"
	ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t" + "frame = float(option)/frameRateNumerator #FrameRate" + "\n"
	ImportScript += "\t\t" + "value = Config.getboolean(SectionFileName, option)" + "\n"
	ImportScript += "\t\t" + "SequencerSection.sequencer_section_add_key(frame,value)" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
			
	#Prepare process import

	ImportScript += "if ue.find_asset(seqLocation+'/'+seqName):" + "\n"
	ImportScript += "\t" + 'print("Warning this file already exists")' + "\n"
	ImportScript += "\t" + "factory = LevelSequenceFactoryNew()" + "\n"
	ImportScript += "\t" + "seq = factory.factory_create_new(seqLocation+'/'+seqTempName.replace('.',''))" + "\n"
	ImportScript += "\t" +  "mustBeReplace = True" + "\n"
	ImportScript += "else:" + "\n"
	ImportScript += "\t" + "factory = LevelSequenceFactoryNew()" + "\n"
	ImportScript += "\t" + "seq = factory.factory_create_new(seqLocation+'/'+seqName.replace('.',''))" + "\n"
	ImportScript += "\n"

	ImportScript += 'if seq:' + "\n"
	ImportScript += "\t" + 'print("Sequencer reference created")' + "\n"
	ImportScript += "\t" + 'print(seq)' + "\n"
	ImportScript += "\t" + "ImportedCamera = [] #(CameraName, CameraGuid)" + "\n"
	ImportScript += "\t" + 'print("========================= Import started ! =========================")' + "\n"
	ImportScript += "\t" + "\n"
	
	ImportScript += "\t" + "#Set frame rate" + "\n"
	#Set frame rate for 4.20 and bigger
	ImportScript += "\t" + "if ue.ENGINE_MINOR_VERSION >= 20:" + "\n"
	ImportScript += "\t\t" + "myFFrameRate = FrameRate()" + "\n"
	ImportScript += "\t\t" + "myFFrameRate.Denominator = frameRateDenominator" + "\n"
	ImportScript += "\t\t" + "myFFrameRate.Numerator = frameRateNumerator" + "\n"
	ImportScript += "\t\t" + "seq.MovieScene.DisplayRate = myFFrameRate" + "\n"		
	#Set frame rate for 4.19	
	ImportScript += "\t" + "else:" + "\n"
	ImportScript += "\t\t" + "seq.MovieScene.FixedFrameInterval = frameRateDenominator/frameRateNumerator" + "\n"
	ImportScript += "\t" + "\n"
		
	#Set playback range
	ImportScript += "\t" + "#Set playback range" + "\n"
	ImportScript += "\t" + "seq.sequencer_set_playback_range(startFrame/frameRateNumerator, (endFrame-secureCrop)/frameRateNumerator)" + "\n"
	ImportScript += "\t" + "camera_cut_track = seq.sequencer_add_camera_cut_track()" + "\n"
	ImportScript += "\t" + "world = ue.get_editor_world()" + "\n"
	
	ImportScript += "else:" + "\n"
	ImportScript += "\t" + 'print("Fail to create Sequencer")' + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	#Import camera
	for asset in scene.UnrealExportedAssetsList:	
		if (asset.assetType == "Camera"):
			camera = asset.object
			ImportScript += "#import " + camera.name + "\n"
			ImportScript += "if seq:" + "\n"
			ImportScript += "\t" + 'print("Start import ' + camera.name + '")' + "\n"
			ImportScript += "\t" + "\n"
			
			#Create spawnable camera
			ImportScript += "\t" + "#Create spawnable camera" + "\n"
			ImportScript += "\t" + "cine_camera_actor = world.actor_spawn(CineCameraActor) #Create camera" + "\n"
			ImportScript += "\t" + "cine_camera_actor.set_actor_label('" + camera.name + "')" + "\n"
			ImportScript += "\t" + "cine_camera_actor.CameraComponent.LensSettings.MinFStop = 0" + "\n"
			ImportScript += "\t" + "cine_camera_actor.CameraComponent.LensSettings.MaxFStop = 1000" + "\n"
			ImportScript += "\t" + "camera_spawnable_guid = seq.sequencer_make_new_spawnable(cine_camera_actor) #Add camera in sequencer" + "\n"
			ImportScript += "\t" + "cine_camera_actor.actor_destroy()" + "\n"
			ImportScript += "\t" + "ImportedCamera.append(('"+camera.name+"', camera_spawnable_guid))"
			
			ImportScript += "\n"
			
			#Import fbx transform
			ImportScript += "\t" + "#Import fbx transform" + "\n"
			AdditionalTracksLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalTrack.ini")))
			ImportScript += "\t" + "AdditionalTracksLoc = os.path.join(r'"+AdditionalTracksLoc+"')" + "\n"
			FbxLoc = (os.path.join(asset.exportPath, GetObjExportFileName(camera)))
			ImportScript += "\t" + "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"
			ImportScript += "\t" + "for obj in seq.MovieScene.ObjectBindings:" + "\n"
			ImportScript += "\t\t" + "if obj.ObjectGuid == ue.string_to_guid(camera_spawnable_guid):" + "\n"
			ImportScript += "\t\t\t" + "transform_track = obj.tracks[0]" + "\n"
			ImportScript += "\t\t\t" + "transform_camera_section = transform_track.Sections[0]" + "\n"
			ImportScript += "\t\t\t" + "transform_camera_section.sequencer_import_fbx_transform(FbxLoc, '" + camera.name + "')" + "\n"
			ImportScript += "\n"
			ImportScript += "\t\t\t" + "#Import additional tracks" + "\n"
			ImportScript += "\t\t\t" + "spawned_track = obj.tracks[1]" + "\n"
			ImportScript += "\t\t\t" + "spawned_camera_section = spawned_track.Sections[0]" + "\n"
			ImportScript += "\t\t\t" + "AddSequencerSectionBoolKeysByIniFile(spawned_camera_section, 'Spawned', AdditionalTracksLoc)" + "\n"
			ImportScript += "\n"
			
			#Import additional tracks
			ImportScript += "\t" + "#Import additional tracks" + "\n"
			ImportScript += "\t" + "Component = seq.MovieScene.ObjectBindings[-1] #Get the last" + "\n"
			ImportScript += "\t" + "sectionFocalLength = Component.Tracks[0].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, 'FocalLength', AdditionalTracksLoc)" + "\n"
			ImportScript += "\n"
			ImportScript += "\t" + "sectionFocusDistance = Component.Tracks[1].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, 'FocusDistance', AdditionalTracksLoc)" + "\n"
			ImportScript += "\n"
			ImportScript += "\t" + "sectionAperture = Component.Tracks[2].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionAperture, 'Aperture', AdditionalTracksLoc)" + "\n"
			ImportScript += "\n"
			ImportScript += "\n\n"

	def getMarkerSceneSections():
		scene = bpy.context.scene
		markersOrderly = [] 
		firstMarkersFrame = scene.frame_start
		lastMarkersFrame = scene.frame_end+1
		
		#If the scene don't use marker
		if len(bpy.context.scene.timeline_markers) < 1:
			return ([[scene.frame_start, scene.frame_end+1, bpy.context.scene.camera]])
		
		for marker in scene.timeline_markers:
			#Re set first frame
			if marker.frame < firstMarkersFrame:
				firstMarkersFrame = marker.frame

		for x in range(firstMarkersFrame, lastMarkersFrame):
			for marker in scene.timeline_markers:
				if marker.frame == x:
					markersOrderly.append(marker)
		#---
		sectionCuts = []		
		for x in range(len(markersOrderly)):
			if scene.frame_end+1 > markersOrderly[x].frame:
				startTime = markersOrderly[x].frame
				if x+1 != len(markersOrderly):
					EndTime = markersOrderly[x+1].frame
				else:
					EndTime = scene.frame_end+1
				sectionCuts.append([startTime, EndTime, markersOrderly[x].camera])
			
		return sectionCuts
		
	for section in getMarkerSceneSections():	
				#Camera cut sections
			ImportScript += "#Import camera cut section" + "\n"
			ImportScript += "if seq:" + "\n"
			ImportScript += "\t" + "camera_cut_section = camera_cut_track.sequencer_track_add_section()" + "\n"
			if section[2] is not None:
				if section[2].ExportEnum == "export_recursive" or section[2].ExportEnum == "auto":
					ImportScript += "\t" + "for camera in ImportedCamera:" + "\n"
					ImportScript += "\t\t" + "if camera[0] == '"+section[2].name+"':" + "\n"
					ImportScript += "\t\t\t" + "camera_cut_section.CameraBindingID = MovieSceneObjectBindingID( Guid=ue.string_to_guid( camera[1] ), Space=EMovieSceneObjectBindingSpace.Local )" + "\n"
				else:
					ImportScript += "\t" + "#Not camera found for this section" + "\n"
			else:
				ImportScript += "\t" + "#Not camera found for this section" + "\n"
			ImportScript += "\t" + "camera_cut_section.sequencer_set_section_range("+str(section[0])+"/frameRateNumerator, ("+str(section[1])+"-secureCrop)/frameRateNumerator)" + "\n"
	
	#Replace
	ImportScript += "if mustBeReplace == True:" + "\n"
	ImportScript += "\t" + "OldSeq = seqLocation+'/'+seqName.replace('.','')+'.'+seqName.replace('.','')" + "\n"
	ImportScript += "\t" + "NewSeq = seqLocation+'/'+seqTempName.replace('.','')+'.'+seqTempName.replace('.','')" + "\n"
	ImportScript += "\t" + "print(OldSeq)" + "\n"
	ImportScript += "\t" + "print(NewSeq)" + "\n"
	ImportScript += "\t" + "print(\"LevelSequence'\"+OldSeq+\"'\")" + "\n"
	ImportScript += "\t" + "ue.delete_asset(OldSeq)" + "\n"
	#ImportScript += "\t" + "ue.rename_asset(NewSeq, seqName.replace('.',''))" + "\n"

	#import result
	ImportScript += "if seq:" + "\n"
	ImportScript += "\t" + "print('========================= Imports completed ! =========================')" + "\n"
	ImportScript += "\t" + "\n"
	ImportScript += "\t" + "for cam in ImportedCamera:" + "\n"
	ImportScript += "\t\t" + "print(cam[0])" + "\n"
	ImportScript += "\t" + "\n"
	ImportScript += "\t" + "print('=========================')" + "\n"
	ImportScript += "\t" + "seq.sequencer_changed(True)" + "\n"
	
	return ImportScript

	
def WriteSingleCameraAdditionalTrack(obj):
	
	def getCameraFocusDistance(Camera, Target):
		transA = Camera.matrix_world.copy()
		transB = Target.matrix_world.copy()
		transA.invert()
		distance = (transA * transB).translation.z #Z is the Fosrward
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

		
	def getOneKeysByPath(obj,DataPath, DataValue, Frame, IsData = True):
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
		
	def getAllKeysByPath(obj,DataPath, DataValue, IsData = True):
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

	#Write FocalLength keys
	ImportScript += "[FocalLength]" + "\n"
	for key in getAllKeysByPath(obj,"lens",obj.data.lens): 
		#Fov type return auto to lens
		ImportScript += str(key[0])+": "+str(key[1]) + "\n"
	ImportScript += "\n\n\n"
		
	#Write FocusDistance keys
	ImportScript += "[FocusDistance]" + "\n"
	if obj.data.dof_object is None:
		DataKeys = getAllKeysByPath(obj,"dof_distance",obj.data.dof_distance)
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
	if scene.render.engine == 'CYCLES': #Work only with cycle.
		if obj.data.cycles.aperture_type == 'FSTOP':
			DataKeys = getAllKeysByPath(obj,"cycles.aperture_fstop",obj.data.cycles.aperture_fstop)
		else:
			DataKeys = getAllKeysByPath(obj,"cycles.aperture_size",obj.data.cycles.aperture_size)
		for key in DataKeys:
			CorrectedValue = key[1]
			if obj.data.cycles.aperture_type == 'RADIUS':
				#Convert radius to Fstop
				FocalLength = getOneKeysByPath(obj,"lens",obj.data.lens,key[0])
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
	for key in getAllKeysByPath(obj,"hide",obj.hide, False):
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
			RelativeMatrix = (bml.inverted() * am.inverted() * em)
			l = RelativeMatrix.to_translation()
			r = RelativeMatrix.to_euler()
			s = socket.scale

			#Convet to array for configparser and convert value for Unreal
			array_l = [l[0], l[1]*-1, l[2]]
			array_r = [r[0], degrees(r[1])*-1, degrees(r[2])*-1]
			array_s = [s[0], s[1], s[2]]

			MySocket = [SocketName, b.name, array_l, array_r, array_s]
			config.set('Sockets', 'socket_'+str(i), str(MySocket))
		
		
	return config

def WriteAllTextFiles():

	scene = bpy.context.scene
	if scene.text_exportLog:
		Text = WriteExportLog()
		if Text is not None:
			Filename = scene.file_export_log_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)
			
	#Import script
	if scene.text_ImportAssetScript:
		Text = WriteImportAssetScript()
		if Text is not None:
			Filename = scene.file_import_asset_script_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)
			
	if scene.text_ImportSequenceScript:
		Text = WriteImportSequencerScript()
		if Text is not None:
			Filename = scene.file_import_sequencer_script_name
			ExportSingleText(Text, scene.export_other_file_path, Filename)
			
	#ConfigParser 
	#if scene.text_ImportAssetScript:
		#Text = WriteExportedAssetsDetail()
		#if Text is not None:
			#Filename = "ExportedAssetsDetail.ini" 
			#ExportSingleConfigParser(Text, scene.export_other_file_path, Filename)
			
	#if scene.text_ImportSequenceScript:
		#Text = WriteSequencerDetail()
		#if Text is not None:
			#Filename = "SequencerDetail.ini" 
			#ExportSingleConfigParser(Text, scene.export_other_file_path, Filename)

