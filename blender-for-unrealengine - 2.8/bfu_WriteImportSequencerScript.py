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


def WriteImportSequencerScript(use20tab = False):
	GetImportSequencerScriptCommand()
	scene = bpy.context.scene

	#Import
	ImportScript = "def CreateSequencer():" + "\n"
	ImportScript += "\t" + "import os.path" + "\n"
	ImportScript += "\t" + "import time" + "\n"


	if use20tab == True:
		ImportScript += "\t" + "import configparser" + "\n"
		ImportScript += "\t" + "import unreal_engine as ue" + "\n"
		ImportScript += "\t" + "from unreal_engine.classes import MovieSceneCameraCutTrack, MovieScene3DTransformSection, MovieScene3DTransformTrack, MovieSceneAudioTrack, CineCameraActor, LevelSequenceFactoryNew" + "\n"
		ImportScript += "\t" + "if ue.ENGINE_MINOR_VERSION >= 20:" + "\n"
		ImportScript += "\t\t" + "from unreal_engine.structs import FloatRange, FloatRangeBound, MovieSceneObjectBindingID, FrameRate" + "\n"
		ImportScript += "\t" + "else:" + "\n"
		ImportScript += "\t\t" + "from unreal_engine.structs import FloatRange, FloatRangeBound, MovieSceneObjectBindingID" + "\n"
		ImportScript += "\t" + "from unreal_engine import FTransform, FRotator, FVector, FColor" + "\n"
		ImportScript += "\t" + "from unreal_engine.enums import EMovieSceneObjectBindingSpace" + "\n"
		ImportScript += "\t" + "from unreal_engine.structs import MovieSceneObjectBindingID" + "\n"
	else:
		ImportScript += "\t" + "import ConfigParser" + "\n"
		ImportScript += "\t" + "import unreal" + "\n"

	ImportScript += "\n"
	ImportScript += "\n"


	#Prepare var
	ImportScript += '\t' + 'seqPath = r"'+os.path.join(r'/Game/',scene.unreal_levelsequence_import_location)+'"' + '\n'
	ImportScript += "\t" + "seqName = r'"+scene.unreal_levelsequence_name+"'" + "\n"
	ImportScript += "\t" + "seqTempName = r'"+scene.unreal_levelsequence_name+"'+str(time.time())" + "\n"
	if use20tab == True:
		ImportScript += "\t" + "mustBeReplace = False" + "\n"
	ImportScript += "\t" + "startFrame = " + str(scene.frame_start) + "\n"
	ImportScript += "\t" + "endFrame = " + str(scene.frame_end+1) + "\n"
	ImportScript += "\t" + "frameRateDenominator = " + str(scene.render.fps_base) + "\n"
	ImportScript += "\t" + "frameRateNumerator = " + str(scene.render.fps) + "\n"
	ImportScript += "\t" + "secureCrop = 0.0001 #add end crop for avoid section overlay" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"


	#Prepare def
	ImportScript += "\t" +	"def AddSequencerSectionTransformKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	if use20tab == True:
		ImportScript += "\t\t" + "Config = configparser.ConfigParser()" + "\n"
	else:
		ImportScript += "\t\t" + "Config = ConfigParser.ConfigParser()" + "\n"
	ImportScript += "\t\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t\t" + "frame = float(option)/float(frameRateNumerator) #FrameRate" + "\n"
	ImportScript += "\t\t\t" + "list = Config.get(SectionFileName, option)" + "\n"

	if use20tab == True:
		ImportScript += "\t\t\t" + "list = list.split(',')" + "\n"
		ImportScript += "\t\t\t" + "transform = FTransform(FVector(float(list[0]), float(list[1]), float(list[2])), FRotator(float(list[3]), float(list[4]), float(list[5])))" + "\n"
		ImportScript += "\t\t\t" + "SequencerSection.sequencer_section_add_key(frame,transform)" + "\n"
	else:
		ImportScript += "\t\t\t" + "for x in range(0, 9): #(x,y,z x,y,z x,y,z)" + "\n"
		ImportScript += "\t\t\t\t" + "value = float(list.split(',')[x])" + "\n"
		ImportScript += "\t\t\t\t" + "SequencerSection.get_channels()[x].add_key(unreal.FrameNumber(frame*float(frameRateNumerator)),value)" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	ImportScript += "\t" +	"def AddSequencerSectionFloatKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	if use20tab == True:
		ImportScript += "\t\t" + "Config = configparser.ConfigParser()" + "\n"
	else:
		ImportScript += "\t\t" + "Config = ConfigParser.ConfigParser()" + "\n"
	ImportScript += "\t\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t\t" + "frame = float(option)/float(frameRateNumerator) #FrameRate" + "\n"
	ImportScript += "\t\t\t" + "value = float(Config.get(SectionFileName, option))" + "\n"
	if use20tab == True:
		ImportScript += "\t\t\t" + "SequencerSection.sequencer_section_add_key(frame,value)" + "\n"
	else:
		ImportScript += "\t\t\t" + "SequencerSection.get_channels()[0].add_key(unreal.FrameNumber(frame*float(frameRateNumerator)),value)" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"

	ImportScript += "\t" + "def AddSequencerSectionBoolKeysByIniFile(SequencerSection, SectionFileName, FileLoc):" + "\n"
	if use20tab == True:
		ImportScript += "\t\t" + "Config = configparser.ConfigParser()" + "\n"
	else:
		ImportScript += "\t\t" + "Config = ConfigParser.ConfigParser()" + "\n"
	ImportScript += "\t\t" + "Config.read(FileLoc)" + "\n"
	ImportScript += "\t\t" + "for option in Config.options(SectionFileName):" + "\n"
	ImportScript += "\t\t\t" + "frame = float(option)/float(frameRateNumerator) #FrameRate" + "\n"
	ImportScript += "\t\t\t" + "value = Config.getboolean(SectionFileName, option)" + "\n"
	if use20tab == True:
		ImportScript += "\t\t\t" + "SequencerSection.sequencer_section_add_key(frame,value)" + "\n"
	else:
		ImportScript += "\t\t\t" + "SequencerSection.get_channels()[0].add_key(unreal.FrameNumber(frame*float(frameRateNumerator)),value)" + "\n"
	ImportScript += "\n"
	ImportScript += "\n"


	#Prepare process import

	if use20tab == True:
		ImportScript += "\t" + "if ue.find_asset(seqPath+'/'+seqName):" + "\n"
		ImportScript += "\t\t" + 'print("Warning this file already exists")' + "\n"
		ImportScript += "\t\t" + "factory = LevelSequenceFactoryNew()" + "\n"
		ImportScript += "\t\t" + "seq = factory.factory_create_new(seqPath+'/'+seqTempName.replace('.',''))" + "\n"
		ImportScript += "\t\t" +	"mustBeReplace = True" + "\n"
		ImportScript += "\t" + "else:" + "\n"
		ImportScript += "\t\t" + "factory = LevelSequenceFactoryNew()" + "\n"
		ImportScript += "\t\t" + "seq = factory.factory_create_new(seqPath+'/'+seqName.replace('.',''))" + "\n"
	else:
		ImportScript += "\t" + 'print("Warning this file already exists")' + "\n"
		ImportScript += "\t" + "factory = unreal.LevelSequenceFactoryNew()" + "\n"
		ImportScript += "\t" + "asset_tools = unreal.AssetToolsHelpers.get_asset_tools()" + "\n"
		ImportScript += "\t" + "seq = asset_tools.create_asset_with_dialog(seqName.replace('.',''), seqPath, None, factory)" + "\n"
		#ImportScript += "unreal.EditorAssetLibrary.save_loaded_asset(seq)" + "\n"

	ImportScript += "\t" + "if seq is None:" + "\n"
	ImportScript += "\t\t" + "return 'Error /!\ level sequencer factory_create fail' " + "\n"
	ImportScript += "\n"


	ImportScript += "\t" + 'print("Sequencer reference created")' + "\n"
	ImportScript += "\t" + 'print(seq)' + "\n"
	ImportScript += "\t" + "ImportedCamera = [] #(CameraName, CameraGuid)" + "\n"
	ImportScript += "\t" + 'print("========================= Import started ! =========================")' + "\n"
	ImportScript += "\t" + "\n"

	ImportScript += "\t" + "#Set frame rate" + "\n"
	if use20tab == True:
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
	else:
		ImportScript += "\t" + "myFFrameRate = unreal.FrameRate()" + "\n"
		ImportScript += "\t" + "myFFrameRate.denominator = frameRateDenominator" + "\n"
		ImportScript += "\t" + "myFFrameRate.numerator = frameRateNumerator" + "\n"
		ImportScript += "\t" + "seq.set_display_rate(myFFrameRate)" + "\n"

	#Set playback range
	ImportScript += "\t" + "#Set playback range" + "\n"
	if use20tab == True:
		ImportScript += "\t" + "seq.sequencer_set_playback_range(startFrame/frameRateNumerator, (endFrame-secureCrop)/frameRateNumerator)" + "\n"
		ImportScript += "\t" + "camera_cut_track = seq.sequencer_add_camera_cut_track()" + "\n"
		ImportScript += "\t" + "world = ue.get_editor_world()" + "\n"
	else:
		ImportScript += "\t" + "seq.set_playback_end_seconds((endFrame-secureCrop)/float(frameRateNumerator))" + "\n"
		ImportScript += "\t" + "seq.set_playback_start_seconds(startFrame/float(frameRateNumerator))" + "\n" #set_playback_end_seconds
		ImportScript += "\t" + "camera_cut_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)" + "\n"
		#ImportScript += "\t" + "world = unreal.EditorLevelLibrary.get_editor_world()" + "\n"

	ImportScript += "\n"
	ImportScript += "\n"

	#Import camera
	for asset in scene.UnrealExportedAssetsList:
		if (asset.assetType == "Camera"):
			camera = asset.object
			ImportScript += "\t" + "#import " + camera.name + "\n"
			ImportScript += "\t" + 'print("Start import ' + camera.name + '")' + "\n"
			ImportScript += "\t" + "\n"

			#Create spawnable camera
			ImportScript += "\t" + "#Create spawnable camera" + "\n"
			if use20tab == True:
				ImportScript += "\t" + "cine_camera_actor = world.actor_spawn(CineCameraActor) #Create camera" + "\n"
				ImportScript += "\t" + "cine_camera_actor.set_actor_label('" + camera.name + "')" + "\n"
				ImportScript += "\t" + "cine_camera_actor.CameraComponent.LensSettings.MinFStop = 0" + "\n"
				ImportScript += "\t" + "cine_camera_actor.CameraComponent.LensSettings.MaxFStop = 1000" + "\n"
				ImportScript += "\t" + "camera_spawnable_guid = seq.sequencer_make_new_spawnable(cine_camera_actor) #Add camera in sequencer" + "\n"
				ImportScript += "\t" + "cine_camera_actor.actor_destroy()" + "\n"
				ImportScript += "\t" + "ImportedCamera.append(('"+camera.name+"', camera_spawnable_guid))" + "\n"
			else:
				ImportScript += "\t" + "cine_camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CineCameraActor,  [0,0,0]) #Add camera in sequencer" + "\n"
				ImportScript += "\t" + "cine_camera_actor.set_actor_label('" + camera.name + "')" + "\n"
				ImportScript += "\t" + "cine_camera_actor.camera_component.lens_settings.min_f_stop = 0" + "\n"
				ImportScript += "\t" + "cine_camera_actor.camera_component.lens_settings.max_f_stop = 1000" + "\n"
				ImportScript += "\t" + "camera_spawnable = seq.add_possessable(cine_camera_actor) #Add camera in sequencer" + "\n"
				ImportScript += "\t" + "ImportedCamera.append(('"+camera.name+"', camera_spawnable))" + "\n"
				'''
				ImportScript += "\t" + "camera_spawnable = seq.add_spawnable_from_class(unreal.CineCameraActor) #Add camera in sequencer" + "\n"
				ImportScript += "\t" + "camera_spawnable.get_object_template().set_actor_label('" + camera.name + "')" + "\n"
				ImportScript += "\t" + "camera_spawnable.get_object_template().camera_component.lens_settings.min_f_stop = 0" + "\n"
				ImportScript += "\t" + "camera_spawnable.get_object_template().camera_component.lens_settings.max_f_stop = 1000" + "\n"
				ImportScript += "\t" + "ImportedCamera.append(('"+camera.name+"', camera_spawnable))" + "\n"
				'''
			ImportScript += "\n"

			#Import fbx transform
			ImportScript += "\t" + "#Import fbx transform" + "\n"
			AdditionalTracksLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalTrack.ini")))
			ImportScript += '\t' + 'AdditionalTracksLoc = os.path.join(r"'+AdditionalTracksLoc+'")' + '\n'
			fbxFilePath = (os.path.join(asset.exportPath, GetObjExportFileName(camera)))
			ImportScript += '\t' + 'fbxFilePath = os.path.join(r"'+fbxFilePath+'")' + '\n'
			if use20tab == True:
				ImportScript += "\t" + "for obj in seq.MovieScene.ObjectBindings:" + "\n"
				ImportScript += "\t\t" + "if obj.ObjectGuid == ue.string_to_guid(camera_spawnable_guid):" + "\n"
				ImportScript += "\t\t\t" + "transform_track = obj.tracks[0]" + "\n"
				ImportScript += "\t\t\t" + "transform_section = transform_track.Sections[0]" + "\n"
				#ImportScript += "\t\t\t" + "transform_section.sequencer_import_fbx_transform(fbxFilePath, '" + camera.name + "')" + "\n"
				ImportScript += "\t\t\t" + "AddSequencerSectionTransformKeysByIniFile(transform_section, 'Transform', AdditionalTracksLoc)" + "\n"
				ImportScript += "\n"
				ImportScript += "\t\t\t" + "#Spawned tracks" + "\n"
				ImportScript += "\t\t\t" + "spawned_track = obj.tracks[1]" + "\n"
				ImportScript += "\t\t\t" + "spawned_section = spawned_track.Sections[0]" + "\n"
				ImportScript += "\t\t\t" + "AddSequencerSectionBoolKeysByIniFile(spawned_section, 'Spawned', AdditionalTracksLoc)" + "\n"
			else:
				ImportScript += "\t" + "transform_track = camera_spawnable.add_track(unreal.MovieScene3DTransformTrack)" + "\n"
				ImportScript += "\t" + "transform_section = transform_track.add_section()" + "\n"
				ImportScript += "\t" + "transform_section.set_end_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "transform_section.set_start_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "AddSequencerSectionTransformKeysByIniFile(transform_section, 'Transform', AdditionalTracksLoc)" + "\n"
				'''
				ImportScript += "\n"
				ImportScript += "\t" + "#Spawned tracks" + "\n"
				ImportScript += "\t" + "spawned_track = camera_spawnable.get_tracks()[0]" + "\n"  #Spawn tracks with 0
				ImportScript += "\t" + "spawned_section = spawned_track.get_sections()[0]" + "\n"
				ImportScript += "\t" + "AddSequencerSectionBoolKeysByIniFile(spawned_section, 'Spawned', AdditionalTracksLoc)" + "\n"
				'''
			ImportScript += "\n"

			#Import additional tracks
			ImportScript += "\t" + "#Import additional tracks (camera_component)" + "\n"
			if use20tab == True:
				ImportScript += "\t" + "camera_component = seq.MovieScene.ObjectBindings[-1] #Get the last" + "\n"
				ImportScript += "\t" + "sectionFocalLength = camera_component.Tracks[0].Sections[0]" + "\n"
				ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, 'FocalLength', AdditionalTracksLoc)" + "\n"
				ImportScript += "\n"
				ImportScript += "\t" + "sectionFocusDistance = camera_component.Tracks[1].Sections[0]" + "\n"
				ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, 'FocusDistance', AdditionalTracksLoc)" + "\n"
				ImportScript += "\n"
				ImportScript += "\t" + "sectionAperture = camera_component.Tracks[2].Sections[0]" + "\n"
				ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionAperture, 'Aperture', AdditionalTracksLoc)" + "\n"
			else:
				ImportScript += "\t" + "camera_component = seq.add_possessable(cine_camera_actor.camera_component) #Get the last" + "\n"
				#ImportScript += "\t" + "camera_component = seq.add_possessable(camera_spawnable.get_object_template().camera_component) #Get the last" + "\n"
				ImportScript += "\t" + "TrackFocalLength = camera_component.add_track(unreal.MovieSceneFloatTrack)" + "\n"
				ImportScript += "\t" + "TrackFocalLength.set_property_name_and_path('CurrentFocalLength', 'CurrentFocalLength')" + "\n"
				ImportScript += "\t" + "TrackFocalLength.set_editor_property('display_name', 'Current Focal Length')" + "\n"
				ImportScript += "\t" + "sectionFocalLength = TrackFocalLength.add_section()" + "\n"
				ImportScript += "\t" + "sectionFocalLength.set_end_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "sectionFocalLength.set_start_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocalLength, 'FocalLength', AdditionalTracksLoc)" + "\n"
				ImportScript += "\n"
				ImportScript += "\t" + "TrackFocusDistance = camera_component.add_track(unreal.MovieSceneFloatTrack)" + "\n"
				ImportScript += "\t" + "TrackFocusDistance.set_property_name_and_path('ManualFocusDistance', 'ManualFocusDistance')" + "\n"
				ImportScript += "\t" + "TrackFocusDistance.set_editor_property('display_name', 'Manual Focus Distance')" + "\n"
				ImportScript += "\t" + "sectionFocusDistance = TrackFocusDistance.add_section()" + "\n"
				ImportScript += "\t" + "sectionFocusDistance.set_end_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "sectionFocusDistance.set_start_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "AddSequencerSectionFloatKeysByIniFile(sectionFocusDistance, 'FocusDistance', AdditionalTracksLoc)" + "\n"
				ImportScript += "\n"
				ImportScript += "\t" + "TracknAperture = camera_component.add_track(unreal.MovieSceneFloatTrack)" + "\n"
				ImportScript += "\t" + "TracknAperture.set_property_name_and_path('CurrentAperture', 'CurrentAperture')" + "\n"
				ImportScript += "\t" + "TracknAperture.set_editor_property('display_name', 'Current Aperture')" + "\n"
				ImportScript += "\t" + "sectionAperture = TracknAperture.add_section()" + "\n"
				ImportScript += "\t" + "sectionAperture.set_end_frame_bounded(False)" + "\n"
				ImportScript += "\t" + "sectionAperture.set_start_frame_bounded(False)" + "\n"
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
			ImportScript += "\t" + "#Import camera cut section" + "\n"
			if use20tab == True:
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
			else:
				ImportScript += "\t" + "camera_cut_section = camera_cut_track.add_section()" + "\n"
				if section[2] is not None:
					if section[2].ExportEnum == "export_recursive" or section[2].ExportEnum == "auto":
						ImportScript += "\t" + "for camera in ImportedCamera:" + "\n"
						ImportScript += "\t\t" + "if camera[0] == '"+section[2].name+"':" + "\n"
						ImportScript += "\t\t\t" + "camera_binding_id = unreal.MovieSceneObjectBindingID()" + "\n"
						ImportScript += "\t\t\t" + "camera_binding_id.set_editor_property('guid', camera[1].get_id())" + "\n"
						ImportScript += "\t\t\t" + "camera_cut_section.set_camera_binding_id(camera_binding_id)" + "\n"
					else:
						ImportScript += "\t" + "#Not camera found for this section" + "\n"
				else:
					ImportScript += "\t" + "#Not camera found for this section" + "\n"
				#ImportScript += "\t" + "sectionRange = unreal.MovieSceneFrameRange()" + "\n"
				#ImportScript += "\t" + "camera_cut_section.set_editor_property('section_range', sectionRange)" + "\n"

				ImportScript += "\t" + "camera_cut_section.set_end_frame_seconds(("+str(section[1])+"-secureCrop)/float(frameRateNumerator))" + "\n"
				ImportScript += "\t" + "camera_cut_section.set_start_frame_seconds("+str(section[0])+"/float(frameRateNumerator))" + "\n"

	if use20tab == True:
		#Replace
		ImportScript += "\t" + "if mustBeReplace == True:" + "\n"
		ImportScript += "\t\t" + "OldSeq = seqPath+'/'+seqName.replace('.','')+'.'+seqName.replace('.','')" + "\n"
		ImportScript += "\t\t" + "NewSeq = seqPath+'/'+seqTempName.replace('.','')+'.'+seqTempName.replace('.','')" + "\n"
		ImportScript += "\t\t" + "print(OldSeq)" + "\n"
		ImportScript += "\t\t" + "print(NewSeq)" + "\n"
		ImportScript += "\t\t" + "print(\"LevelSequence'\"+OldSeq+\"'\")" + "\n"
		#ImportScript += "\t\t" + "ue.delete_asset(OldSeq)" + "\n"
		#ImportScript += "\t\t" + "ue.rename_asset(NewSeq, seqName.replace('.',''))" + "\n"

	#import result
	ImportScript += "\t" + "print('========================= Imports completed ! =========================')" + "\n"
	ImportScript += "\t" + "\n"
	ImportScript += "\t" + "for cam in ImportedCamera:" + "\n"
	ImportScript += "\t\t" + "print(cam[0])" + "\n"
	ImportScript += "\t" + "\n"
	ImportScript += "\t" + "print('=========================')" + "\n"
	
		
	ImportScript += "#Select and open seq in content browser" + "\n"
	
	if use20tab == True:
		ImportScript += "\t" + "seq.sequencer_changed(True)" + "\n"
		pass #sync_browser_to_objects
	else:
		ImportScript += "\t" + "unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets([unreal.load_asset(seqPath+'/'+seqName.replace('.',''))])" + "\n"
		ImportScript += "\t" + "unreal.EditorAssetLibrary.sync_browser_to_objects([seqPath+'/'+seqName.replace('.','')])" + "\n"
	ImportScript += "\t" + "return 'Sequencer created with success !' " + "\n"
	ImportScript += "print(CreateSequencer())" + "\n"

	OutImportScript = WriteImportPythonHeadComment(use20tab, True)
	OutImportScript += ImportScript#bfu_Utils.AddFrontEachLine(ImportScript, "\t")

	return OutImportScript