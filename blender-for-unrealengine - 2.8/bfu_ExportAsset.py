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

import importlib
from . import bfu_writetext
importlib.reload(bfu_writetext)

from . import bfu_basics
importlib.reload(bfu_basics)
from .bfu_basics import *

from . import bfu_utils
importlib.reload(bfu_utils)
from .bfu_utils import *
	
def ExportSingleFbxAction(dirpath, filename, obj, targetAction, actionType):
	#Export a single action like a animation or pose

	
	scene = bpy.context.scene
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	if obj.animation_data is None:
		obj.animation_data_create()
	userAction = obj.animation_data.action #Save current action
	userAction_extrapolation = obj.animation_data.action_extrapolation
	userAction_blend_type = obj.animation_data.action_blend_type
	userAction_influence = obj.animation_data.action_influence

	
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	ResetArmaturePose(obj)
	if (scene.is_nla_tweakmode == True):
		obj.animation_data.use_tweak_mode = False #animation_data.action is ReadOnly with tweakmode in 2.8
	obj.animation_data.action = targetAction #Apply desired action and reset NLA
	obj.animation_data.action_extrapolation = 'HOLD' 
	obj.animation_data.action_blend_type = 'REPLACE'
	obj.animation_data.action_influence = 1
	scene.frame_start = GetDesiredActionStartEndTime(obj, targetAction)[0]
	scene.frame_end = GetDesiredActionStartEndTime(obj, targetAction)[1]

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	
	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsArmature(obj)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=obj.exportGlobalScale,
		object_types={'ARMATURE', 'MESH'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
		bake_anim_simplify_factor=obj.SimplifyAnimForExport
		)
		
	#Reset armature name
	ResetArmatureName(obj, oldArmatureName)
		
	obj.location = originalLoc #Resets previous object location
	ResetArmaturePose(obj)
	obj.animation_data.action = userAction #Resets previous action and NLA
	obj.animation_data.action_extrapolation = userAction_extrapolation
	obj.animation_data.action_blend_type = userAction_blend_type
	obj.animation_data.action_influence = userAction_influence
	exportTime = time.process_time()-curr_time
	
	MyAsset = scene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = actionType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset
	
def ExportSingleFbxNLAAnim(dirpath, filename, obj):
	#Export a single NLA Animation

	
	scene = bpy.context.scene
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	ResetArmaturePose(obj)
	if obj.AddOneAdditionalFramesAtTheEnd == True:
		scene.frame_end += 1
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	
	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsArmature(obj)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=obj.exportGlobalScale,
		object_types={'ARMATURE', 'MESH'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
		bake_anim_simplify_factor=obj.SimplifyAnimForExport
		)
	obj.location = originalLoc #Resets previous object location
	ResetArmaturePose(obj)
	if obj.AddOneAdditionalFramesAtTheEnd == True:
		scene.frame_end -= 1
	exportTime = time.process_time()-curr_time
	
	#Reset armature name
	ResetArmatureName(obj, oldArmatureName)
	
	MyAsset = scene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "NlAnim"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleFbxMesh(dirpath, filename, obj):
	#Export a single Mesh
	
	scene = bpy.context.scene
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	if  bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save current object location
	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	meshType = GetAssetType(obj)

	#Set socket scale for Unreal
	for socket in GetSocketDesiredChild(obj):
		socket.delta_scale*=0.01
		
	#Set rename temporarily the Armature as "Armature"
	if meshType == "SkeletalMesh":
		oldArmatureName = RenameArmatureAsArmature(obj)

	object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'} #Default
	
	if meshType == "StaticMesh":
		#Dont export ARMATURE with static mesh
		object_types={'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}
	if meshType == "SkeletalMesh":
		#Dont export EMPTY with Skeletal mesh
		object_types={'ARMATURE', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'}
	
	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=obj.exportGlobalScale,
		object_types=object_types,
		mesh_smooth_type="FACE",
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=False
		)
	
	obj.location = originalLoc #Resets previous object location
	exportTime = time.process_time()-curr_time
	
	#Reset socket scale
	for socket in GetSocketDesiredChild(obj):
		socket.delta_scale*=100
		
	#Reset armature name
	if meshType == "SkeletalMesh":
		ResetArmatureName(obj, oldArmatureName)
	
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
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj
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
		use_selection=True,
		global_scale=obj.exportGlobalScale,
		object_types={'CAMERA'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
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
	AdditionalTrack = bfu_writetext.WriteSingleCameraAdditionalTrack(obj)
	return bfu_writetext.ExportSingleText(AdditionalTrack, absdirpath, filename)
	
def ExportSingleAdditionalParameterMesh(dirpath, filename, obj):
	#Export additional parameter from static and skeletal mesh track for ue4
	#SocketsList
	
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	AdditionalTrack = bfu_writetext.WriteSingleMeshAdditionalParameter(obj)
	return bfu_writetext.ExportSingleConfigParser(AdditionalTrack, absdirpath, filename)
	
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
				UserStartFrame = scene.frame_start #Save current start frame
				UserEndFrame = scene.frame_end #Save current end frame
				ExportSingleFbxCamera(GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					ExportSingleAdditionalTrackCamera(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalTrack.ini"), obj)
				scene.frame_start = UserStartFrame #Resets previous start frame
				scene.frame_end = UserEndFrame #Resets previous end frame
				UpdateProgress()
			
			#StaticMesh
			if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				ExportSingleFbxMesh(GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					ExportSingleAdditionalParameterMesh(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalParameter.ini"), obj)
				UpdateProgress()
			
			#SkeletalMesh
			if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
					ExportSingleFbxMesh(GetObjExportDir(obj), GetObjExportFileName(obj), obj)
					ExportSingleAdditionalParameterMesh(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalParameter.ini"), obj)
					UpdateProgress()
					
			#Action animation
			if GetAssetType(obj) == "SkeletalMesh" and obj.visible_get() == True:	
				animExportDir = os.path.join( GetObjExportDir(obj), scene.anim_subfolder_name )
				
				for action in GetActionToExport(obj):
										
					animType = GetActionType(action)
									
					#Action
					if animType == "Action" and bpy.context.scene.anin_export == True:
						UserStartFrame = scene.frame_start #Save current start frame
						UserEndFrame = scene.frame_end #Save current end frame
						ExportSingleFbxAction(animExportDir, GetActionExportFileName(obj, action), obj, action, "Action")
						scene.frame_start = UserStartFrame #Resets previous start frame
						scene.frame_end = UserEndFrame #Resets previous end frame
						UpdateProgress()
						
					#pose
					if animType == "Pose" and bpy.context.scene.anin_export == True:
						UserStartFrame = scene.frame_start #Save current start frame
						UserEndFrame = scene.frame_end #Save current end frame
						ExportSingleFbxAction(animExportDir, GetActionExportFileName(obj, action), obj, action, "Pose")
						scene.frame_start = UserStartFrame #Resets previous start frame
						scene.frame_end = UserEndFrame #Resets previous end frame
						UpdateProgress()
						
				#NLA animation
				if bpy.context.scene.anin_export == True:
					if obj.ExportNLA == True:
						scene.frame_end +=1
						ExportSingleFbxNLAAnim(animExportDir, GetNLAExportFileName(obj), obj)
						scene.frame_end -=1
						
				
	wm.progress_end()	
	

def PrepareAndSaveDataForExport():

	scene = bpy.context.scene
	view_layer = bpy.context.view_layer
	#----------------------------------------Save data
	UserObjHideViewport = []
	UserObjHideSelect = []
	
	
	for obj in scene.objects: #Save previous object visibility
		UserObjHideViewport.append(obj.hide_viewport)
		UserObjHideSelect.append(obj.hide_select)
		obj.hide_viewport = False
		obj.hide_select = False
		
	UsedViewLayerCollectionHideViewport = []
	UsedCollectionHideViewport = []
	UsedCollectionHideselect = []
	for collection in bpy.data.collections: #Save previous collections visibility
		try:
			UsedViewLayerCollectionHideViewport.append(view_layer.layer_collection.children[collection.name].hide_viewport)
		except:
			print(collection.name," not found in view_layer.layer_collection")
			pass
		UsedCollectionHideViewport.append(collection.hide_viewport)
		UsedCollectionHideselect.append(collection.hide_select)
		SetCollectionUse(collection)

	if obj is None:
		view_layer.objects.active = bpy.data.objects[0]

	UserActive = bpy.context.active_object #Save current active object
	UserMode = None 
	if UserActive and UserActive.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		UserMode = UserActive.mode #Save current mode
		bpy.ops.object.mode_set(mode='OBJECT')
	UserSelected = bpy.context.selected_objects #Save current selected objects
	#----------------------------------------


	ExportAllAssetByList(GetAllobjectsByExportType("export_recursive"))
	
	
	#----------------------------------------Reset data
	for x, collection in enumerate(bpy.data.collections):
		try:
			view_layer.layer_collection.children[collection.name].hide_viewport = UsedViewLayerCollectionHideViewport[x]
		except:
			print(collection.name," not found in view_layer.layer_collection")
			pass
		collection.hide_viewport = UsedCollectionHideViewport[x]
		collection.hide_select = UsedCollectionHideselect[x]
		


	bpy.ops.object.select_all(action='DESELECT')
	
	for obj in UserSelected: obj.select_set(True) #Resets previous selected object
	view_layer.objects.active = UserActive #Resets previous active object
	if UserActive and UserMode and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode=UserMode) #Resets previous mode
	
	for x, obj in enumerate(scene.objects):
		obj.hide_viewport = UserObjHideViewport[x] #Resets previous object visibility
		obj.hide_select = UserObjHideSelect[x] #Resets previous object visibility(select)
	#----------------------------------------

def ExportForUnrealEngine():
	PrepareAndSaveDataForExport()
