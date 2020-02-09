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

def DuplicateSelect():
	scene = bpy.context.scene
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

def SetSocketsExportTransform(obj):
	#Set socket scale for Unreal
	
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	for socket in GetSocketDesiredChild(obj):
		socket.delta_scale *= addon_prefs.staticSocketsImportedSize
		if addon_prefs.staticSocketsAdd90X == True:
			savedScale = socket.scale.copy()
			AddMat = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
			socket.matrix_world = socket.matrix_world @ AddMat
			socket.scale = savedScale
	
def AddSocketsTempName(obj):
	#Add _UE4Socket_TempName at end
	
	for socket in GetSocketDesiredChild(obj):
		socket.name += "_UE4Socket_TempName"
		
def RemoveDuplicatedSocketsTempName(obj):
	#Remove _UE4Socket_TempName at end
	
	for socket in GetSocketDesiredChild(obj):
		ToRemove = "_UE4Socket_TempName.xxx"
		socket.name = socket.name[:-len(ToRemove)]
	
def RemoveSocketsTempName(obj):
	#Remove _UE4Socket_TempName at end
	
	for socket in GetSocketDesiredChild(obj):
		ToRemove = "_UE4Socket_TempName"
		socket.name = socket.name[:-len(ToRemove)]
		

	

def ExportSingleFbxAction(originalScene, dirpath, filename, obj, targetAction, actionType):
	'''
	#####################################################
			#SKELETAL ACTION
	#####################################################
	'''
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
	DuplicateSelect()
	
	BaseTransform = obj.matrix_world.copy()
	active = bpy.context.view_layer.objects.active
	
	ApplyExportTransform(active)
	rootScale = addon_prefs.SkeletonRootBoneScale
	savedUnitLength = ApplySkelatalExportScale(active, rootScale)
	
	RescaleActionCurve(targetAction, 100*rootScale)
	ResetArmaturePose(active)
	RescaleStretchLengthConsraints(active, 100*rootScale)
	

	if (scene.is_nla_tweakmode == True):
		active.animation_data.use_tweak_mode = False #animation_data.action is ReadOnly with tweakmode in 2.8
	active.animation_data.action = targetAction #Apply desired action and reset NLA
	active.animation_data.action_extrapolation = 'HOLD'
	active.animation_data.action_blend_type = 'REPLACE'
	active.animation_data.action_influence = 1
	scene.frame_start = GetDesiredActionStartEndTime(active, targetAction)[0]
	scene.frame_end = GetDesiredActionStartEndTime(active, targetAction)[1]
	
	
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	
	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsExportName(active)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(active),
		object_types={'ARMATURE', 'EMPTY', 'MESH'},
		use_custom_props=addon_prefs.exportWithCustomProps,
		mesh_smooth_type="FACE",
		add_leaf_bones=False,
		use_armature_deform_only=active.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(active),
		bake_anim_simplify_factor=active.SimplifyAnimForExport,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = active.exportPrimaryBaneAxis,
		secondary_bone_axis = active.exporSecondaryBoneAxis,	
		axis_forward = active.exportAxisForward,
		axis_up = active.exportAxisUp,
		bake_space_transform = False
		)

	

	#Reset armature name
	ResetArmatureName(active, oldArmatureName, )
	
	ResetArmaturePose(obj)
		
	obj.animation_data.action = userAction #Resets previous action and NLA
	obj.animation_data.action_extrapolation = userAction_extrapolation
	obj.animation_data.action_blend_type = userAction_blend_type
	obj.animation_data.action_influence = userAction_influence
	
	
	#Reset Transform
	obj.matrix_world = BaseTransform
	bpy.context.scene.unit_settings.scale_length = savedUnitLength
	
	#Reset Curve
	RescaleActionCurve(targetAction, 1/(100*rootScale))

	bpy.ops.object.delete()
	
	exportTime = time.process_time()-curr_time
	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = actionType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset

def ExportSingleFbxNLAAnim(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#NLA ANIMATION
	#####################################################
	'''
	#Export a single NLA Animation

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()

	SelectParentAndDesiredChilds(obj)
	DuplicateSelect()
	BaseTransform = obj.matrix_world.copy()
	active = bpy.context.view_layer.objects.active
	
	ApplyExportTransform(active)
	rootScale = addon_prefs.SkeletonRootBoneScale
	savedUnitLength = ApplySkelatalExportScale(active, rootScale)

	RescaleAllActionCurve(100*rootScale)
	ResetArmaturePose(active)
	RescaleStretchLengthConsraints(active, 100*rootScale)
	
	scene.frame_start += active.StartFramesOffset
	scene.frame_end += active.EndFramesOffset
	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsExportName(active)

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(active),
		object_types={'ARMATURE', 'EMPTY', 'MESH'},
		use_custom_props=addon_prefs.exportWithCustomProps,
		add_leaf_bones=False,
		use_armature_deform_only=active.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=GetAnimSample(active),
		bake_anim_simplify_factor=active.SimplifyAnimForExport,
		use_metadata=addon_prefs.exportWithMetaData,
		primary_bone_axis = active.exportPrimaryBaneAxis,
		secondary_bone_axis = active.exporSecondaryBoneAxis,	
		axis_forward = active.exportAxisForward,
		axis_up = active.exportAxisUp,
		bake_space_transform = False
		)		
		
	ResetArmaturePose(active)
	scene.frame_start -= active.StartFramesOffset
	scene.frame_end -= active.EndFramesOffset
	exportTime = time.process_time()-curr_time

	#Reset armature name
	ResetArmatureName(active, oldArmatureName)
	
	ResetArmaturePose(obj)
	
	#Reset Transform
	obj.matrix_world = BaseTransform
	bpy.context.scene.unit_settings.scale_length = savedUnitLength
	
	#Reset Curve
	RescaleAllActionCurve(1/(100*rootScale))

	bpy.ops.object.delete()

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = "NlAnim"
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset



def ExportSingleAlembicAnimation(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#ALEMBIC ANIMATION
	#####################################################
	'''
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


def ExportSingleStaticMeshCollection(originalScene, dirpath, filename, collectionName):
	'''
	#####################################################
			#COLLECTION
	#####################################################
	'''
	#create collection and export it
	obj = bpy.data.objects.new( "EmptyCollectionForUnrealExport_Temp", None )
	bpy.context.scene.collection.objects.link( obj )
	obj.instance_type = 'COLLECTION'
	obj.instance_collection = bpy.data.collections[collectionName]
	ExportSingleStaticMesh(originalScene, dirpath, filename, obj)
	
	#Remove the created collection
	obj.select_set(True)
	bpy.ops.object.delete()  
	
	
def ExportSingleStaticMesh(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#STATIC MESH
	#####################################################
	'''
	#Export a single Mesh

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	
	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	
	SelectParentAndDesiredChilds(obj)
	AddSocketsTempName(obj)
	DuplicateSelect()	
	ApplyNeededModifierToSelect()

	active = bpy.context.view_layer.objects.active
	

	if addon_prefs.correctExtremUVScale == True:
		bpy.ops.object.mode_set(mode = 'EDIT')
		CorrectExtremeUV(2)
		bpy.ops.object.mode_set(mode = 'OBJECT')
		
	UpdateNameHierarchy(GetAllCollisionAndSocketsObj(bpy.context.selected_objects))
	
	
	ApplyExportTransform(active)
	

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	meshType = GetAssetType(active)
	
	SetSocketsExportTransform(active)
	RemoveDuplicatedSocketsTempName(active)
		
	savedUnitLength = bpy.context.scene.unit_settings.scale_length
	bpy.context.scene.unit_settings.scale_length = 1

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(active),
		object_types={'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
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
	
	bpy.context.scene.unit_settings.scale_length = savedUnitLength
	
	
	bpy.ops.object.delete()
	RemoveSocketsTempName(obj)
		

	
	
	exportTime = time.process_time()-curr_time

	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = meshType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset
	
def ExportSingleSkeletalMesh(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#SKELETAL MESH
	#####################################################
	'''
	#Export a single Mesh




	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	filename = ValidFilenameForUnreal(filename)
	curr_time = time.process_time()
	
	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = 'OBJECT')
	
	SelectParentAndDesiredChilds(obj)
	AddSocketsTempName(obj)
	DuplicateSelect()	
	
	ApplyNeededModifierToSelect()
	
	
	
	if addon_prefs.correctExtremUVScale == True:
		activeArmature = bpy.context.view_layer.objects.active
		if GoToMeshEditMode() == True:
			CorrectExtremeUV(2)
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.context.view_layer.objects.active = activeArmature
		
		
		
		
	UpdateNameHierarchy(GetAllCollisionAndSocketsObj(bpy.context.selected_objects))
	active = bpy.context.view_layer.objects.active
	
	ApplyExportTransform(active)
	rootScale = addon_prefs.SkeletonRootBoneScale
	savedUnitLength = ApplySkelatalExportScale(active, rootScale)


	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )
	meshType = GetAssetType(active)
			
	SetSocketsExportTransform(active)
	RemoveDuplicatedSocketsTempName(active)


	#Set rename temporarily the Armature as "Armature"
	oldArmatureName = RenameArmatureAsExportName(active)
	
	RemoveAllConsraints(active)
	bpy.context.object.data.pose_position = 'REST'
	
	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		use_selection=True,
		global_scale=GetObjExportScale(active),
		object_types={'ARMATURE', 'EMPTY', 'CAMERA', 'LIGHT', 'MESH', 'OTHER'},
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
	ResetArmatureName(active, oldArmatureName)
	
	bpy.context.scene.unit_settings.scale_length = savedUnitLength
	
	bpy.ops.object.delete()
	
	RemoveSocketsTempName(obj)
	
	exportTime = time.process_time()-curr_time
	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = meshType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset


def ExportSingleFbxCamera(originalScene, dirpath, filename, obj):
	'''
	#####################################################
			#CAMERA
	#####################################################
	'''
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
