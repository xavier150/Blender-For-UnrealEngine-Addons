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

from . import bfu_ExportSingleAlembicAnimation
importlib.reload(bfu_ExportSingleAlembicAnimation)
from .bfu_ExportSingleAlembicAnimation import *

from . import bfu_ExportSingleFbxAction
importlib.reload(bfu_ExportSingleFbxAction)
from .bfu_ExportSingleFbxAction import *

from . import bfu_ExportSingleFbxCamera
importlib.reload(bfu_ExportSingleFbxCamera)
from .bfu_ExportSingleFbxCamera import *

from . import bfu_ExportSingleFbxNLAAnim
importlib.reload(bfu_ExportSingleFbxNLAAnim)
from .bfu_ExportSingleFbxNLAAnim import *

from . import bfu_ExportSingleSkeletalMesh
importlib.reload(bfu_ExportSingleSkeletalMesh)
from .bfu_ExportSingleSkeletalMesh import *

from . import bfu_ExportSingleStaticMesh
importlib.reload(bfu_ExportSingleStaticMesh)
from .bfu_ExportSingleStaticMesh import *

from . import bfu_ExportSingleStaticMeshCollection
importlib.reload(bfu_ExportSingleStaticMeshCollection)
from .bfu_ExportSingleStaticMeshCollection import *




def ExportAllAssetByList(originalScene, targetobjects, targetActionName, targetcollection):
	#Export all objects that need to be exported from a list
	
	if len(targetobjects) < 1 and len(targetcollection) < 1 :
		return

	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	
	s = CounterStart()
	
	NumberAssetToExport = len(GetFinalAssetToExport())

	def UpdateProgress(time = None):
		update_progress("Export assets", len(originalScene.UnrealExportedAssetsList)/NumberAssetToExport, time)
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


	UpdateProgress(CounterEnd(s))


def PrepareAndSaveDataForExport():
	
	scene = bpy.context.scene
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences

	
	MoveToGlobalView()

	#----------------------------------------Save data
	#This can take time
	
	actionNames = []
	for action in bpy.data.actions:
		actionNames.append(action.name)
		
	collectionNames = []
	for collection in bpy.data.collections:
		collectionNames.append(collection.name)
	
	UserObjHide = []
	for object in bpy.data.objects:
		UserObjHide.append((object.name, object.hide_select, object.hide_viewport))
		if object.hide_select == True:
			object.hide_select = False	
		if object.hide_viewport == True:
			object.hide_viewport = False

	UserColHide = []
	for col in bpy.data.collections:
		UserColHide.append((col.name, col.hide_select, col.hide_viewport))
		if col.hide_select == True:
			col.hide_select = False	
		if col.hide_viewport == True:
			col.hide_viewport = False	
	
	UserVLayerHide = []
	for vlayer in bpy.context.scene.view_layers:	
		for childCol in vlayer.layer_collection.children:	
			UserVLayerHide.append((vlayer.name, childCol.name, childCol.exclude, childCol.hide_viewport))
			if childCol.exclude == True:
				childCol.exclude = False
			if childCol.hide_viewport == True:
				childCol.hide_viewport = False
	
	copyScene = bpy.context.scene.copy()
	copyScene.name = "ue4-export_Temp"
	bpy.context.window.scene = copyScene #Switch the scene but can take time

	UserActive = bpy.context.active_object #Save current active object
	if	bpy.ops.object.mode_set.poll():
		UserMode = UserActive.mode #Save current mode
	else:
		UserMode = None
	if UserActive and UserActive.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	
	if addon_prefs.revertExportPath == True:
		RemoveFolderTree(bpy.path.abspath(scene.export_static_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_skeletal_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_alembic_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_camera_file_path))
		RemoveFolderTree(bpy.path.abspath(scene.export_other_file_path))

	
	assetList = [] #Do a simple lit of objects to export
	for Asset in GetFinalAssetToExport():
		if Asset.obj in GetAllobjectsByExportType("export_recursive"):
			if Asset.obj not in assetList:
				assetList.append(Asset.obj)
	
		
	
	ExportAllAssetByList(
	originalScene = scene,
	targetobjects = assetList,
	targetActionName = actionNames,
	targetcollection = collectionNames,
	)
	
	bpy.context.window.scene = scene
	bpy.data.scenes.remove(copyScene)
	
	#UserActive = bpy.context.active_object #Save current active object
	if UserMode:
		bpy.ops.object.mode_set(mode=UserMode)
	
	#Clean actions
	for action in bpy.data.actions:
		if action.name not in actionNames:
			bpy.data.actions.remove(action)
			
	#Reset hide and select (bpy.data.objects)
	for object in UserObjHide:
		if object[0] in bpy.data.objects:
			if bpy.data.objects[object[0]].hide_select != object[1]:
				bpy.data.objects[object[0]].hide_select = object[1]
			if bpy.data.objects[object[0]].hide_select != object[2]:
				bpy.data.objects[object[0]].hide_viewport = object[2]
			pass
		else:
			print("/!\ "+object[0]+" not found in bpy.data.objects")	
			
	#Reset hide and select (collections)
	for col in UserColHide:
		if col[0] in bpy.data.collections:
			if bpy.data.collections[col[0]].hide_select != col[1]:
				bpy.data.collections[col[0]].hide_select = col[1]
			if bpy.data.collections[col[0]].hide_select != col[2]:
				bpy.data.collections[col[0]].hide_viewport = col[2]
			pass
		else:
			print("/!\ "+col[0]+" not found in bpy.data.collections")
		
	#Reset hide in and viewport (collections)
	for childCol in UserVLayerHide:
		if bpy.context.scene.view_layers[childCol[0]].layer_collection.children[childCol[1]].exclude != childCol[2]:
			bpy.context.scene.view_layers[childCol[0]].layer_collection.children[childCol[1]].exclude = childCol[2]		
		if bpy.context.scene.view_layers[childCol[0]].layer_collection.children[childCol[1]].hide_viewport != childCol[3]:
			bpy.context.scene.view_layers[childCol[0]].layer_collection.children[childCol[1]].hide_viewport = childCol[3]


def ExportForUnrealEngine():
	PrepareAndSaveDataForExport()