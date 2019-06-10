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
from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *

from . import bfu_Utils
importlib.reload(bfu_Utils)
from .bfu_Utils import *


def WriteImportPythonFooter():

	#import result
	ImportScript = ""
	ImportScript += "print('========================= Full import completed !  =========================')" + "\n"
	ImportScript += "\n"
	ImportScript += "StaticMesh_ImportedList = []" + "\n"	
	ImportScript += "SkeletalMesh_ImportedList = []" + "\n"	
	ImportScript += "Alembic_ImportedList = []" + "\n"	
	ImportScript += "Animation_ImportedList = []" + "\n"	
	ImportScript += "for asset in ImportedList:" + "\n"		
	ImportScript += "\t" + "if asset[1] == 'StaticMesh':" + "\n"	
	ImportScript += "\t\t" + "StaticMesh_ImportedList.append(asset[0])" + "\n"	
	ImportScript += "\t" + "elif asset[1] == 'SkeletalMesh':" + "\n"
	ImportScript += "\t\t" + "SkeletalMesh_ImportedList.append(asset[0])" + "\n"	
	ImportScript += "\t" + "elif asset[1] == 'Alembic':" + "\n"
	ImportScript += "\t\t" + "Alembic_ImportedList.append(asset[0])" + "\n"
	ImportScript += "\t" + "else:" + "\n"
	ImportScript += "\t\t" + "Animation_ImportedList.append(asset[0])" + "\n"
	ImportScript += "\n"
	ImportScript += "print('Imported StaticMesh: '+str(len(StaticMesh_ImportedList)))" + "\n"
	ImportScript += "print('Imported SkeletalMesh: '+str(len(SkeletalMesh_ImportedList)))" + "\n"
	ImportScript += "print('Imported Alembic: '+str(len(Alembic_ImportedList)))" + "\n"
	ImportScript += "print('Imported Animation: '+str(len(Animation_ImportedList)))" + "\n"
	ImportScript += "print('Import failled: '+str(len(ImportFailList)))" + "\n"
	ImportScript += "for error in ImportFailList:" + "\n"
	ImportScript += "\t" + "print(error)" + "\n"
	ImportScript += "\n"
	ImportScript += "print('=========================')" + "\n"
	return ImportScript		

def WriteImportAssetScript():
	def GetFBXImportType(assetType):
		if assetType == "StaticMesh":
			return "FBXIT_STATIC_MESH"
		else:
			if GetIsAnimation(assetType):
				return "FBXIT_ANIMATION"
			else:
				return "FBXIT_SKELETAL_MESH"
				
	#Generate a script for import assets in Ue4
	scene = bpy.context.scene

	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += "#It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose" + "\n"
	ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "#Use this command : " + GetImportAssetScriptCommand() + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	#Import
	ImportScript += "import os.path" + "\n"
	ImportScript += "import ConfigParser" + "\n"
	ImportScript += "import ast" + "\n"
	ImportScript += "import unreal" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
		
	#Prepare var and def
	ImportScript += "#Prepare var and def" + "\n"
	ImportScript += "unrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
	ImportScript += "ImportedList = []" + "\n"
	ImportScript += "ImportFailList = []" + "\n"
	ImportScript += "\n"
	
	
	ImportScript += "def GetOptionByIniFile(FileLoc, OptionName, literal = False):" + "\n"
	ImportScript += "\t" + "Config = ConfigParser.ConfigParser()" + "\n"
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
	
	def WriteOneAssetTaskDef(asset):
		ImportScript = ""
		ImportScript += "\n"
		if (asset.object.ExportAsLod == False and 
			(asset.assetType == "StaticMesh" 
			or asset.assetType == "SkeletalMesh"
			or asset.assetType == "Alembic"
			or GetIsAnimation(asset.assetType))
			):		
			
			obj = asset.object
			if GetIsAnimation(asset.assetType):
				AssetRelatifImportPath = os.path.join(obj.exportFolderName, scene.anim_subfolder_name)
			else:
				AssetRelatifImportPath = obj.exportFolderName
			fbxFilePath = (os.path.join(asset.exportPath, asset.assetName))
			AdditionalParameterLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalParameter.ini")))
			
			
			assetUseName = asset.assetName[:-4].replace(' ','_')
			ImportScript += "def CreateTask_"+ assetUseName + "():" + "\n"	
			################[ New import task ]################
			ImportScript += "\t" + "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"
			ImportScript += "\t" + "print('================[ New import task : "+obj.name+" as "+asset.assetType+" type ]================')" + "\n"		
			
			
			##################################[Change]
			
			#Property
			ImportScript += "\t" + "fbxFilePath = os.path.join(r'"+fbxFilePath+"')" + "\n"	
			ImportScript += "\t" + "AssetImportPath = (os.path.join(unrealImportLocation, r'"+AssetRelatifImportPath+r"').replace('\\','/')).rstrip('/')" + "\n"
			if GetIsAnimation(asset.assetType):				
				SkeletonName = scene.skeletal_prefix_export_name+obj.name+"_Skeleton."+scene.skeletal_prefix_export_name+obj.name+"_Skeleton"
				SkeletonLoc = os.path.join(obj.exportFolderName,SkeletonName)
				ImportScript += "\t" + "SkeletonLocation = os.path.join(unrealImportLocation, r'" + SkeletonLoc + r"').replace('\\','/')" + "\n"
				ImportScript += "\t" + "OriginSkeleton = unreal.find_asset(SkeletonLocation)" + "\n"
			ImportScript += "\t" + "AdditionalParameterLoc = os.path.join(r'"+AdditionalParameterLoc+"')" + "\n"	
			
			
			# unreal.FbxImportUI
			ImportScript += "\t" + "taskoptions = unreal.FbxImportUI()" + "\n"
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "if OriginSkeleton:" + "\n"
				ImportScript += "\t\t" + "taskoptions.set_editor_property('Skeleton', OriginSkeleton)" + "\n"
				ImportScript += "\t" + "else:" + "\n"
				ImportScript += "\t\t" + "ImportFailList.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"
				ImportScript += "\t\t" + "return" + "\n"
				
			ImportScript += "\t" + "taskoptions.set_editor_property('original_import_type', unreal.FBXImportType."+GetFBXImportType(asset.assetType)+")" + "\n"
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "taskoptions.set_editor_property('import_materials', False)" + "\n"
			else:
				ImportScript += "\t" + "taskoptions.set_editor_property('import_materials', True)" + "\n"
			ImportScript += "\t" + "taskoptions.set_editor_property('import_textures', False)" + "\n"
			
			if asset.assetType == "SkeletalMesh":
				ImportScript += "\t" + "taskoptions.set_editor_property('import_animations', False)" + "\n"
				ImportScript += "\t" + "taskoptions.set_editor_property('create_physics_asset', " + str(obj.CreatePhysicsAsset) + ")" + "\n"
			
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "taskoptions.set_editor_property('import_animations', True)" + "\n"
				ImportScript += "\t" + "taskoptions.set_editor_property('import_mesh', False)" + "\n"
				ImportScript += "\t" + "taskoptions.set_editor_property('create_physics_asset',False)" + "\n"
			else:
				ImportScript += "\t" + "taskoptions.set_editor_property('import_animations', False)" + "\n"
				ImportScript += "\t" + "taskoptions.set_editor_property('import_mesh', True)" + "\n"
				ImportScript += "\t" + "taskoptions.set_editor_property('create_physics_asset', True)" + "\n"	
			
			
			# unreal.FbxMeshImportData
			if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":
				# unreal.FbxTextureImportData
				if obj.MaterialSearchLocation == "Local": python_MaterialSearchLocation = "LOCAL"
				if obj.MaterialSearchLocation == "UnderParent": python_MaterialSearchLocation = "UNDER_PARENT"
				if obj.MaterialSearchLocation == "UnderRoot": python_MaterialSearchLocation = "UNDER_ROOT"
				if obj.MaterialSearchLocation == "AllAssets": python_MaterialSearchLocation = "ALL_ASSETS"
				ImportScript += "\t" + "taskoptions.texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation." + python_MaterialSearchLocation +")"+ "\n"
				
			if asset.assetType == "StaticMesh":
				# unreal.FbxStaticMeshImportData
				ImportScript += "\t" + "taskoptions.static_mesh_import_data.set_editor_property('combine_meshes', True)" + "\n"
				ImportScript += "\t" + "taskoptions.static_mesh_import_data.set_editor_property('auto_generate_collision', "+ str(obj.AutoGenerateCollision) +")"+ "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" + "taskoptions.static_mesh_import_data.set_editor_property('static_mesh_lod_group', '" + obj.StaticMeshLODGroup +"')"+ "\n"	
				ImportScript += "\t" + "taskoptions.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', " + str(obj.GenerateLightmapUVs) +")"+ "\n"

			
			if asset.assetType == "SkeletalMesh" or GetIsAnimation(asset.assetType):
				# unreal.FbxSkeletalMeshImportData
				ImportScript += "\t" + "taskoptions.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)" + "\n"

			#Task	
			ImportScript += "\t" + "task = unreal.AssetImportTask()" + "\n"
			ImportScript += "\t" + "task.filename = fbxFilePath" + "\n"
			ImportScript += "\t" + "task.destination_path = AssetImportPath" + "\n"
			ImportScript += "\t" + "task.automated = True" + "\n"
			ImportScript += "\t" + "task.save = True" + "\n"
			ImportScript += "\t" + "task.replace_existing = True" + "\n"	
			ImportScript += "\t" + "task.set_editor_property('options', taskoptions)" + "\n"
			
			
			################[ import asset ]################
			ImportScript += "\t" + "print('================[ import asset : "+obj.name+" ]================')" + "\n"	

			ImportScript += "\t" + "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])" + "\n"
			ImportScript += "\t" + "asset = unreal.find_asset(task.imported_object_paths[0])" + "\n"
			ImportScript += "\t" + "if asset == None:" + "\n"
			ImportScript += "\t\t" + "ImportFailList.append('Asset \""+obj.name+"\" not found for after inport')" + "\n"
			ImportScript += "\t\t" + "return" + "\n"
				

			
			################[ Post treatment ]################
			ImportScript += "\t" + "print('========================= Imports of "+obj.name+" completed ! Post treatment started...	=========================')" + "\n"
			if asset.assetType == "StaticMesh":
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" "asset.set_editor_property('lod_group', '" + obj.StaticMeshLODGroup + "')" + "\n"
				if (obj.UseStaticMeshLightMapRes == True):
					ImportScript += "\t" "asset.set_editor_property('light_map_resolution', " + str(obj.StaticMeshLightMapRes) + ")" +"\n"
				if obj.CollisionTraceFlag == "CTF_UseDefault": python_CollisionTraceFlag = "CTF_USE_DEFAULT"
				if obj.CollisionTraceFlag == "CTF_UseSimpleAndComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AND_COMPLEX"
				if obj.CollisionTraceFlag == "CTF_UseSimpleAsComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AS_COMPLEX"
				if obj.CollisionTraceFlag == "CTF_UseComplexAsSimple": python_CollisionTraceFlag = "CTF_USE_COMPLEX_AS_SIMPLE"
				ImportScript += "\t" + "asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag." + python_CollisionTraceFlag + ") " + "\n"
			

			if asset.assetType == "SkeletalMesh":
				################
				################ Vania unreal python dont have unreal.Skeleton.Sockets
				################
				'''
				ImportScript += "\t" + "skeleton = asset.get_editor_property('skeleton')" + "\n"
				#Sockets
				ImportScript += "\t" + "current_sockets = skeleton.Sockets" + "\n"

				ImportScript += "\t" + "new_sockets = []" + "\n"
				ImportScript += "\t" + "sockets_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'Sockets', True)" + "\n"
				ImportScript += "\t" + "for socket in sockets_to_add :" + "\n"

				#Create socket
				ImportScript += "\t\t" + "#Create socket" + "\n"
				ImportScript += "\t\t" + "new_socket = SkeletalMeshSocket('', skeleton)" + "\n"
				ImportScript += "\t\t" + "new_socket.SocketName = socket[0]" + "\n"
				ImportScript += "\t\t" + "print(socket[0])" + "\n"
				ImportScript += "\t\t" + "new_socket.BoneName = socket[1]" + "\n"
				ImportScript += "\t\t" + "l = socket[2]" + "\n"
				ImportScript += "\t\t" + "r = socket[3]" + "\n"
				ImportScript += "\t\t" + "s = socket[4]" + "\n"
				ImportScript += "\t\t" + "new_socket.RelativeLocation = FVector(l[0], l[1], l[2])" + "\n"
				ImportScript += "\t\t" + "new_socket.RelativeRotation = FRotator(r[0], r[1], r[2])" + "\n"
				ImportScript += "\t\t" + "new_socket.RelativeScale = FVector(s[0], s[1], s[2])" + "\n"
				ImportScript += "\t\t" + "new_sockets.append(new_socket)" + "\n"

				#Save socket
				#ImportScript += "\t" + "skeleton.Sockets = current_sockets + new_sockets" + "\n"
				ImportScript += "\t" + "skeleton.Sockets = new_sockets" + "\n"
				ImportScript += "\t" + "\n"		
				
				'''
			#Lod
			if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":  
				ImportScript += "\t" + "lods_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'LevelOfDetail')" + "\n"
				ImportScript += "\t" + "for x, lod in enumerate(lods_to_add):" + "\n"
				ImportScript += "\t\t" + "pass" + "\n"	
				
				################
				################ Vania unreal python dont have unreal.FbxMeshUtils.
				################
				
				'''
				ImportScript += "\t\t" + "asset.static_mesh_import_lod(lod, x+1)" + "\n"
				ImportScript += "\t\t" + "unreal.FbxMeshUtils.ImportStaticMeshLOD(asset, lod, x+1)" + "\n"
				#ImportScript += "\t\t" + "unreal.FbxMeshUtils.ImportSkeletalMeshLOD(asset, lod, x+1)" + "\n"
				'''
			

			##################################[EndChange]
		
			
			ImportScript += "\t" + "print('========================= Post treatment of "+obj.name+" completed !	 =========================')" + "\n"
			ImportScript += "\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
			ImportScript += "CreateTask_"+assetUseName + "()" + "\n"
			ImportScript += "\n"
			ImportScript += "\n"
			ImportScript += "\n"
			
		return ImportScript
				


			
	
	def WriteImportMultiTask(desiredTaskType):	
		
		ImportScript = ""
		ImportScript += "\n"
		ImportScript += "'''" + "\n"
		emptyChar = ""
		hashtagChar = ""
		for u in range(0, len(desiredTaskType)):
			emptyChar+= " "
			hashtagChar+= "#"
		ImportScript += "<###############################"+ hashtagChar +"#####################################>" + "\n"
		ImportScript += "<#############################  "+ emptyChar +"        #############################>" + "\n"
		ImportScript += "<############################   "+ emptyChar +"         ############################>" + "\n"
		ImportScript += "<############################   "+desiredTaskType+" tasks   ############################>" + "\n"
		ImportScript += "<############################   "+ emptyChar +"         ############################>" + "\n"
		ImportScript += "<#############################  "+ emptyChar +"        #############################>" + "\n"
		ImportScript += "<###############################"+ hashtagChar +"#####################################>" + "\n"
		ImportScript += "'''" + "\n"
		ImportScript += "\n"
		
		ImportScript += desiredTaskType+"_TasksList = []" + "\n"
		ImportScript += desiredTaskType+"_PreImportPath = []" + "\n"
		ImportScript += "print('========================= Creating "+desiredTaskType+" tasks... =========================')" + "\n"	
		
		for asset in scene.UnrealExportedAssetsList:
			if desiredTaskType == asset.assetType or (GetIsAnimation(asset.assetType) and desiredTaskType == "Animation" ):
				ImportScript += WriteOneAssetTaskDef(asset)

		ImportScript += "\n"
				

		
		return ImportScript

	def ExsitTypeInExportedAssets(desiredTaskType):
		#Cree un groupe de tache uniquement si il trouve des taches a faire si non return
		for asset in scene.UnrealExportedAssetsList:
			if asset.assetType == desiredTaskType:
				return True
			if GetIsAnimation(asset.assetType) and desiredTaskType == "Animation":
				return True
		return False
	
	if ExsitTypeInExportedAssets("StaticMesh"):
		ImportScript += WriteImportMultiTask("StaticMesh")
	if ExsitTypeInExportedAssets("SkeletalMesh"):
		ImportScript += WriteImportMultiTask("SkeletalMesh")
	if ExsitTypeInExportedAssets("Alembic"):
		ImportScript += WriteImportMultiTask("Alembic")
	if ExsitTypeInExportedAssets("Animation"):
		ImportScript += WriteImportMultiTask("Animation")
		
	ImportScript += WriteImportPythonFooter()

	return ImportScript	


def WriteImportAssetScript_20tab():
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
	ImportScript += "from unreal_engine.enums import EFBXImportType, EMaterialSearchLocation, ECollisionTraceFlag" + "\n"
	ImportScript += "from unreal_engine.structs import StaticMeshSourceModel, MeshBuildSettings" + "\n"
	ImportScript += "from unreal_engine import FVector, FRotator" + "\n"
	ImportScript += "\n"
		
	#Prepare var and def
	ImportScript += "#Prepare var and def" + "\n"
	ImportScript += "UnrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
	ImportScript += "ImportedList = []" + "\n"
	ImportScript += "ImportFailList = []" + "\n"
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
	
	
	def WriteOneAssetTaskDef(asset):	
		ImportScript = ""
		ImportScript += "\n"
		if (asset.object.ExportAsLod == False and 
		(asset.assetType == "StaticMesh" 
		or asset.assetType == "SkeletalMesh"
		or asset.assetType == "Alembic"
		or GetIsAnimation(asset.assetType))
		):		
			
			obj = asset.object
			if GetIsAnimation(asset.assetType):
				AssetRelatifImportPath = os.path.join(obj.exportFolderName, scene.anim_subfolder_name)
			else:
				AssetRelatifImportPath = obj.exportFolderName
			fbxFilePath = (os.path.join(asset.exportPath, asset.assetName))
			AdditionalParameterLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalParameter.ini")))
			
			
			assetUseName = asset.assetName[:-4].replace(' ','_')
			ImportScript += "def CreateTask_"+ assetUseName + "():" + "\n"	
			################[ New import task ]################
			ImportScript += "\t" + "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"
			ImportScript += "\t" + "print('================[ New import task : "+obj.name+" as "+asset.assetType+" type ]================')" + "\n"					
			
			
			##################################[Change]
			
			#StaticMesh and skeletalMesh
			ImportScript += "\t" + "fbx_factory = PyFbxFactory()" + "\n"
			ImportScript += "\t" + "fbx_factory.ImportUI.bImportMaterials = True" + "\n"
			ImportScript += "\t" + "fbx_factory.ImportUI.bImportTextures = False" + "\n"
			ImportScript += "\t" + "fbx_factory.ImportUI.TextureImportData.MaterialSearchLocation = EMaterialSearchLocation." + obj.MaterialSearchLocation + "\n"
			if asset.assetType == "StaticMesh":
				ImportScript += "\t" + "fbx_factory.ImportUI.StaticMeshImportData.bCombineMeshes = True" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.StaticMeshImportData.bAutoGenerateCollision = "+ str(obj.AutoGenerateCollision) + "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" +"fbx_factory.ImportUI.StaticMeshImportData.StaticMeshLODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
					ImportScript += "\t" + "fbx_factory.ImportUI.StaticMeshImportData.bGenerateLightmapUVs = " + str(obj.GenerateLightmapUVs) + "\n"
	
			if asset.assetType == "SkeletalMesh":
				ImportScript += "\t" + "fbx_factory.ImportUI.bImportAnimations = False" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
				ImportScript += "\t" + "fbx_factory.ImportUI.bCreatePhysicsAsset = " + str(obj.CreatePhysicsAsset) + "\n"

			ImportScript += "\t" + "fbxFilePath = os.path.join(r'"+fbxFilePath+"')" + "\n"			
			ImportScript += "\t" + "AdditionalParameterLoc = os.path.join(r'"+AdditionalParameterLoc+"')" + "\n"	
			ImportScript += "\t" + "AssetImportLocation = (os.path.join(UnrealImportLocation, r'"+AssetRelatifImportPath+r"').replace('\\','/')).rstrip('/')" + "\n"




			#Animation				
			if GetIsAnimation(asset.assetType):
				SkeletonName = scene.skeletal_prefix_export_name+obj.name+"_Skeleton."+scene.skeletal_prefix_export_name+obj.name+"_Skeleton"
				SkeletonLoc = os.path.join(obj.exportFolderName,SkeletonName)
				ImportScript += "\t" + "SkeletonLocation = os.path.join(UnrealImportLocation, r'" + SkeletonLoc + r"').replace('\\','/')" + "\n"
				ImportScript += "\t" + "OriginSkeleton = ue.find_asset(SkeletonLocation)" + "\n"
				ImportScript += "\t" + "if OriginSkeleton:" + "\n"
				ImportScript += "\t\t" + "fbx_factory = PyFbxFactory()" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.bImportMesh = False" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.bCreatePhysicsAsset = False" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.Skeleton = OriginSkeleton" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.bImportAnimations = True" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.MeshTypeToImport = EFBXImportType.FBXIT_Animation" + "\n"
				ImportScript += "\t\t" + "fbx_factory.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
				ImportScript += "\t\t" + "fbxFilePath = os.path.join(r'"+fbxFilePath+"')" + "\n"			
				ImportScript += "\t\t" + r"AssetImportLocation = (os.path.join(UnrealImportLocation, r'"+AssetRelatifImportPath+r"').replace('\\','/')).rstrip('/')" + "\n"
				#-----------Import
				#ImportScript += "\t\t" + "try:" + "\n"

				#Import report
				ImportScript += "\t\t" + "asset = fbx_factory.factory_import_object(fbxFilePath, AssetImportLocation)" + "\n"
				ImportScript += "\t\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
				#ImportScript += "\t\t" + "except:" + "\n"
				#ImportScript += "\t\t\t" + "ImportFailList.append('Import error for asset named \""+obj.name+"\" ')" + "\n"
				ImportScript += "\t" + "else:" + "\n"
				ImportScript += "\t\t" + "ImportFailList.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"

			#Static and skeletal	
			else:
				#-----------Import
				#ImportScript += "try:" + "\n"
				ImportScript += "\t" + "asset = fbx_factory.factory_import_object(fbxFilePath, AssetImportLocation)" + "\n"
				if asset.assetType == "StaticMesh":
					if (obj.UseStaticMeshLODGroup == True):
						ImportScript += "\t" "asset.LODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
					if (obj.UseStaticMeshLightMapRes == True):
						ImportScript += "\t" "asset.LightMapResolution = " + str(obj.StaticMeshLightMapRes) + "\n"
					ImportScript += "\t" + "asset.BodySetup.CollisionTraceFlag = ECollisionTraceFlag." + obj.CollisionTraceFlag + " " + "\n"
					
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
				if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh": 
					ImportScript += "\t" + "lods_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'LevelOfDetail')" + "\n"
					ImportScript += "\t" + "for x, lod in enumerate(lods_to_add):" + "\n"
					ImportScript += "\t\t" + "asset.static_mesh_import_lod(lod, x+1)" + "\n"
					#ImportScript += "\t\t" + "#asset.skeletal_mesh_import_lod(lod, x+1)" + "\n" #Need 20 tab implementation
					
				
				#Import report

				#ImportScript += "except:" + "\n"
				#ImportScript += "\t" + "ImportFailList.append('Import error for asset named \""+obj.name+"\" ')" + "\n"


			##################################[EndChange]

			ImportScript += "\t" + "print('========================= Post treatment of "+obj.name+" completed !	 =========================')" + "\n"
			ImportScript += "\t" + "asset.save_package()" + "\n"
			ImportScript += "\t" + "asset.post_edit_change()" + "\n"		
			ImportScript += "\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
			ImportScript += "CreateTask_"+assetUseName + "()" + "\n"
			ImportScript += "\n"
			ImportScript += "\n"
			ImportScript += "\n"
		return ImportScript
			
	for asset in scene.UnrealExportedAssetsList:
		ImportScript += WriteOneAssetTaskDef(asset)
	
	ImportScript += WriteImportPythonFooter()
	
	return ImportScript