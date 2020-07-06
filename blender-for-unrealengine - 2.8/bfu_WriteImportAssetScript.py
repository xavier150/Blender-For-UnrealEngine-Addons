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

from . import bfu_WriteText
importlib.reload(bfu_WriteText)
from .bfu_WriteText import *

def GetFBXImportType(assetType, use20tab = False):
	if use20tab == True:
		if assetType == "StaticMesh":
			return "FBXIT_StaticMesh"
		else:
			if GetIsAnimation(assetType):
				return "FBXIT_Animation"
			else:
				return "FBXIT_SkeletalMesh"
	else:
		if assetType == "StaticMesh":
			return "FBXIT_STATIC_MESH"
		else:
			if GetIsAnimation(assetType):
				return "FBXIT_ANIMATION"
			else:
				return "FBXIT_SKELETAL_MESH"


def WriteImportPythonHeader(use20tab = False):
	GetImportSequencerScriptCommand()
	scene = bpy.context.scene

	#Import
	ImportScript = "import os.path" + "\n"
	if use20tab == True:
		ImportScript += "import configparser" + "\n"
	else:
		ImportScript += "import ConfigParser" + "\n"
	
	ImportScript += "import ast" + "\n"
	if use20tab == True:
		ImportScript += "import unreal_engine as ue" + "\n"
		ImportScript += "from unreal_engine.classes import PyFbxFactory, AlembicImportFactory, StaticMesh, Skeleton, SkeletalMeshSocket" + "\n"
		ImportScript += "from unreal_engine.enums import EFBXImportType, EMaterialSearchLocation, ECollisionTraceFlag" + "\n"
		ImportScript += "from unreal_engine.structs import StaticMeshSourceModel, MeshBuildSettings" + "\n"
		ImportScript += "from unreal_engine import FVector, FRotator" + "\n"
	else:
		ImportScript += "import unreal" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	#Prepare var and def
	ImportScript += "#Prepare var and def" + "\n"
	ImportScript += "unrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
	ImportScript += "ImportedList = []" + "\n"
	ImportScript += "ImportFailList = []" + "\n"
	ImportScript += "\n"

	return ImportScript

def WriteImportPythonDef(use20tab = False):

	ImportScript = ""
	ImportScript += "def GetOptionByIniFile(FileLoc, OptionName, literal = False):" + "\n"
	if use20tab == True:
		ImportScript += "\t" + "Config = configparser.ConfigParser()" + "\n"
	else:
		ImportScript += "\t" + "Config = ConfigParser.ConfigParser()" + "\n"

	ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t" + "Options = []" + "\n"
	ImportScript += "\t" + 'if Config.has_section(OptionName):' + "\n"
	ImportScript += "\t\t" + 'for option in Config.options(OptionName):' + "\n"
	ImportScript += "\t\t\t" + 'if (literal == True):' + "\n"
	ImportScript += "\t\t\t\t" + 'Options.append(ast.literal_eval(Config.get(OptionName, option)))' + "\n"
	ImportScript += "\t\t\t" + 'else:' + "\n"
	ImportScript += "\t\t\t\t" + 'Options.append(Config.get(OptionName, option))' + "\n"	
	ImportScript += "\t" + 'else:' + "\n"
	ImportScript += "\t\t" + 'print("/!\ Option: "+OptionName+" not found in file: "+FileLoc)' + "\n"
	ImportScript += "\t" + "return Options" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	return ImportScript

def WriteImportPythonFooter(use20tab = False):

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
	
	ImportScript += "#Select asset(s) in content browser" + "\n"
	ImportScript += "PathList = []" + "\n"
	ImportScript += "for asset in (StaticMesh_ImportedList + SkeletalMesh_ImportedList + Alembic_ImportedList + Animation_ImportedList):" + "\n"
	ImportScript += "\t" + "PathList.append(asset.get_path_name())" + "\n"
	if use20tab == True:
		pass #sync_browser_to_objects
	else:
		ImportScript += "unreal.EditorAssetLibrary.sync_browser_to_objects(PathList)" + "\n"
	ImportScript += "\n"
	
	ImportScript += "print('=========================')" + "\n"
	return ImportScript


def WriteOneAssetTaskDef(asset, use20tab = False):
	scene = bpy.context.scene
	ImportScript = ""
	ImportScript += "\n"
	if (asset.object.ExportAsLod == False and
		(asset.assetType == "StaticMesh"
		or asset.assetType == "SkeletalMesh"
		or asset.assetType == "Alembic"
		or GetIsAnimation(asset.assetType))
		):
		pass
	else:
		return ImportScript

	if asset.assetType == "Alembic":
		FileType = "ABC"
	else:
		FileType = "FBX"

	obj = asset.object
	if GetIsAnimation(asset.assetType):
		AssetRelatifImportPath = os.path.join(obj.exportFolderName, scene.anim_subfolder_name)
	else:
		AssetRelatifImportPath = obj.exportFolderName
	FilePath = (os.path.join(asset.exportPath, asset.assetName))
	AdditionalParameterLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalParameter.ini")))


	assetUseName = asset.assetName[:-4].replace(' ','_').replace('-','_')
	ImportScript += "def CreateTask_"+ assetUseName + "():" + "\n"
	################[ New import task ]################
	ImportScript += "\t" + "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"
	ImportScript += "\t" + "print('================[ New import task : "+obj.name+" as "+asset.assetType+" type ]================')" + "\n"


	##################################[Change]

	#Property
	ImportScript += "\t" + "FilePath = os.path.join(r'"+FilePath+"')" + "\n"
	ImportScript += "\t" + "AdditionalParameterLoc = os.path.join(r'"+AdditionalParameterLoc+"')" + "\n"
	ImportScript += "\t" + "AssetImportPath = (os.path.join(unrealImportLocation, r'"+AssetRelatifImportPath+r"').replace('\\','/')).rstrip('/')" + "\n"

	if GetIsAnimation(asset.assetType):
		SkeletonName = scene.skeletal_prefix_export_name+obj.name+"_Skeleton."+scene.skeletal_prefix_export_name+obj.name+"_Skeleton"
		SkeletonLoc = os.path.join(obj.exportFolderName,SkeletonName)
		ImportScript += "\t" + "SkeletonLocation = os.path.join(unrealImportLocation, r'" + SkeletonLoc + r"').replace('\\','/')" + "\n"
		if use20tab == True:
			ImportScript += "\t" + "OriginSkeleton = ue.find_asset(SkeletonLocation)" + "\n"
		else:
			ImportScript += "\t" + "OriginSkeleton = unreal.find_asset(SkeletonLocation)" + "\n"


	#ImportTask
	if use20tab == True:
		if FileType == "FBX":
			ImportScript += "\t" + "task = PyFbxFactory()" + "\n"
		if FileType == "ABC":
			ImportScript += "\t" + "task = AlembicImportFactory()" + "\n"
	else:
		ImportScript += "\t" + "task = unreal.AssetImportTask()" + "\n"
		ImportScript += "\t" + "task.filename = FilePath" + "\n"
		ImportScript += "\t" + "task.destination_path = AssetImportPath" + "\n"
		ImportScript += "\t" + "task.automated = True" + "\n"
		ImportScript += "\t" + "task.save = True" + "\n"
		ImportScript += "\t" + "task.replace_existing = True" + "\n"
		if FileType == "FBX":
			ImportScript += "\t" + "task.set_editor_property('options', unreal.FbxImportUI())" + "\n"
		if FileType == "ABC":
			ImportScript += "\t" + "task.set_editor_property('options', unreal.AbcImportSettings())" + "\n"


	# unreal.FbxImportUI
	if FileType == "FBX":
		if GetIsAnimation(asset.assetType):
			ImportScript += "\t" + "if OriginSkeleton:" + "\n"
			if use20tab == True:
				ImportScript += "\t\t" + "task.ImportUI.Skeleton = OriginSkeleton" + "\n"
			else:
				ImportScript += "\t\t" + "task.get_editor_property('options').set_editor_property('Skeleton', OriginSkeleton)" + "\n"
			ImportScript += "\t" + "else:" + "\n"

			ImportScript += "\t\t" + "ImportFailList.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"
			ImportScript += "\t\t" + "return" + "\n"

		if use20tab == True:
			ImportScript += "\t" + "task.ImportUI.MeshTypeToImport = EFBXImportType."+GetFBXImportType(asset.assetType, True) + "\n"
		else:
			ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType."+GetFBXImportType(asset.assetType)+")" + "\n"

		if use20tab == True: #import_materials
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "task.ImportUI.bImportMaterials = False" + "\n"
			else:
				ImportScript += "\t" + "task.ImportUI.bImportMaterials = True" + "\n"
			ImportScript += "\t" + "task.ImportUI.bImportTextures = False" + "\n"
		else:
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_materials', False)" + "\n"
			else:
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_materials', True)" + "\n"
			ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_textures', False)" + "\n"

		if asset.assetType == "SkeletalMesh":
			if use20tab == True:
				ImportScript += "\t" + "task.ImportUI.bImportAnimations = False" + "\n"
				ImportScript += "\t" + "task.ImportUI.bCreatePhysicsAsset = " + str(obj.CreatePhysicsAsset) + "\n"
			else:
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_animations', False)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('create_physics_asset', " + str(obj.CreatePhysicsAsset) + ")" + "\n"

		if use20tab == True:
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "task.ImportUI.bImportAnimations = True" + "\n"
				ImportScript += "\t" + "task.ImportUI.bImportMesh = False" + "\n"
				ImportScript += "\t" + "task.ImportUI.bCreatePhysicsAsset = False" + "\n"
			else:
				ImportScript += "\t" + "task.ImportUI.bImportAnimations = False" + "\n"
				ImportScript += "\t" + "task.ImportUI.bImportMesh = True" + "\n"
				ImportScript += "\t" + "task.ImportUI.bCreatePhysicsAsset = True" + "\n"
		else:
			if GetIsAnimation(asset.assetType):
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_animations', True)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_mesh', False)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('create_physics_asset',False)" + "\n"
			else:
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_animations', False)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_mesh', True)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('create_physics_asset', True)" + "\n"

		# unreal.FbxMeshImportData
		if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":
			# unreal.FbxTextureImportData
			if use20tab == True:
				ImportScript += "\t" + "task.ImportUI.TextureImportData.MaterialSearchLocation = EMaterialSearchLocation." + obj.MaterialSearchLocation + "\n"
			else:
				if obj.MaterialSearchLocation == "Local": python_MaterialSearchLocation = "LOCAL"
				if obj.MaterialSearchLocation == "UnderParent": python_MaterialSearchLocation = "UNDER_PARENT"
				if obj.MaterialSearchLocation == "UnderRoot": python_MaterialSearchLocation = "UNDER_ROOT"
				if obj.MaterialSearchLocation == "AllAssets": python_MaterialSearchLocation = "ALL_ASSETS"
				ImportScript += "\t" + "task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation." + python_MaterialSearchLocation +")"+ "\n"

		if asset.assetType == "StaticMesh":
			# unreal.FbxStaticMeshImportData
			if use20tab == True:
				ImportScript += "\t" + "task.ImportUI.StaticMeshImportData.bCombineMeshes = True" + "\n"
				ImportScript += "\t" + "task.ImportUI.StaticMeshImportData.bAutoGenerateCollision = "+ str(obj.AutoGenerateCollision) + "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" +"task.ImportUI.StaticMeshImportData.StaticMeshLODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
				else:
					ImportScript += "\t" +"task.ImportUI.StaticMeshImportData.StaticMeshLODGroup = 'None'" + "\n"
				ImportScript += "\t" + "task.ImportUI.StaticMeshImportData.bGenerateLightmapUVs = " + str(obj.GenerateLightmapUVs) + "\n"
			else:
				ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('combine_meshes', True)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('auto_generate_collision', "+ str(obj.AutoGenerateCollision) +")"+ "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', '" + obj.StaticMeshLODGroup +"')"+ "\n"
				else:
					ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', 'None')"+ "\n"
				ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', " + str(obj.GenerateLightmapUVs) +")"+ "\n"


		if asset.assetType == "SkeletalMesh" or GetIsAnimation(asset.assetType):
			# unreal.FbxSkeletalMeshImportData
			if use20tab == True:
				ImportScript += "\t" + "task.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
			else:
				ImportScript += "\t" + "task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)" + "\n"
				ImportScript += "\t" + "task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('convert_scene', True)" + "\n"
	if FileType == "ABC":
		if use20tab:
			ImportScript += "\t" + "task.ImportSettings.ImportType = 2" + "\n"
			ImportScript += "\t" + "task.ImportSettings.CompressionSettings.bMergeMeshes = True" + "\n"
			ImportScript += "\t" + "task.ImportSettings.ConversionSettings.bFlipU = False" + "\n"
			ImportScript += "\t" + "task.ImportSettings.ConversionSettings.bFlipV = True" + "\n"
			ImportScript += "\t" + "task.ImportSettings.ConversionSettings.Rotation = FVector(90,0,0)" + "\n"
			ImportScript += "\t" + "task.ImportSettings.ConversionSettings.Scale = FVector(100,-100,100)" + "\n"
		else:
			ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_type', unreal.AlembicImportType.SKELETAL)" + "\n"



	################[ import asset ]################
	ImportScript += "\t" + "print('================[ import asset : "+obj.name+" ]================')" + "\n"
	if use20tab == True:
		ImportScript += "\t" + "try:" + "\n"
		ImportScript += "\t\t" + "asset = task.factory_import_object(FilePath, AssetImportPath)" + "\n"
		ImportScript += "\t" + "except:" + "\n"
		ImportScript += "\t\t" + "asset = None" + "\n"
	else:
		ImportScript += "\t" + "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])" + "\n"
		ImportScript += "\t" + "if len(task.imported_object_paths) > 0:" + "\n"
		ImportScript += "\t\t" + "asset = unreal.find_asset(task.imported_object_paths[0])" + "\n"
		ImportScript += "\t" + "else:" + "\n"
		ImportScript += "\t\t" + "asset = None" + "\n"
	ImportScript += "\t" + "if asset == None:" + "\n"
	ImportScript += "\t\t" + "ImportFailList.append('Asset \""+obj.name+"\" not found for after inport')" + "\n"
	ImportScript += "\t\t" + "return" + "\n"
	if asset.assetType == "Action" or asset.assetType == "Pose" or asset.assetType == "NlAnim":
		if use20tab == True:
			pass
		else:
			ImportScript += "\t" + "p = task.imported_object_paths[0]" + "\n"
			ImportScript += "\t" + "animAsset = unreal.find_asset(p.split('.')[0]+'_anim.'+p.split('.')[1]+'_anim')" + "\n"
			ImportScript += "\t" + "unreal.EditorAssetLibrary.delete_asset(task.imported_object_paths[0])" + "\n"
			ImportScript += "\t" + "if animAsset == None:" + "\n"
			ImportScript += "\t\t" + "ImportFailList.append('animAsset \""+obj.name+"\" not found for after inport')" + "\n"
			ImportScript += "\t\t" + "return" + "\n"


	################[ Post treatment ]################
	ImportScript += "\t" + "print('========================= Imports of "+obj.name+" completed ! Post treatment started...	=========================')" + "\n"

	
	if asset.assetType == "StaticMesh":
		if use20tab == True:
			if (obj.UseStaticMeshLODGroup == True):
				ImportScript += "\t" "asset.LODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
			else:
				ImportScript += "\t" "asset.LODGroup = 'None'" + "\n"
			if (obj.UseStaticMeshLightMapRes == True):
				ImportScript += "\t" "asset.LightMapResolution = " + str(obj.StaticMeshLightMapRes) + "\n"
			ImportScript += "\t" + "asset.BodySetup.CollisionTraceFlag = ECollisionTraceFlag." + obj.CollisionTraceFlag + " " + "\n"
		else:
			if (obj.UseStaticMeshLODGroup == True):
				ImportScript += "\t" "asset.set_editor_property('lod_group', '" + obj.StaticMeshLODGroup + "')" + "\n"
			else:
				ImportScript += "\t" "asset.set_editor_property('lod_group', 'None')" + "\n"
			if (obj.UseStaticMeshLightMapRes == True):
				ImportScript += "\t" "asset.set_editor_property('light_map_resolution', " + str(obj.StaticMeshLightMapRes) + ")" +"\n"
			if obj.CollisionTraceFlag == "CTF_UseDefault": python_CollisionTraceFlag = "CTF_USE_DEFAULT"
			if obj.CollisionTraceFlag == "CTF_UseSimpleAndComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AND_COMPLEX"
			if obj.CollisionTraceFlag == "CTF_UseSimpleAsComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AS_COMPLEX"
			if obj.CollisionTraceFlag == "CTF_UseComplexAsSimple": python_CollisionTraceFlag = "CTF_USE_COMPLEX_AS_SIMPLE"
			ImportScript += "\t" + "asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag." + python_CollisionTraceFlag + ") " + "\n"

			if obj.VertexColorImportOption == "VCIO_Ignore" : python_VertexColorImportOption = "IGNORE"
			if obj.VertexColorImportOption == "VCIO_Replace" : python_VertexColorImportOption = "REPLACE"
			ImportScript += "\t" + "asset.get_editor_property('asset_import_data').set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption." + python_VertexColorImportOption + ") " + "\n"

	#Socket
	if asset.assetType == "SkeletalMesh":
		
		ImportScript += "\n\t" + "#Import the SkeletalMesh socket(s)" + "\n" #Import the SkeletalMesh  Socket(s)
		ImportScript += "\t" + "sockets_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'Sockets', True)" + "\n"
		if use20tab == True:
			ImportScript += "\t" + "skeleton = asset.skeleton" + "\n"
			#Sockets
			ImportScript += "\t" + "current_sockets = skeleton.Sockets" + "\n"
			ImportScript += "\t" + "new_sockets = []" + "\n"
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
			ImportScript += "\t" + "skeleton.Sockets = new_sockets" + "\n"
			ImportScript += "\t" + "\n"
		else:
			ImportScript += "\t" + "skeleton = asset.get_editor_property('skeleton')" + "\n"
			ImportScript += "\t" + "for socket in sockets_to_add:" + "\n"
			
			#Create socket
			ImportScript += "\t\t" + "pass" + "\n"
			#ImportScript += "\t\t" + "#Create socket" + "\n"
			#ImportScript += "\t\t" + "new_socket = unreal.SkeletalMeshSocket('', skeleton)" + "\n"
			#ImportScript += "\t\t" + "new_socket.SocketName = socket[0]" + "\n"

	#Lod
	if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":	
		if asset.assetType == "StaticMesh":
			ImportScript += "\n\t" + "#Import the StaticMesh lod(s)" + "\n" #Import the StaticMesh lod(s)
			if use20tab == True:
				pass
			else:
				ImportScript += "\t" + "unreal.EditorStaticMeshLibrary.remove_lods(asset)" + "\n"
		
		if asset.assetType == "SkeletalMesh":
			ImportScript += "\n\t" + "#Import the SkeletalMesh lod(s)" + "\n" #Import the SkeletalMesh  lod(s)
			if use20tab == True:
				pass
			else:
				pass
		
		ImportScript += "\t" + "lods_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'LevelOfDetail')" + "\n"
		ImportScript += "\t" + "for x, lod in enumerate(lods_to_add):" + "\n"
		
		
		if asset.assetType == "StaticMesh":
			
			if use20tab == True:
				ImportScript += "\t\t" + "asset.static_mesh_import_lod(lod, x+1)" + "\n"
			else:
				ImportScript += "\t\t" + "lodTask = unreal.AssetImportTask()" + "\n"
				ImportScript += "\t\t" + "lodTask.filename = lod" + "\n"
				ImportScript += "\t\t" + "lodTask.destination_path = AssetImportPath" + "\n"
				ImportScript += "\t\t" + "lodTask.automated = True" + "\n"
				ImportScript += "\t\t" + "lodTask.replace_existing = True" + "\n"
				ImportScript += "\t\t" + "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])" + "\n"
				ImportScript += "\t\t" + "lodAsset = unreal.find_asset(lodTask.imported_object_paths[0])" + "\n"
				ImportScript += "\t\t" + "slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, x+1, lodAsset, 0, True)" + "\n"
				ImportScript += "\t\t" + "unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])" + "\n"
		elif asset.assetType == "SkeletalMesh":
			if use20tab == True:
				ImportScript += "\t\t" + "pass" + "\n"
				#ImportScript += "\t\t" + "asset.skeletal_mesh_import_lod(lod, x+1)" + "\n" #Need 20 tab implementation
			else:
				ImportScript += "\t\t" + "pass" + "\n"
				#ImportScript += "\t\t" + "unreal.FbxMeshUtils.ImportSkeletalMeshLOD(asset, lod, x+1)" + "\n" #Vania unreal python dont have unreal.FbxMeshUtils.
		else:
			ImportScript += "\t\t" + "pass" + "\n"


	##################################[EndChange]


	ImportScript += "\t" + "print('========================= Post treatment of "+obj.name+" completed !	 =========================')" + "\n"
	if use20tab == True:
		ImportScript += "\t" + "asset.save_package()" + "\n"
		ImportScript += "\t" + "asset.post_edit_change()" + "\n"
	else:
		if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":	
			ImportScript += "\t" + "unreal.EditorAssetLibrary.save_loaded_asset(asset)" + "\n"
	
	if use20tab == True:
		ImportScript += "\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
	else:
		if asset.assetType == "Action" or asset.assetType == "Pose" or asset.assetType == "NlAnim":
			ImportScript += "\t" + "ImportedList.append([animAsset, '" + asset.assetType + "'])" + "\n"
		else:
			ImportScript += "\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
	ImportScript += "CreateTask_"+assetUseName + "()" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	return ImportScript

def WriteImportAssetScript(use20tab = False):
	#Generate a script for import assets in Ue4
	scene = bpy.context.scene

	ImportScript = WriteImportPythonHeader(use20tab)
	ImportScript += WriteImportPythonDef(use20tab)

	#Process import
	ImportScript += "#Process import" + "\n"
	ImportScript += "print('========================= Import started ! =========================')" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	ImportScript += "\n"


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
		ImportScript += "<#############################	 "+ emptyChar +"		#############################>" + "\n"
		ImportScript += "<############################	 "+ emptyChar +"		 ############################>" + "\n"
		ImportScript += "<############################	 "+desiredTaskType+" tasks	 ############################>" + "\n"
		ImportScript += "<############################	 "+ emptyChar +"		 ############################>" + "\n"
		ImportScript += "<#############################	 "+ emptyChar +"		#############################>" + "\n"
		ImportScript += "<###############################"+ hashtagChar +"#####################################>" + "\n"
		ImportScript += "'''" + "\n"
		ImportScript += "\n"

		ImportScript += desiredTaskType+"_TasksList = []" + "\n"
		ImportScript += desiredTaskType+"_PreImportPath = []" + "\n"
		ImportScript += "print('========================= Creating "+desiredTaskType+" tasks... =========================')" + "\n"

		for asset in scene.UnrealExportedAssetsList:
			if desiredTaskType == asset.assetType or (GetIsAnimation(asset.assetType) and desiredTaskType == "Animation" ):
				ImportScript += WriteOneAssetTaskDef(asset, use20tab)


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

	#Deffini la priorité d'import des objects
	if ExsitTypeInExportedAssets("Alembic"):
		ImportScript += WriteImportMultiTask("Alembic")
	if ExsitTypeInExportedAssets("StaticMesh"):
		ImportScript += WriteImportMultiTask("StaticMesh")
	if ExsitTypeInExportedAssets("SkeletalMesh"):
		ImportScript += WriteImportMultiTask("SkeletalMesh")
	if ExsitTypeInExportedAssets("Animation"):
		ImportScript += WriteImportMultiTask("Animation")

	ImportScript += WriteImportPythonFooter(use20tab)

	ImportScript += "if len(ImportFailList) == 0:" + "\n"
	ImportScript += "\t" + "return 'Assets imported with success !' " + "\n"
	ImportScript += "else:" + "\n"
	ImportScript += "\t" + "return 'Some asset(s) could not be imported.' " + "\n"

	#-------------------------------------
	
	CheckScript = ""
	if use20tab == True:
		CheckScript += "pass" + "\n"
	else:
		CheckScript += "import unreal" + "\n"
		
		CheckScript += "if hasattr(unreal, 'EditorAssetLibrary') == False:" + "\n"
		CheckScript += "\t" + "print('--------------------------------------------------\\n /!\ Warning: Editor Scripting Utilities should be activated.\\n Plugin > Scripting > Editor Scripting Utilities.')" + "\n"
		CheckScript += "\t" + "return False" + "\n"
		
		CheckScript += "return True" + "\n"
	
	#-------------------------------------

	OutImportScript = ""
	OutImportScript += WriteImportPythonHeadComment(use20tab, False)
	
	OutImportScript += "def CheckTasks():" + "\n"
	OutImportScript += bfu_Utils.AddFrontEachLine(CheckScript, "\t")
	
	OutImportScript += "def ImportAllAssets():" + "\n"
	OutImportScript += bfu_Utils.AddFrontEachLine(ImportScript, "\t")
	
	OutImportScript += "if CheckTasks() == True:" + "\n"
	OutImportScript += "\t" + "print(ImportAllAssets())" + "\n"
	

	return OutImportScript