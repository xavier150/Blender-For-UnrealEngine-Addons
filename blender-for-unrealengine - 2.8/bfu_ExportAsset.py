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

from . import bfu_ExportAssetsByType
importlib.reload(bfu_ExportAssetsByType)
from .bfu_ExportAssetsByType import *


def ExportAllAssetByList(originalScene, targetobjects, targetActionName, targetcollection):
	#Export all objects that need to be exported from a list
	
	
	if len(targetobjects) < 1 and len(targetcollection) < 1 :
		return

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	wm = bpy.context.window_manager
	wm.progress_begin(0, len(GetFinalAssetToExport()))
	

	def UpdateProgress():
		wm.progress_update(len(scene.UnrealExportedAssetsList))
	UpdateProgress()
	
	if scene.static_collection_export:
		for col in GetCollectionToExport(originalScene):
			if col in targetcollection:
				#StaticMesh collection
				ExportSingleStaticMeshCollection(originalScene, GetCollectionExportDir(), GetCollectionExportFileName(col), col)
					#if scene.text_AdditionalData == True and addon_prefs.useGeneratedScripts == True:
						#ExportSingleAdditionalParameterMesh(GetCollectionExportDir(), GetCollectionExportFileName(col,"_AdditionalParameter.ini"), col)
				UpdateProgress()
	
	for obj in targetobjects:

		if obj.ExportEnum == "export_recursive":

			#Camera
			if GetAssetType(obj) == "Camera" and scene.camera_export:
				UserStartFrame = scene.frame_start #Save current start frame
				UserEndFrame = scene.frame_end #Save current end frame
				ExportSingleFbxCamera(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					if scene.text_AdditionalData == True and addon_prefs.useGeneratedScripts == True:
						ExportSingleAdditionalTrackCamera(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalTrack.ini"), obj)
				scene.frame_start = UserStartFrame #Resets previous start frame
				scene.frame_end = UserEndFrame #Resets previous end frame
				UpdateProgress()

			#StaticMesh
			if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				ExportSingleStaticMesh(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if obj.ExportAsLod == False:
					if scene.text_AdditionalData == True and addon_prefs.useGeneratedScripts == True:
						ExportSingleAdditionalParameterMesh(GetObjExportDir(obj), GetObjExportFileName(obj,"_AdditionalParameter.ini"), obj)
				UpdateProgress()
			
			#SkeletalMesh
			if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
				ExportSingleSkeletalMesh(originalScene, GetObjExportDir(obj), GetObjExportFileName(obj), obj)
				if scene.text_AdditionalData == True and addon_prefs.useGeneratedScripts == True:
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

	#Move to global view
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			space = area.spaces[0]
			if space.local_view: #check if using local view
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region} #override context
						bpy.ops.view3d.localview(override) #switch to global view

	#----------------------------------------Save data
	
	baseActionName = []
	for action in bpy.data.actions:
		baseActionName.append(action.name)
		
	baseCollectionName = []
	for collection in bpy.data.collections:
		baseCollectionName.append(collection.name)
	
	UserObjHideSelect = []
	for object in bpy.data.objects:
		UserObjHideSelect.append((object.name, object.hide_select))
		object.hide_select = False
		
	UserObjHideViewport = []
	for object in bpy.data.objects:
		UserObjHideViewport.append((object.name, object.hide_viewport))
		object.hide_viewport = False
	
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
	targetcollection = baseCollectionName,
	)
	
	bpy.context.window.scene = scene
	bpy.data.scenes.remove(copyScene)
	
	#Clean actions
	for action in bpy.data.actions:
		if action.name not in baseActionName:
			bpy.data.actions.remove(action)
			
	#Reset hide select
	for object in UserObjHideSelect:
		if object[0] in bpy.data.objects:
			bpy.data.objects[object[0]].hide_select = object[1]
		else:
			print("/!\ "+object[0]+" not found in bpy.data.objects")
			
	#Reset hide viewport
	for object in UserObjHideViewport:
		if object[0] in bpy.data.objects:
			bpy.data.objects[object[0]].hide_viewport = object[1]
		else:
			print("/!\ "+object[0]+" not found in bpy.data.objects")
		

def ExportForUnrealEngine():
	PrepareAndSaveDataForExport()