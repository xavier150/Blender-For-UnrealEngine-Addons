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

from . import bfu_ExportUtils
importlib.reload(bfu_ExportUtils)
from .bfu_ExportUtils import *

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
	s = CounterStart()
	
	if obj.animation_data is None:
		obj.animation_data_create()
	userAction = obj.animation_data.action #Save current action
	userAction_extrapolation = obj.animation_data.action_extrapolation
	userAction_blend_type = obj.animation_data.action_blend_type
	userAction_influence = obj.animation_data.action_influence


	if	bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
		
	
	SelectParentAndDesiredChilds(obj)
	DuplicateSelectForExport()

	BaseTransform = obj.matrix_world.copy()
	active = bpy.context.view_layer.objects.active
	if active.ExportAsProxy == True:
		ApplyProxyData(active)	
		
	scene.frame_start = GetDesiredActionStartEndTime(active, targetAction)[0]
	scene.frame_end = GetDesiredActionStartEndTime(active, targetAction)[1]

	active.animation_data.action = targetAction #Apply desired action

	if addon_prefs.bakeArmatureAction == True:
		BakeArmatureAnimation(active, scene.frame_start, scene.frame_end)
	
	ApplyExportTransform(active)
	
	#This will recale the rig and unit scale to get a root bone egal to 1
	ShouldRescaleRig = GetShouldRescaleRig()
	if ShouldRescaleRig == True:
	
		rrf = GetRescaleRigFactor() #rigRescaleFactor
		savedUnitLength = bpy.context.scene.unit_settings.scale_length
		bpy.context.scene.unit_settings.scale_length *= 1/rrf
		oldScale = active.scale.z
		ApplySkeletalExportScale(active, rrf)
		RescaleAllActionCurve(rrf*oldScale)
		for selected in bpy.context.selected_objects:
			if selected.type == "MESH":
				RescaleShapeKeysCurve(selected, 1/rrf)
		RescaleSelectCurveHook(1/rrf)
		ResetArmaturePose(active)
		RescaleRigConsraints(active, rrf)
		
		
	if (scene.is_nla_tweakmode == True):
		active.animation_data.use_tweak_mode = False #animation_data.action is ReadOnly with tweakmode in 2.8

	if addon_prefs.ignoreNLAForAction == True: #Reset NLA
		active.animation_data.action_extrapolation = 'HOLD'
		active.animation_data.action_blend_type = 'REPLACE'
		active.animation_data.action_influence = 1
		
	
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
	if addon_prefs.ignoreNLAForAction == True:
		obj.animation_data.action_extrapolation = userAction_extrapolation
		obj.animation_data.action_blend_type = userAction_blend_type
		obj.animation_data.action_influence = userAction_influence
	
	
	#Reset Transform
	obj.matrix_world = BaseTransform
	
	##This will recale the rig and unit scale to get a root bone egal to 1
	if ShouldRescaleRig == True:
		#Reset Curve an unit
		bpy.context.scene.unit_settings.scale_length = savedUnitLength
		RescaleAllActionCurve(1/(rrf*oldScale))

	CleanDeleteObjects(bpy.context.selected_objects)
	
	exportTime = CounterEnd(s)
	MyAsset = originalScene.UnrealExportedAssetsList.add()
	MyAsset.assetName = filename
	MyAsset.assetType = actionType
	MyAsset.exportPath = absdirpath
	MyAsset.exportTime = exportTime
	MyAsset.object = obj
	return MyAsset