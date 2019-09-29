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
from . import bfu_WriteText
importlib.reload(bfu_WriteText)

from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *

from . import bfu_Utils
importlib.reload(bfu_Utils)
from .bfu_Utils import *

def ExportSingleFbxAction(originalScene, dirpath, filename, obj, targetAction, actionType):
	#Export a single action like a animation or pose


	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	if obj.animation_data is None:
		obj.animation_data_create()
	userAction = obj.animation_data.action #Save current action
	userAction_extrapolation = obj.animation_data.action_extrapolation
	userAction_blend_type = obj.animation_data.action_blend_type
	userAction_influence = obj.animation_data.action_influence


	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
		

	SelectParentAndDesiredChilds(obj)
	ApplyExportTransform(obj)

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
	oldArmatureName = RenameArmatureAsExportName(obj)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(obj),
		object_types={'ARMATURE', 'EMPTY', 'MESH'},
		use_custom_props=addon_prefs.exportWithCustomProps,
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
		bake_anim_simplify_factor=obj.SimplifyAnimForExport,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = obj.exportPrimaryBaneAxis,
		secondary_bone_axis = obj.exporSecondaryBoneAxis,	
		axis_forward = obj.exportAxisForward,
		axis_up = obj.exportAxisUp,
		bake_space_transform = False
		)

	#Reset armature name
	ResetArmatureName(obj, oldArmatureName, )
	
	ResetArmaturePose(obj)
	obj.animation_data.action = userAction #Resets previous action and NLA
	obj.animation_data.action_extrapolation = userAction_extrapolation
	obj.animation_data.action_blend_type = userAction_blend_type
	obj.animation_data.action_influence = userAction_influence
	exportTime = time.process_time()-curr_time

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = actionType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset

def ExportSingleFbxNLAAnim(originalScene, dirpath, filename, obj):
	#Export a single NLA Animation


	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()

	SelectParentAndDesiredChilds(obj)
	ApplyExportTransform(obj)

	ResetArmaturePose(obj)
	scene.frame_start += obj.StartFramesOffset
	scene.frame_end += obj.EndFramesOffset
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsExportName(obj)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(obj),
		object_types={'ARMATURE', 'EMPTY', 'MESH'},
		use_custom_props=addon_prefs.exportWithCustomProps,
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
		bake_anim_simplify_factor=obj.SimplifyAnimForExport,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = obj.exportPrimaryBaneAxis,
		secondary_bone_axis = obj.exporSecondaryBoneAxis,	
		axis_forward = obj.exportAxisForward,
		axis_up = obj.exportAxisUp,
		bake_space_transform = False
		)		
		
	ResetArmaturePose(obj)
	scene.frame_start -= obj.StartFramesOffset
	scene.frame_end -= obj.EndFramesOffset
	exportTime = time.process_time()-curr_time

	#Reset armature name
	ResetArmatureName(obj, oldArmatureName)

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "NlAnim"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleAlembicAnimation(originalScene, dirpath, filename, obj):
	#Export a single alembic animation

	scene = bpy.context.scene
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')

	SelectParentAndDesiredChilds(obj)

	scene.frame_start += obj.StartFramesOffset
	scene.frame_end += obj.EndFramesOffset
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	##Export
	bpy.ops.wm.alembic_export(
		filepath=fullpath,
		check_existing=False,
		selected=True,
		triangulate=False,
		)

	scene.frame_start -= obj.StartFramesOffset
	scene.frame_end -= obj.EndFramesOffset
	exportTime = time.process_time()-curr_time

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "Alembic"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleFbxMesh(originalScene, dirpath, filename, obj):
	#Export a single Mesh

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	
	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	
	SelectParentAndDesiredChilds(obj)
	bpy.ops.object.duplicate()
	currentObjName = []
	for objScene in scene.objects:
		currentObjName.append(objScene.name)
		
	bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
	
	for objScene in scene.objects:
		if objScene.name not in currentObjName:
			objScene.select_set(True)
			pass
			
	for objScene in bpy.context.selected_objects:
		if objScene.data is not None:
			objScene.data = objScene.data.copy()
	
	
	
	ApplyNeededModifierToSelect()
	UpdateNameHierarchy(GetAllCollisionAndSocketsObj(bpy.context.selected_objects))
	active = bpy.context.view_layer.objects.active
	
	ApplyExportTransform(active)
	

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	meshType = GetAssetType(active)

	#Set socket scale for Unreal
	for socket in GetSocketDesiredChild(active):
		socket.delta_scale*=0.01*addon_prefs.StaticSocketsImportedSize

	#Set rename temporarily the Armature as "Armature"
	if meshType == "SkeletalMesh":
		oldArmatureName = RenameArmatureAsExportName(active)

	object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'} #Default

	if meshType == "StaticMesh":
		#Dont export ARMATURE with static mesh
		object_types={'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}
	if meshType == "SkeletalMesh":
		#Dont export EMPTY with Skeletal mesh
		object_types={'ARMATURE', 'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'}
	
	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(active),
		object_types=object_types,
		use_custom_props=addon_prefs.exportWithCustomProps,
		mesh_smooth_type="FACE",
		add_leaf_bones=False,
		use_armature_deform_only=active.exportDeformOnly,
		bake_anim=False,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = active.exportPrimaryBaneAxis,
		secondary_bone_axis = active.exporSecondaryBoneAxis,	
		axis_forward = active.exportAxisForward,
		axis_up = active.exportAxisUp,
		bake_space_transform = False
		)

	#Reset armature name
	if meshType == "SkeletalMesh":
		ResetArmatureName(active, oldArmatureName)
		
	
	bpy.ops.object.delete()
	
	exportTime = time.process_time()-curr_time

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = meshType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleFbxCamera(originalScene, dirpath, filename, obj):
	#Export single camera

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilename(filename)
	if obj.type != 'CAMERA':
		return;
	curr_time = time.process_time()
	if	bpy.ops.object.mode_set.poll():
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
		global_scale=GetObjExportScale(obj),
		object_types={'CAMERA'},
		use_custom_props=addon_prefs.exportWithCustomProps,
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(obj),
		bake_anim_simplify_factor=obj.SimplifyAnimForExport,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = obj.exportPrimaryBaneAxis,
		secondary_bone_axis = obj.exporSecondaryBoneAxis,	
		axis_forward = obj.exportAxisForward,
		axis_up = obj.exportAxisUp,
		bake_space_transform = False
		)

	#Reset camera scale
	obj.delta_scale*=100

	exportTime = time.process_time()-curr_time

	MyAsset = originalScene.UnrealExportedAssetsList.add()
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
	AdditionalTrack = bfu_WriteText.WriteSingleCameraAdditionalTrack(obj)
	return bfu_WriteText.ExportSingleText(AdditionalTrack, absdirpath, filename)

def ExportSingleAdditionalParameterMesh(dirpath, filename, obj):
	#Export additional parameter from static and skeletal mesh track for ue4
	#SocketsList

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	AdditionalTrack = bfu_WriteText.WriteSingleMeshAdditionalParameter(obj)
	return bfu_WriteText.ExportSingleConfigParser(AdditionalTrack, absdirpath, filename)

def ExportAllAssetByList(originalScene, targetobjects, targetActionName):
	#Export all objects that need to be exported from a list
	
	

	if len(targetobjects) < 1:
		return

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
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
				ExportSingleFbxCamera(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					if scene.text_AdditionalData == True and addon_prefs.UseGeneratedScripts == True:
						ExportSingleAdditionalTrackCamera(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalTrack.ini"), obj)
				scene.frame_start = UserStartFrame #Resets previous start frame
				scene.frame_end = UserEndFrame #Resets previous end frame
				UpdateProgress()

			#StaticMesh
			if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				ExportSingleFbxMesh(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					if scene.text_AdditionalData == True and addon_prefs.UseGeneratedScripts == True:
						ExportSingleAdditionalParameterMesh(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalParameter.ini"), obj)
				UpdateProgress()
			
			#SkeletalMesh
			if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
				ExportSingleFbxMesh(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if scene.text_AdditionalData == True and addon_prefs.UseGeneratedScripts == True:
					ExportSingleAdditionalParameterMesh(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalParameter.ini"), obj)
				UpdateProgress()

			#Alembic
			if GetAssetType(obj) == "Alembic" and scene.alembic_export:
				ExportSingleAlembicAnimation(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj, ".abc"), obj)
				UpdateProgress()
				
			#Action animation
			if GetAssetType(obj) == "SkeletalMesh" and obj.visible_get() == True:
				animExportDir = os.path.join( GetObjExportDir(obj), scene.anim_subfolder_name )
				for action in GetActionToExport(obj):
					if action.name in targetActionName:
						animType = GetActionType(action)
						
						#Action
						if animType == "Action" and bpy.context.scene.anin_export == True:
							UserStartFrame = scene.frame_start #Save current start frame
							UserEndFrame = scene.frame_end #Save current end frame
							ExportSingleFbxAction(originalScene, animExportDir, GetActionExportFileName(obj, action), obj, action, "Action")
							scene.frame_start = UserStartFrame #Resets previous start frame
							scene.frame_end = UserEndFrame #Resets previous end frame
							UpdateProgress()
						
						#pose
						if animType == "Pose" and bpy.context.scene.anin_export == True:
							UserStartFrame = scene.frame_start #Save current start frame
							UserEndFrame = scene.frame_end #Save current end frame
							ExportSingleFbxAction(originalScene, animExportDir, GetActionExportFileName(obj, action), obj, action, "Pose")
							scene.frame_start = UserStartFrame #Resets previous start frame
							scene.frame_end = UserEndFrame #Resets previous end frame
							UpdateProgress()

				#NLA animation
				if bpy.context.scene.anin_export == True:
					if obj.ExportNLA == True:
						scene.frame_end +=1
						ExportSingleFbxNLAAnim(originalScene, animExportDir, GetNLAExportFileName(obj), obj)
						scene.frame_end -=1


	wm.progress_end()


def PrepareAndSaveDataForExport():

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	view_layer = bpy.context.view_layer
	#----------------------------------------Save data
	UserObjHideViewport = []
	UserObjHideSelect = []
	
	baseActionName = []
	for action in bpy.data.actions:
		baseActionName.append(action.name)
	
	copyScene = bpy.context.scene.copy()
	copyScene.name = "ue4-export_Temp"
	bpy.context.window.scene = copyScene
	UserActive = bpy.context.active_object #Save current active object
	if UserActive and UserActive.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		UserMode = UserActive.mode #Save current mode
		bpy.ops.object.mode_set(mode='OBJECT')
	
	if addon_prefs.revertExportPath == True:
		RemoveFolderTree(bpy.path.abspath(scene.export_static_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_skeletal_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_alembic_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_camera_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_other_file_path))

	list = []
	for Asset in GetFinalAssetToExport():
		if Asset.obj in GetAllobjectsByExportType("export_recursive"):
			if Asset.obj not in list:
				list.append(Asset.obj)
	ExportAllAssetByList(
	originalScene = scene,
	targetobjects = list,
	targetActionName = baseActionName,
	)
	
	bpy.context.window.scene = scene
	bpy.data.scenes.remove(copyScene)
	
	for action in bpy.data.actions:
		if action.name not in baseActionName:
			bpy.data.actions.remove(action)



def ExportForUnrealEngine():
	PrepareAndSaveDataForExport()