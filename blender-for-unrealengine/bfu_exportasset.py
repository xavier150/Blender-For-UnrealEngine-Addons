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
import math
from .bfu_basics import *
from .bfu_utils import *

import importlib
from . import bfu_writetext
importlib.reload(bfu_writetext)
	
def ExportSingleFbxAnimation(dirpath, filename, obj, targetAction, actionType):
	#Export a single animation or pose

	
	scene = bpy.context.scene
	filename = ValidFilename(filename)
	curr_time = time.process_time()
	print(obj.name)
	UserAction = obj.animation_data.action #Save current action
	
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	ResetArmaturePose(obj)
	obj.animation_data.action = targetAction #Apply desired action
	scene.frame_start = GetDesiredActionStartEndTime(obj, targetAction)[0]
	scene.frame_end = GetDesiredActionStartEndTime(obj, targetAction)[1]

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		version='BIN7400',
		use_selection=True,
		object_types={'ARMATURE', 'MESH'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=obj.SampleAnimForExport,
		bake_anim_simplify_factor=obj.SimplifyAnimForExport
		)
	obj.location = originalLoc #Resets previous object location
	ResetArmaturePose(obj)
	obj.animation_data.action = UserAction #Resets previous action
	exportTime = time.process_time()-curr_time
	
	MyAsset = scene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = actionType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleFbxMesh(dirpath, filename, obj):
	#Export a single Mesh
	
	scene = bpy.context.scene
	filename = ValidFilename(filename)
	curr_time = time.process_time()
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save current object location
	obj.location = (0,0,0) #Moves object to the center of the scene for export
	#Set socket scale for Unreal
	for socket in GetAllChildSocket(obj):
		socket.delta_scale*=0.01

	SelectParentAndDesiredChilds(obj)
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	meshType = GetAssetType(obj)

	object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}
	if meshType == "StaticMesh":
		#Dont export ARMATURE with static mesh
		object_types={'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}
	
	bpy.ops.export_scene.fbx(filepath=fullpath,
		check_existing=False,
		version='BIN7400',
		use_selection=True,
		object_types=object_types,
		mesh_smooth_type="FACE",
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=False
		)
	
	obj.location = originalLoc #Resets previous object location
	exportTime = time.process_time()-curr_time
	
	#Reset socket scale
	for socket in GetAllChildSocket(obj):
		socket.delta_scale*=100
	
	MyAsset = scene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = meshType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset

	
def ExportSingleFbxCamera(dirpath, filename, obj):
	#Export single camera

	scene = bpy.context.scene
	filename = ValidFilename(filename)
	if obj.type != 'CAMERA':
		return;
	curr_time = time.process_time()
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	bpy.ops.object.select_all(action='DESELECT')

	#Select and rescale camera for export
	obj.select = True
	scene.objects.active = obj
	obj.delta_scale*=0.01
	if obj.animation_data is not None:
		action = obj.animation_data.action
		scene.frame_start = GetDesiredActionStartEndTime(obj, action)[0]
		scene.frame_end = GetDesiredActionStartEndTime(obj, action)[1]
	
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		axis_forward = ('-Z'), #-Z
		axis_up = ("Y"), #Y
		version='BIN7400',
		use_selection=True,
		object_types={'CAMERA'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=obj.SampleAnimForExport,
		bake_anim_simplify_factor=obj.SimplifyAnimForExport
		)

	#Reset camera scale
	obj.delta_scale*=100

	exportTime = time.process_time()-curr_time
	
	MyAsset = scene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "Camera"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset

def ExportSingleAdditionalTrackCamera(dirpath, filename, obj):
	#Export additional camera track for ue4
	#FocalLength
	#FocusDistance
	#Aperture
	
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	CameraAdditionalTrack = bfu_writetext.WriteSingleCameraAdditionalTrack(obj)
	return bfu_writetext.ExportSingleText(CameraAdditionalTrack, absdirpath, filename)
	
def ExportAllAssetByList(targetobjects):
	#Export all objects that need to be exported from a list
	

	if len(targetobjects) < 1:
		return
	
	scene = bpy.context.scene
	wm = bpy.context.window_manager
	wm.progress_begin(0, len(GetFinalAssetToExport()))

	def UpdateProgress():
		wm.progress_update(len(scene.UnrealExportedAssetsList))
	UpdateProgress()
	
	for obj in targetobjects:
		if obj.ExportEnum == "export_recursive":
			
			#Camera
			if GetAssetType(obj) == "Camera" and scene.camera_export:
				exportDir = os.path.join( scene.export_camera_file_path, obj.exportFolderName )
				UserStartFrame = scene.frame_start #Save current start frame
				UserEndFrame = scene.frame_end #Save current end frame
				ExportSingleFbxCamera(exportDir, GetObjExportFileName(obj), obj)
				
				ExportSingleAdditionalTrackCamera(exportDir, GetCameraTrackFileName(obj), obj)
				scene.frame_start = UserStartFrame #Resets previous start frame
				scene.frame_end = UserEndFrame #Resets previous end frame
				UpdateProgress()
			
			#StaticMesh
			if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				exportDir = os.path.join( scene.export_static_file_path, obj.exportFolderName )
				ExportSingleFbxMesh(exportDir, GetObjExportFileName(obj), obj)
				UpdateProgress()

			if GetAssetType(obj) == "SkeletalMesh":
				exportDir = os.path.join( scene.export_skeletal_file_path , obj.exportFolderName , obj.name )
				#SkeletalMesh
				if scene.skeletal_export:
					ExportSingleFbxMesh(exportDir, GetObjExportFileName(obj), obj)
					UpdateProgress()
				
				for action in GetActionToExport(obj):
					animExportDir = os.path.join( exportDir, scene.anim_subfolder_name )					
					animType = GetActionType(action)
									
					#Animation
					if animType == "Animation" and bpy.context.scene.anin_export == True:
						UserStartFrame = scene.frame_start #Save current start frame
						UserEndFrame = scene.frame_end #Save current end frame
						ExportSingleFbxAnimation(animExportDir, GetActionExportFileName(obj, action), obj, action, "Animation")
						scene.frame_start = UserStartFrame #Resets previous start frame
						scene.frame_end = UserEndFrame #Resets previous end frame
						UpdateProgress()
						
					#pose
					if animType == "Pose" and bpy.context.scene.pose_export == True:
						UserStartFrame = scene.frame_start #Save current start frame
						UserEndFrame = scene.frame_end #Save current end frame
						ExportSingleFbxAnimation(animExportDir,	GetActionExportFileName(obj, action), obj, action, "Pose")
						scene.frame_start = UserStartFrame #Resets previous start frame
						scene.frame_end = UserEndFrame #Resets previous end frame
						UpdateProgress()
				
	wm.progress_end()	
	
	


def PrepareAndSaveDataForExport():

	scene = bpy.context.scene
	#----------------------------------------Save data
	UserObjHide = []
	UserObjHideSelect = []
	for obj in scene.objects: #Save previous object visibility
		UserObjHide.append(obj.hide)
		UserObjHideSelect.append(obj.hide_select)
		obj.hide = False
		obj.hide_select = False

	LayerVisibility = []
	for x in range(20): #Save previous layer visibility
		LayerVisibility.append(scene.layers[x])
		scene.layers[x] = True

	if obj is None:
		scene.objects.active = bpy.data.objects[0]

	UserActive = bpy.context.active_object #Save current active object
	UserMode = None 
	if UserActive and UserActive.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		UserMode = UserActive.mode #Save current mode
		bpy.ops.object.mode_set(mode='OBJECT')
	UserSelected = bpy.context.selected_objects #Save current selected objects
	#----------------------------------------


	ExportAllAssetByList(GetAllobjectsByExportType("export_recursive"))
	
	
	#----------------------------------------Reset data
	for x in range(20):
		scene.layers[x] = LayerVisibility[x]
	bpy.ops.object.select_all(action='DESELECT')
	for obj in UserSelected: obj.select = True #Resets previous selected object
	scene.objects.active = UserActive #Resets previous active object
	if UserActive and UserMode and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode=UserMode) #Resets previous mode
	for x, obj in enumerate(scene.objects):
		obj.hide = UserObjHide[x] #Resets previous object visibility
		obj.hide_select = UserObjHideSelect[x] #Resets previous object visibility(select)
	#----------------------------------------

def ExportForUnrealEngine():
	PrepareAndSaveDataForExport()