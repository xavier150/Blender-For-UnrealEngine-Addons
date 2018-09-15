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
from .bfu_basics import *
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

	
def WriteExportLog():
	#Write Export log with exported assets in scene.UnrealExportedAssetsList
	
	def GetNumberByType(targetType):
		foundNumber = 0
		scene = bpy.context.scene
		for assets in scene.UnrealExportedAssetsList:
			if assets.assetType == targetType:
				foundNumber = foundNumber + 1
		return foundNumber
	
	scene = bpy.context.scene
	StaticNum = GetNumberByType("StaticMesh")
	SkeletalNum = GetNumberByType("SkeletalMesh")
	AnimNum = GetNumberByType("Animation")
	PoseNum = GetNumberByType("Pose")
	CameraNum = GetNumberByType("Camera")
	OtherNum = len(scene.UnrealExportedAssetsList)-(StaticNum+SkeletalNum+AnimNum+PoseNum+CameraNum)	
	AssetNumberByType = str(StaticNum)+" StaticMesh(s) | "
	AssetNumberByType += str(SkeletalNum)+" SkeletalMesh(s) | "
	AssetNumberByType += str(AnimNum)+" Animation(s) | "
	AssetNumberByType += str(PoseNum)+" Pose(s) | "
	AssetNumberByType += str(CameraNum)+" Camera(s)"
	AssetNumberByType += str(OtherNum)+" Other(s)" + "\n"
	
	ExportLog = "..." + "\n"
	ExportLog += AssetNumberByType
	ExportLog += "\n"
	for asset in scene.UnrealExportedAssetsList:
		ExportLog +=("["+asset.assetType+"] -> "+"\""+asset.assetName+"\" exported in "+str(asset.exportTime)+" sec.\n")
		ExportLog +=(asset.exportPath + "\n")
		ExportLog += "\n"
	
	return ExportLog

				
def WriteImportAssetScript():
	#Generate a script for import assets in Ue4
	scene = bpy.context.scene

	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += "#It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose" + "\n"
	ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "\n"
	ImportScript += "import os.path" + "\n"
	ImportScript += "import unreal_engine as ue" + "\n"
	ImportScript += "from unreal_engine.classes import PyFbxFactory" + "\n"
	ImportScript += "from unreal_engine.enums import EFBXImportType, EMaterialSearchLocation" + "\n"
	ImportScript += "\n"
		
	#Prepare var and process import
	ImportScript += "#Prepare var and process import" + "\n"
	ImportScript += "UnrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
	ImportScript += "ImportedAsset = []" + "\n"
	ImportScript += "\n"
	ImportScript += "print('========================= Import started ! =========================')" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	ImportScript += "\n"
	
	#Import asset
	for asset in scene.UnrealExportedAssetsList:		
		if (asset.assetType == "StaticMesh" 
		or asset.assetType == "SkeletalMesh"
		or asset.assetType == "Animation"
		or asset.assetType == "Pose"):		
			
			obj = asset.object
			MeshRelatifImportLoc = obj.exportFolderName
			AnimRelatifImportLoc = os.path.join( obj.exportFolderName, scene.anim_subfolder_name )
			FbxLoc = (os.path.join(asset.exportPath, asset.assetName))
			ImportScript += "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"			
			
			if asset.assetType == "StaticMesh":
				ImportScript += "fbx_factory = PyFbxFactory()" + "\n"
				ImportScript += "fbx_factory.ImportUI.bImportMaterials = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.bImportTextures = False" + "\n"
				ImportScript += "fbx_factory.ImportUI.TextureImportData.MaterialSearchLocation = EMaterialSearchLocation." + obj.MaterialSearchLocation + "\n"
				ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bCombineMeshes = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bAutoGenerateCollision = False" + "\n"

				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.StaticMeshLODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
				ImportScript += "fbx_factory.ImportUI.StaticMeshImportData.bGenerateLightmapUVs = " + str(obj.GenerateLightmapUVs) + "\n"
					
				ImportScript += "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"			
				ImportScript += r"AssetImportLocation = os.path.join(UnrealImportLocation, r'"+MeshRelatifImportLoc+r"').replace('\\','/')" + "\n"
				ImportScript += "AssetImportLocation = AssetImportLocation.rstrip('/')" + "\n"
				#-----------Import
				ImportScript += "try:" + "\n"
				ImportScript += "\t" + "asset = fbx_factory.factory_import_object(FbxLoc, AssetImportLocation)" + "\n"
				ImportScript += "\t" + "ImportedAsset.append(asset)" + "\n"
				if (obj.UseStaticMeshLODGroup == True):
					ImportScript += "\t" "asset.LODGroup = '" + obj.StaticMeshLODGroup + "'" + "\n"
				if (obj.UseStaticMeshLightMapRes == True):
					ImportScript += "\t" "asset.LightMapResolution = " + str(obj.StaticMeshLightMapRes) + "\n"
				ImportScript += "except:" + "\n"
				ImportScript += "\t" + "ImportedAsset.append('Import error for asset named \""+obj.name+"\" ')" + "\n"
								
			if asset.assetType == "SkeletalMesh":
				ImportScript += "fbx_factory = PyFbxFactory()" + "\n"
				ImportScript += "fbx_factory.ImportUI.bImportMaterials = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.bImportTextures = False" + "\n"
				ImportScript += "fbx_factory.ImportUI.TextureImportData.MaterialSearchLocation = EMaterialSearchLocation." + obj.MaterialSearchLocation + "\n"
				ImportScript += "fbx_factory.ImportUI.bImportAnimations = False" + "\n"
				ImportScript += "fbx_factory.ImportUI.SkeletalMeshImportData.bImportMorphTargets = True" + "\n"
				ImportScript += "fbx_factory.ImportUI.bCreatePhysicsAsset = " + str(obj.CreatePhysicsAsset) + "\n"
				ImportScript += "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"			
				ImportScript += r"AssetImportLocation = os.path.join(UnrealImportLocation, r'"+MeshRelatifImportLoc+r"').replace('\\','/')" + "\n"
				ImportScript += "AssetImportLocation = AssetImportLocation.rstrip('/')" + "\n"
				#-----------Import
				ImportScript += "try:" + "\n"
				ImportScript += "\t" + "asset = fbx_factory.factory_import_object(FbxLoc, AssetImportLocation)" + "\n"
				ImportScript += "\t" + "ImportedAsset.append(asset)" + "\n"
				ImportScript += "except:" + "\n"
				ImportScript += "\t" + "ImportedAsset.append('Import error for asset named \""+obj.name+"\" ')" + "\n"
			
			if (asset.assetType == "Animation" or asset.assetType == "Pose"):
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
				ImportScript += "\t" + r"AssetImportLocation = os.path.join(UnrealImportLocation, r'"+AnimRelatifImportLoc+r"').replace('\\','/')" + "\n"
				ImportScript += "\t" + "AssetImportLocation = AssetImportLocation.rstrip('/')" + "\n"
				#-----------Import
				ImportScript += "\t" + "try:" + "\n"
				ImportScript += "\t\t" + "asset = fbx_factory.factory_import_object(FbxLoc, AssetImportLocation)" + "\n"
				ImportScript += "\t\t" + "ImportedAsset.append(asset)" + "\n"
				ImportScript += "\t" + "except:" + "\n"
				ImportScript += "\t\t" + "ImportedAsset.append('Import error for asset named \""+obj.name+"\" ')" + "\n"
				ImportScript += "else:" + "\n"
				ImportScript += "\t" + "ImportedAsset.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"
			
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
	#Generate a script for import camera in Ue4 sequencer
	scene = bpy.context.scene
	
	#Comment
	ImportScript = "#This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += "#This script will import in unreal all camera in target sequencer" + "\n"
	ImportScript += "#The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "\n"
	ImportScript += "import os.path" + "\n"
	ImportScript += "import configparser" + "\n"
	ImportScript += "import unreal_engine as ue" + "\n"
	ImportScript += "from unreal_engine.classes import MovieSceneCameraCutTrack, MovieScene3DTransformSection, MovieScene3DTransformTrack, MovieSceneAudioTrack, CineCameraActor" + "\n"
	ImportScript += "from unreal_engine.structs import FloatRange, FloatRangeBound, MovieSceneObjectBindingID, FrameRate" + "\n"
	ImportScript += "from unreal_engine import FTransform, FVector, FColor" + "\n"
	ImportScript += "from unreal_engine.enums import EMovieSceneObjectBindingSpace" + "\n"
	ImportScript += "\n"
	
	#Prepare def	
	ImportScript += "def AddSequencerSectionKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	ImportScript += "\t" + "Config = configparser.ConfigParser()" + "\n"
	ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t" + "frame = float(option)/"+str(scene.render.fps)+" #FrameRate" + "\n"
	ImportScript += "\t\t" + "value = float(Config.get(SectionFileName, option))" + "\n"
	ImportScript += "\t\t" + "SequencerSection.sequencer_section_add_key(frame,value)" + "\n"
			
	#Prepare var and process import
		

	
	ImportScript += 'seq = ue.find_asset("'+scene.unreal_levelsequence_reference+'")' + "\n"
	ImportScript += 'if seq:' + "\n"
	ImportScript += "\t" + 'print("Sequencer reference found")' + "\n"
	ImportScript += "\t" + "ImportedCamera = [] #(CameraName, CameraGuid)" + "\n"
	ImportScript += "\t" + 'print("========================= Import started ! =========================")' + "\n"
	ImportScript += "\t" + "\n"
		#Set frame rate
	ImportScript += "\t" + "#Set frame rate" + "\n"
	ImportScript += "\t" + "myFFrameRate = FrameRate()" + "\n"
	ImportScript += "\t" + "myFFrameRate.Denominator = 1" + "\n"
	ImportScript += "\t" + "myFFrameRate.Numerator = " + str(scene.render.fps) + "\n"
	ImportScript += "\t" + "seq.MovieScene.DisplayRate = myFFrameRate" + "\n"
	ImportScript += "\t" + "\n"
		#Set playback range
	StartPlayback = str(scene.frame_start/scene.render.fps)
	EndPlayback = str(scene.frame_end/scene.render.fps)
	ImportScript += "\t" + "#Set playback range" + "\n"
	ImportScript += "\t" + "seq.sequencer_set_playback_range("+StartPlayback+", "+EndPlayback+")" + "\n"
	ImportScript += "\t" + "camera_cut_track = seq.sequencer_add_camera_cut_track()" + "\n"
	ImportScript += "\t" + "world = ue.get_editor_world()" + "\n"
	
	ImportScript += "else:" + "\n"
	ImportScript += "\t" + 'print("Sequencer reference not valid !")' + "\n"
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
			FbxLoc = (os.path.join(asset.exportPath, GetObjExportFileName(camera)))
			ImportScript += "\t" + "FbxLoc = os.path.join(r'"+FbxLoc+"')" + "\n"
			ImportScript += "\t" + "for obj in seq.MovieScene.ObjectBindings:" + "\n"
			ImportScript += "\t\t" + "if obj.ObjectGuid == ue.string_to_guid(camera_spawnable_guid):" + "\n"
			ImportScript += "\t\t\t" + "transform_track = obj.tracks[0]" + "\n"
			ImportScript += "\t\t\t" + "camera_section = transform_track.Sections[0]" + "\n"
			ImportScript += "\t\t\t" + "camera_section.sequencer_import_fbx_transform(FbxLoc, '" + camera.name + "')" + "\n"
			ImportScript += "\n"
			
			#Import additional tracks
			ImportScript += "\t" + "#Import additional tracks" + "\n"
			TracksLoc = (os.path.join(asset.exportPath, GetCameraTrackFileName(camera)))
			ImportScript += "\t" + "TracksLoc = os.path.join(r'"+TracksLoc+"')" + "\n"
			ImportScript += "\t" + "Component = seq.MovieScene.ObjectBindings[-1]" + "\n"
			ImportScript += "\t" + "sectionFocalLength = Component.Tracks[0].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionKeysByIniFile(sectionFocalLength, 'FocalLength', TracksLoc)" + "\n"
			ImportScript += "\t" + "sectionFocusDistance = Component.Tracks[1].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionKeysByIniFile(sectionFocusDistance, 'FocusDistance', TracksLoc)" + "\n"
			ImportScript += "\t" + "sectionAperture = Component.Tracks[2].Sections[0]" + "\n"
			ImportScript += "\t" + "AddSequencerSectionKeysByIniFile(sectionAperture, 'Aperture', TracksLoc)" + "\n"
			ImportScript += "\n"
			ImportScript += "\n\n"

	def getMarkerSceneSections():
		scene = bpy.context.scene
		markersOrderly = []	
		firstMarkersFrame = scene.frame_start
		lastMarkersFrame = scene.frame_end+1
		
		
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
			if scene.frame_end > markersOrderly[x].frame:
				startTime = markersOrderly[x].frame/scene.render.fps
				if x+1 != len(markersOrderly):
					EndTime = markersOrderly[x+1].frame/scene.render.fps
				else:
					EndTime = scene.frame_end/scene.render.fps
				sectionCuts.append([startTime, EndTime, markersOrderly[x]])
			
		return sectionCuts
		
	for section in getMarkerSceneSections():	
				#Camera cut sections
			ImportScript += "#Import camera cut section" + "\n"
			ImportScript += "if seq:" + "\n"
			ImportScript += "\t" + "camera_cut_section = camera_cut_track.sequencer_track_add_section()" + "\n"
			if section[2].camera is not None:
				if section[2].camera.ExportEnum == "export_recursive" or section[2].camera.ExportEnum == "auto":
					ImportScript += "\t" + "for camera in ImportedCamera:" + "\n"
					ImportScript += "\t\t" + "if camera[0] == '"+section[2].camera.name+"':" + "\n"
					ImportScript += "\t\t\t" + "camera_cut_section.CameraBindingID = MovieSceneObjectBindingID( Guid=ue.string_to_guid( camera[1] ), Space=EMovieSceneObjectBindingSpace.Local )" + "\n"
				else:
					ImportScript += "\t" + "#Not camera found for this section" + "\n"
			else:
				ImportScript += "\t" + "#Not camera found for this section" + "\n"
			ImportScript += "\t" + "camera_cut_section.sequencer_set_section_range("+str(section[0])+", "+str(section[1])+")" + "\n"
	
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
		distance = (transA*transB).translation.z #Z is the Fosrward
		if distance < 0:
			distance *= -1
		return distance

	def	getAllCamDistKeys(Camera, Target):
		scene = bpy.context.scene
		saveFrame = scene.frame_current #Save current frame
		keys = []
		for frame in range(scene.frame_start, scene.frame_end+1):
			scene.frame_set(frame)
			v = getCameraFocusDistance(Camera, Target)
			keys.append((frame,v))
		scene.frame_set(saveFrame)	#Resets previous start frame
		return keys

		
	def getOneDataKeysByPath(obj,DataPath, DataValue, Frame):
		scene = bpy.context.scene
		if obj.data.animation_data is not None:
			f = obj.data.animation_data.action.fcurves.find(DataPath)
			if f is not None:
				return f.evaluate(Frame)
		return DataValue
		
	def getAllDataKeysByPath(obj,DataPath, DataValue):
		scene = bpy.context.scene
		keys = []
		if obj.data.animation_data is not None:
			if obj.data.animation_data.action is not None:
				f = obj.data.animation_data.action.fcurves.find(DataPath)
				if f is not None:
					for frame in range(scene.frame_start, scene.frame_end+1):
						v = f.evaluate(frame)
						keys.append((frame,v))
					return keys
		return[(scene.frame_start,DataValue)]

	scene = bpy.context.scene
	ImportScript = ";This file was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" + "\n"
	ImportScript += ";This file contains animation informations that is not supported with fbx files" + "\n"
	ImportScript += ";The script must be used in Unreal Engine Editor with UnrealEnginePython : https://github.com/20tab/UnrealEnginePython" + "\n"
	ImportScript += "\n\n\n"

	#Get FocalLength keys
	ImportScript += "[FocalLength]" + "\n"
	for key in getAllDataKeysByPath(obj,"lens",obj.data.lens): 
		#Fov type return auto to lens
		ImportScript += str(key[0])+": "+str(key[1]) + "\n"
	ImportScript += "\n\n\n"
	
	#Get FocusDistance keys
	ImportScript += "[FocusDistance]" + "\n"
	if obj.data.dof_object is None:
		DataKeys = getAllDataKeysByPath(obj,"dof_distance",obj.data.dof_distance)
	else: 
		DataKeys = getAllCamDistKeys(obj, obj.data.dof_object)
	for key in DataKeys:
		CorrectedValue = key[1]*100
		if CorrectedValue > 0:
			ImportScript += str(key[0])+": "+str(CorrectedValue) + "\n"
		else:
			ImportScript += str(key[0])+": "+str(100000) + "\n" #100000 is default value in ue4
	ImportScript += "\n\n\n"
	
	#Get Aperture (Depth of Field) keys
	ImportScript += "[Aperture]" + "\n"
	if scene.render.engine == 'CYCLES': #Work only with cycle.
		if obj.data.cycles.aperture_type == 'FSTOP':
			DataKeys = getAllDataKeysByPath(obj,"cycles.aperture_fstop",obj.data.cycles.aperture_fstop)
		else:
			DataKeys = getAllDataKeysByPath(obj,"cycles.aperture_size",obj.data.cycles.aperture_size)
		for key in DataKeys:
			CorrectedValue = key[1]
			if obj.data.cycles.aperture_type == 'RADIUS':
				#Convert radius to Fstop
				FocalLength = getOneDataKeysByPath(obj,"lens",obj.data.lens,key[0])
				if CorrectedValue == 0:
					CorrectedValue = 64
				else:
					CorrectedValue = (FocalLength/(key[1]*2000))
			ImportScript += str(key[0])+": "+str(CorrectedValue) + "\n"	
	else:
		ImportScript += "0: 21\n" #21 is default value in ue4
	ImportScript += "\n\n\n"
	return ImportScript
	
def WriteAllTextFiles():

	scene = bpy.context.scene
	if scene.text_exportLog:
		exportLog = WriteExportLog()
		if exportLog is not None:
			exportLogFilename = "ExportLog.txt"
			ExportSingleText(exportLog, scene.export_other_file_path, exportLogFilename)
		
	if scene.text_ImportAssetScript:
		ImportAssetScript = WriteImportAssetScript()
		if ImportAssetScript is not None:
			ImportAssetScriptFilename = "ImportAssetScript.py" 
			ExportSingleText(ImportAssetScript, scene.export_other_file_path, ImportAssetScriptFilename)
			
	if scene.text_ImportSequenceScript:
		ImportSequencerScript = WriteImportSequencerScript()
		if ImportSequencerScript is not None:
			ImportSequencerScriptFilename = "ImportSequencerScript.py" 
			ExportSingleText(ImportSequencerScript, scene.export_other_file_path, ImportSequencerScriptFilename)

