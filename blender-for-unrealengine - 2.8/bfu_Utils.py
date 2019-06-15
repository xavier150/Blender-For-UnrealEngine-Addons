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
import fnmatch

import importlib
from . import bfu_Basics
importlib.reload(bfu_Basics)
from .bfu_Basics import *



def GetAllobjectsByExportType(exportType):
	#Find all objects with a specific ExportEnum property

	targetObj = []
	for obj in bpy.context.scene.objects:
		prop = obj.ExportEnum
		if prop == exportType:
			targetObj.append(obj)
	return(targetObj)


def GetAllCollisionAndSocketsObj():
	#Get any object that can be understood as a collision or a socket by unreal

	colObjs = [obj for obj in bpy.context.scene.objects if
		fnmatch.fnmatchcase(obj.name, "UBX*") or
		fnmatch.fnmatchcase(obj.name, "UCP*") or
		fnmatch.fnmatchcase(obj.name, "USP*") or
		fnmatch.fnmatchcase(obj.name, "UCX*") or
		fnmatch.fnmatchcase(obj.name, "SOCKET*")]
	return colObjs


def GetExportDesiredChilds(obj):
	#Get only all child objects that must be exported with parent object

	DesiredObj = []
	for child in GetRecursiveChilds(obj):
		if child.ExportEnum != "dont_export":
			DesiredObj.append(child)
	return DesiredObj


def GetSocketDesiredChild(targetObj):
	socket = [obj for obj in GetExportDesiredChilds(targetObj) if
		fnmatch.fnmatchcase(obj.name, "SOCKET*")]
	return socket


def GetAllCollisionObj():
	#Get any object that can be understood as a collision or a socket by unreal

	colObjs = [obj for obj in bpy.context.scene.objects if
		fnmatch.fnmatchcase(obj.name, "UBX*") or
		fnmatch.fnmatchcase(obj.name, "UCP*") or
		fnmatch.fnmatchcase(obj.name, "USP*") or
		fnmatch.fnmatchcase(obj.name, "UCX*")]
	return colObjs


def GetActionToExport(obj):
	#Returns only the actions that will be exported with the Armature
	
	#if obj.animation_data is None:
		#return []
		
	if obj.ExportAsLod == True:
		return []

	TargetActionToExport = [] #Action list
	if obj.exportActionEnum == "dont_export":
		return []	
	elif obj.exportActionEnum == "export_specific_list":
		for action in bpy.data.actions:
			for targetAction in obj.exportActionList:
				if targetAction.use == True:
					if targetAction.name == action.name:
						TargetActionToExport.append(action)

	elif obj.exportActionEnum == "export_specific_prefix":
		for action in bpy.data.actions:
			if fnmatch.fnmatchcase(action.name, obj.PrefixNameToExport+"*"):
				TargetActionToExport.append(action)
				
	elif obj.exportActionEnum == "export_auto":
		objBoneNames = [bone.name for bone in obj.data.bones]
		for action in bpy.data.actions:
			actionBoneNames = [group.name for group in action.groups]
			if ChecksRelationship(objBoneNames, actionBoneNames):
				TargetActionToExport.append(action)

	return TargetActionToExport
		

def GetDesiredActionStartEndTime(obj, action): 
	#Returns desired action or camera anim start/end time
	#Return start with index 0 and end with index 1
	
	scene = bpy.context.scene
	if obj.type == "CAMERA":
		startTime = scene.frame_start
		endTime = scene.frame_end
		
	elif obj.AnimStartEndTimeEnum == "with_keyframes":
		startTime = action.frame_range.x #GetFirstActionFrame
		endTime = action.frame_range.y #GetLastActionFrame
		
	elif obj.AnimStartEndTimeEnum == "with_sceneframes":
		startTime = scene.frame_start
		endTime = scene.frame_end
		
	elif obj.AnimStartEndTimeEnum == "with_customframes":
		startTime = obj.AnimCustomStartTime
		endTime = obj.AnimCustomEndTime

	if obj.AddOneAdditionalFramesAtTheEnd == True:
		endTime += 1
	return (startTime,endTime)	
	
	
def GetActionType(action):
	#return action type
	
	if action.frame_range.y - action.frame_range.x == 1:
		return "Pose"
	return "Action"
	
	
def GetIsAnimation(type):
	#return True if type(string) is a animation
	if (type == "NlAnim" or type == "Action" or type == "Pose"):
		return True
	return False


def GetAssetType(obj):
	#Return asset type of a object

	if obj.type == "CAMERA":
		return "Camera"	
		
	if obj.ExportAsAlembic == True:
		return "Alembic"
		
	if obj.type == "ARMATURE" and obj.ForceStaticMesh == False:
		return "SkeletalMesh"
		
	return "StaticMesh"
	

def CheckIsCollision(target): 
	#Return true if obj is a collision
	for obj in GetAllCollisionObj():
		if obj == target:
			return True
	return False
	
	
def SelectParentAndDesiredChilds(obj):
	#Selects only all child objects that must be exported with parent object

	bpy.ops.object.select_all(action='DESELECT')
	for selectObj in GetExportDesiredChilds(obj):
		selectObj.select_set(True)
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj


def GetFinalAssetToExport():
	#Returns all assets that will be exported
	
	
	
	scene = bpy.context.scene
	TargetAssetToExport = [] #Obj, Action, type
	class AssetToExport:
		def __init__(self, obj, action, type):
			self.obj = obj
			self.action = action
			self.type = type
	
	if scene.export_ExportOnlySelected == True:
		objList = []
		for obj in GetAllobjectsByExportType("export_recursive"):
			if obj in bpy.context.selected_objects:
				if obj not in objList:
					objList.append(obj)
			for objChild in GetExportDesiredChilds(obj):
				if objChild in bpy.context.selected_objects:
					if obj not in objList:
						objList.append(obj)
	
	else:
		objList = GetAllobjectsByExportType("export_recursive")
		
	for obj in  objList:

		if GetAssetType(obj) == "Alembic":
			#Alembic
			if scene.alembic_export:
				TargetAssetToExport.append(AssetToExport(obj,None,"Alembic"))
			
		if GetAssetType(obj) == "SkeletalMesh":
			#SkeletalMesh
			if scene.skeletal_export:
				TargetAssetToExport.append(AssetToExport(obj,None,"SkeletalMesh"))
				
			#NLA
			if scene.anin_export:
				if obj.ExportNLA:
					TargetAssetToExport.append(AssetToExport(obj,obj.animation_data,"NlAnim"))
					
			for action in GetActionToExport(obj):
				
				#Action
				if scene.anin_export:
					if GetActionType(action) == "Action":
						TargetAssetToExport.append(AssetToExport(obj,action,"Action"))
				
				#Pose
				if scene.anin_export:
					if GetActionType(action) == "Pose":
						TargetAssetToExport.append(AssetToExport(obj,action,"Pose"))
		#Camera
		if GetAssetType(obj) == "Camera" and scene.camera_export:
			TargetAssetToExport.append(AssetToExport(obj,None,"Camera"))

		#StaticMesh
		if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				TargetAssetToExport.append(AssetToExport(obj,None,"StaticMesh"))

	return TargetAssetToExport


def ValidFilenameForUnreal(filename):
	# valid file name for unreal assets
	extension = os.path.splitext(filename)[1]
	newfilename = ValidFilename(os.path.splitext(filename)[0])
	return (''.join(c for c in newfilename if c != ".")+extension)


def GetObjExportDir(obj, abspath = False):
	#Generate assset folder path
	scene = bpy.context.scene	
	if GetAssetType(obj) == "SkeletalMesh":
		dirpath = os.path.join( scene.export_skeletal_file_path , obj.exportFolderName , obj.name)	
	if GetAssetType(obj) == "Alembic":
		dirpath = os.path.join( scene.export_alembic_file_path , obj.exportFolderName , obj.name)
	if GetAssetType(obj) == "StaticMesh":
		dirpath = os.path.join( scene.export_static_file_path, obj.exportFolderName )
	if GetAssetType(obj) == "Camera":
		dirpath = os.path.join( scene.export_camera_file_path, obj.exportFolderName )
	if abspath == True:
		return bpy.path.abspath(dirpath)
	else:
		return dirpath


def GetObjExportFileName(obj, fileType = ".fbx"):
	#Generate assset file name
	
	scene = bpy.context.scene
	assetType = GetAssetType(obj)
	if assetType == "Camera":
		return scene.camera_prefix_export_name+obj.name+fileType
	elif assetType == "StaticMesh":
		return scene.static_prefix_export_name+obj.name+fileType
	elif assetType == "SkeletalMesh":
		return scene.skeletal_prefix_export_name+obj.name+fileType	
	elif assetType == "Alembic":
		return scene.alembic_prefix_export_name+obj.name+fileType
	else:
		return None
		

def GetActionExportFileName(obj, action, fileType = ".fbx"):
	#Generate action file name

	scene = bpy.context.scene
	animType = GetActionType(action)
	if animType == "NlAnim" or animType == "Action": #Nla can be exported as action
		return scene.anim_prefix_export_name+obj.name+"_"+action.name+fileType
	elif animType == "Pose":
		return scene.pose_prefix_export_name+obj.name+"_"+action.name+fileType
	else:
		return None
		
def GetNLAExportFileName(obj, fileType = ".fbx"):
	#Generate action file name

	scene = bpy.context.scene
	return scene.anim_prefix_export_name+obj.name+"_"+obj.NLAAnimName+fileType
	
def GetImportAssetScriptCommand():
	scene = bpy.context.scene
	fileName = scene.file_import_asset_script_name
	absdirpath = bpy.path.abspath(scene.export_other_file_path)
	fullpath = os.path.join( absdirpath , fileName )
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	if addon_prefs.Use20TabScript == True:
		return 'unreal_engine.py_exec(r"'+fullpath+'")' #20tab
	else:
		return 'py "'+fullpath+'"' #Vania
	
def GetImportSequencerScriptCommand():
	scene = bpy.context.scene
	fileName = scene.file_import_sequencer_script_name
	absdirpath = bpy.path.abspath(scene.export_other_file_path)
	fullpath = os.path.join( absdirpath , fileName )
	
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	if addon_prefs.Use20TabScript == True:
		return 'unreal_engine.py_exec(r"'+fullpath+'")' #20tab
	else:
		return 'py "'+fullpath+'"' #Vania
	
def GetAnimSample(obj):
	#return obj sample animation
	#return 1000 #Debug
	return obj.SampleAnimForExport
	
def RenameArmatureAsExportName(obj):
	#Rename temporarily the Armature as DefaultArmature
	
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	scene = bpy.context.scene
	oldArmatureName = None
	if obj.name != addon_prefs.skeletonRootBoneName:
		oldArmatureName = obj.name
		#Avoid same name for two armature
		if addon_prefs.skeletonRootBoneName in scene.objects:
			scene.objects[addon_prefs.skeletonRootBoneName].name = "ArmatureTemporarilyNameForUe4Export"
		obj.name = addon_prefs.skeletonRootBoneName
	return oldArmatureName
			
def ResetArmatureName(obj, oldArmatureName):
	#Reset armature name
	
	addon_prefs = bpy.context.preferences.addons["blender-for-unrealengine"].preferences
	scene = bpy.context.scene
	if oldArmatureName is not None:
		obj.name = oldArmatureName
		if "ArmatureTemporarilyNameForUe4Export" in scene.objects:
			scene.objects["ArmatureTemporarilyNameForUe4Export"].name = addon_prefs.skeletonRootBoneName
			
def GenerateUe4Name(name):
	#Generate a new name with suffix number

	def IsValidName(testedName):
		#Checks if objet end with number suffix 

		try:
			number = int(testedName.split("_")[-1])
		except:
			#Last suffix is not a number
			return False

		#Checks if an object uses this name. (If not is a valid name)
		for obj in bpy.context.scene.objects:
			if testedName == obj.name:
				return False

		return True

	newName = ""
	if IsValidName(name):
		return name
	else:
		for num in range(0, 1000):
			newName = name+"_"+str('%02d' % num) #Min two pad
			if IsValidName(newName):
				return newName

	return name

def CreateCollisionMaterial():
	mat = bpy.data.materials.get("UE4Collision")
	if mat is None:
		mat = bpy.data.materials.new(name="UE4Collision")
	mat.diffuse_color = (0, 0.6, 0, 0.11)
	#mat.alpha = 0.1
	#mat.use_transparency = True
	mat.use_nodes = False
	if bpy.context.scene.render.engine == 'CYCLES':
		#sets up the nodes to create a transparent material with GLSL mat in Cycle
		mat.use_nodes = True
		node_tree = mat.node_tree
		nodes = node_tree.nodes
		nodes.clear()
		out = nodes.new('ShaderNodeOutputMaterial')
		out.location = (0,0)
		mix = nodes.new('ShaderNodeMixShader')
		mix.location = (-200,000)
		mix.inputs[0].default_value = (0.95)
		diff = nodes.new('ShaderNodeBsdfDiffuse')
		diff.location = (-400,100)
		diff.inputs[0].default_value = (0, 0.6, 0, 1)
		trans = nodes.new('ShaderNodeBsdfTransparent')
		trans.location = (-400,-100)
		trans.inputs[0].default_value = (0, 0.6, 0, 1)
		node_tree.links.new(diff.outputs['BSDF'], mix.inputs[1])
		node_tree.links.new(trans.outputs['BSDF'], mix.inputs[2])
		node_tree.links.new(mix.outputs['Shader'], out.inputs[0])
	return mat

def Ue4SubObj_set(SubType):
	#Convect obj to ue4 sub objects (Collisions Shapes or Socket)
	
	def DeselectAllWithoutActive():
		for obj in bpy.context.selected_objects:
			if obj != bpy.context.active_object:
				obj.select_set(False)
	
	ownerObj = bpy.context.active_object
	ownerBone = bpy.context.active_pose_bone
	objList = bpy.context.selected_objects
	if ownerObj is None:
		return []
		
	ConvertedObjs = []

	for obj in objList:
		DeselectAllWithoutActive()
		obj.select_set(True)
		if obj != ownerObj:
		
			#SkeletalMesh Colider
			if obj.type == 'MESH':
				ConvertToConvexHull(obj)
				obj.modifiers.clear()
				obj.data
				obj.data.materials.clear()
				obj.active_material_index = 0
				obj.data.materials.append(CreateCollisionMaterial())
				
				#Set the name of the Prefix depending on the type of collision in agreement with unreal FBX Pipeline
				if SubType == "Box":
					prefixName = "UBX_"
				elif SubType == "Capsule":
					prefixName = "UCP_"
				elif SubType == "Sphere":
					prefixName = "USP_"
				elif SubType == "Convex":
					prefixName = "UCX_"
				
				obj.name = GenerateUe4Name(prefixName+ownerObj.name)
				obj.show_wire = True
				obj.show_transparent = True
				bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
				ConvertedObjs.append(obj)
				
				
			#StaticMesh Socket
			if obj.type == 'EMPTY' and SubType == "ST_Socket":
				if ownerObj.type == 'MESH':
					if not obj.name.startswith("SOCKET_"):
						obj.name = GenerateUe4Name("SOCKET_"+obj.name)
					bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
					ConvertedObjs.append(obj)
						
			#SkeletalMesh Socket			
			if obj.type == 'EMPTY' and SubType == "SK_Socket":
				if ownerObj.type == 'ARMATURE':
					if not obj.name.startswith("SOCKET_"):
						obj.name = GenerateUe4Name("SOCKET_"+obj.name)
					bpy.ops.object.parent_set(type='BONE')
					ConvertedObjs.append(obj)
						
	DeselectAllWithoutActive()
	for obj in objList: obj.select_set(True) #Resets previous selected object
	return ConvertedObjs
	
	
def UpdateUe4Name(SubType, objList):
	#Convect obj to ue4 sub objects (Collisions Shapes or Socket)
	
	for obj in objList:
		ownerObj = obj.parent
			

		if ownerObj is not None:
			if obj != ownerObj:
		
				#SkeletalMesh Colider
				if obj.type == 'MESH':

					#Set the name of the Prefix depending on the type of collision in agreement with unreal FBX Pipeline
					if SubType == "Box":
						prefixName = "UBX_"
					elif SubType == "Capsule":
						prefixName = "UCP_"
					elif SubType == "Sphere":
						prefixName = "USP_"
					elif SubType == "Convex":
						prefixName = "UCX_"

					obj.name = GenerateUe4Name(prefixName+ownerObj.name)
					
					
				#StaticMesh Socket
				if obj.type == 'EMPTY' and SubType == "ST_Socket":
					if ownerObj.type == 'MESH':
						if not obj.name.startswith("SOCKET_"):
							obj.name = GenerateUe4Name("SOCKET_"+obj.name)
							
				#SkeletalMesh Socket			
				if obj.type == 'EMPTY' and SubType == "SK_Socket":
					if ownerObj.type == 'ARMATURE':
						if not obj.name.startswith("SOCKET_"):
							obj.name = GenerateUe4Name("SOCKET_"+obj.name)


def UpdateNameHierarchy():
#Updates hierarchy names
	for obj in GetAllCollisionAndSocketsObj():
		if fnmatch.fnmatchcase(obj.name, "UBX*"):
			UpdateUe4Name("Box", [obj])
		if fnmatch.fnmatchcase(obj.name, "UCP*"):
			UpdateUe4Name("Capsule", [obj])
		if fnmatch.fnmatchcase(obj.name, "USP*"):
			UpdateUe4Name("Sphere", [obj])
		if fnmatch.fnmatchcase(obj.name, "UCX*"):
			UpdateUe4Name("Convex", [obj])
		if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
			UpdateUe4Name("Socket", [obj])


def CorrectBadProperty():
#Corrects bad properties
	UpdatedProp = 0
	for obj in GetAllCollisionAndSocketsObj():
		if obj.ExportEnum == "export_recursive":
			obj.ExportEnum = "auto"
			UpdatedProp += 1
	return UpdatedProp

def GetVertexWithZeroWeight(Armature, Mesh):
	vertices = []
	for vertex in Mesh.data.vertices:
		cumulateWeight = 0
		if len(vertex.groups) > 0:
			for GroupElem in vertex.groups:
				if Mesh.vertex_groups[GroupElem.group].name in Armature.data.bones:
					cumulateWeight += GroupElem.weight
		if cumulateWeight == 0:
			vertices.append(vertex)
	return vertices

def UpdateUnrealPotentialError():
	#Find and reset list of all potential error in scene
	
	
	PotentialErrors = bpy.context.scene.potentialErrorList
	PotentialErrors.clear()
	
	#prepares the data to avoid unnecessary loops	
	objToCheck = []
	for Asset in GetFinalAssetToExport():
		if Asset.obj in GetAllobjectsByExportType("export_recursive"):
			if Asset.obj not in objToCheck:
				objToCheck.append(Asset.obj)
			for child in GetExportDesiredChilds(Asset.obj):
				if child not in objToCheck:
					objToCheck.append(child)

	MeshTypeToCheck = []
	for obj in objToCheck:
		if obj.type == 'MESH':
			MeshTypeToCheck.append(obj)
			
	MeshTypeWithoutCol = [] # is Mesh Type To Check Without Collision	
	for obj in MeshTypeToCheck:
		if not CheckIsCollision(obj):
			MeshTypeWithoutCol.append(obj)

	def CheckObjType():
	#Check if objects use a non-recommended type
		for obj in objToCheck:
			if obj.type == "SURFACE" or obj.type == "META" or obj.type == "FONT":
				MyError = PotentialErrors.add()
				MyError.name = obj.name
				MyError.type = 1
				MyError.text = 'Object "'+obj.name+'" is a '+obj.type+'. The object of the type SURFACE, META and FONT is not recommended.'
				MyError.object = obj
				MyError.correctRef = "ConvertToMesh"
				MyError.correctlabel = 'Convert to mesh'
				
	def CheckShapeKeys():
		for obj in MeshTypeToCheck:
			if obj.data.shape_keys is not None:
				#Check that no modifiers is destructive for the key shapes
				if len(obj.data.shape_keys.key_blocks) > 0:
					for modif in obj.modifiers:
						if modif.type != "ARMATURE" :
							MyError = PotentialErrors.add()
							MyError.name = obj.name
							MyError.type = 2
							MyError.object = obj
							MyError.itemName = modif.name
							MyError.text = 'In object "'+obj.name+'" the modifier '+modif.type+' named "'+modif.name+'" can destroy shape keys. Please use only Armature modifier with shape keys.'
							MyError.correctRef = "RemoveModfier"
							MyError.correctlabel = 'Remove modifier'
				
				#Check that the key shapes are not out of bounds for Unreal
				for key in obj.data.shape_keys.key_blocks:
					#Min
					if key.slider_min < -5:
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 1
						MyError.object = obj
						MyError.itemName = key.name
						MyError.text = 'In object "'+obj.name+'" the shape key "'+key.name+'" is out of bounds for Unreal. The min range of must not be inferior to -5.'
						MyError.correctRef = "SetKeyRangeMin"
						MyError.correctlabel = 'Set min range to -5'
					
					#Max
					if key.slider_max > 5:
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 1
						MyError.object = obj
						MyError.itemName = key.name
						MyError.text = 'In object "'+obj.name+'" the shape key "'+key.name+'" is out of bounds for Unreal. The max range of must not be superior to 5.'
						MyError.correctRef = "SetKeyRangeMax"
						MyError.correctlabel = 'Set max range to -5'
						
	def CheckUVMaps():
		#Check that the objects have at least one UV map valid
		for obj in MeshTypeWithoutCol:
			if len(obj.data.uv_layers) < 1:
				MyError = PotentialErrors.add()
				MyError.name = obj.name
				MyError.type = 1
				MyError.text = 'Object "'+obj.name+'" does not have any UV Layer.'
				MyError.object = obj
				MyError.correctRef = "CreateUV"
				MyError.correctlabel = 'Create Smart UV Project'

	def CheckBadStaicMeshExportedLikeSkeletalMesh():
		#Check if the correct object is defined as exportable
		for obj in MeshTypeToCheck:
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					if obj.ExportEnum == "export_recursive":
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 1
						MyError.text = 'In object "'+obj.name+'" the modifier '+modif.type+' named "'+modif.name+'" will not be applied when exported with StaticMesh assets.\nNote: with armature if you want export objets as skeletal mesh you need set only the armature as export_recursive not the childs'
						MyError.object = obj

	def CheckArmatureModNumber():
		#check that there is no more than one Modifier ARMATURE at the same time
		for obj in MeshTypeToCheck:
			ArmatureModifiers = 0
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					ArmatureModifiers = ArmatureModifiers + 1
			if ArmatureModifiers > 1:
				MyError = PotentialErrors.add()
				MyError.name = obj.name
				MyError.type = 2
				MyError.text = 'In object "'+obj.name+'" there are several Armature modifiers at the same time. Please use only one Armature modifier.'
				MyError.object = obj

	def CheckArmatureModData():
		#check the parameter of Modifier ARMATURE
		for obj in MeshTypeToCheck:
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					if modif.use_deform_preserve_volume == True:
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 2
						MyError.text = 'In object "'+obj.name+'" the modifier '+modif.type+' named "'+modif.name+'". The parameter Preserve Volume must be set to False.'
						MyError.object = obj
						MyError.itemName = modif.name
						MyError.correctRef = "PreserveVolume"
						MyError.correctlabel = 'Set Preserve Volume to False'
						
	def CheckArmatureBoneData():
		#check the parameter of the ARMATURE bones
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				for bone in obj.data.bones:
					if bone.bbone_segments > 1:
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 2
						MyError.text = 'In object3 "'+obj.name+'" the bone named "'+bone.name+'". The parameter Bendy Bones / Segments must be set to 1.'
						MyError.object = obj
						MyError.itemName = bone.name
						MyError.correctRef = "BoneSegments"
						MyError.correctlabel = 'Set Bone Segments to 1'
						
					if bone.use_inherit_scale == False:
						MyError = PotentialErrors.add()
						MyError.name = obj.name
						MyError.type = 2
						MyError.text = 'In object2 "'+obj.name+'" the bone named "'+bone.name+'". The parameter Inherit Scale must be set to True.'
						MyError.object = obj
						MyError.itemName = bone.name
						MyError.correctRef = "InheritScale"
						MyError.correctlabel = 'Set Inherit Scale to True'
	
	def CheckArmatureValidChild():
		#Check that skeleton also has a mesh to export
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				childs = GetExportDesiredChilds(obj)
				validChild = 0
				for child in childs:
					if child.type == "MESH":
						validChild += 1
				if validChild < 1:
					MyError = PotentialErrors.add()
					MyError.name = obj.name
					MyError.type = 2
					MyError.text = 'Object "'+obj.name+'" is an Armature and does not have any valid children.'
					MyError.object = obj

	def CheckArmatureMultipleRoots():
		#Check that skeleton have multiples roots
		
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				RootsBone = []
				for bone in obj.data.bones:
					if bone.parent == None:
						RootsBone.append(bone)
				if len(RootsBone) > 1:
					MyError = PotentialErrors.add()
					MyError.name = obj.name
					MyError.type = 2
					MyError.text = 'Object "'+obj.name+'" have Multiple roots bones. Unreal only support single root bone.'
					MyError.object = obj
		
	def CheckMarkerOverlay():
		#Check that there is no overlap with the Marker
		usedFrame = []
		for marker in bpy.context.scene.timeline_markers:
			if marker.frame in usedFrame:
				MyError = PotentialErrors.add()
				MyError.type = 2
				MyError.text = 'In the scene timeline the frame "'+str(marker.frame)+'" contains overlaped Markers\n To avoid camera conflict in the generation of sequencer you must use max one marker per frame '
			else:
				usedFrame.append(marker.frame)
			
	
	def CheckVertexGroupWeight():
		#Check that all vertex have a weight
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				childs = GetExportDesiredChilds(obj)
				for child in childs:
					if child.type == "MESH":						
						#Result data	
						VertexWithZeroWeight = GetVertexWithZeroWeight(obj, child)
						if len(VertexWithZeroWeight) > 0:
							MyError = PotentialErrors.add()
							MyError.name = child.name
							MyError.type = 1
							MyError.text = 'Object named "'+child.name+'" contains '+str(len(VertexWithZeroWeight))+' vertex with zero cumulative valid weight.'
							MyError.object = child							
							MyError.vertexErrorType = "VertexWithZeroWeight"
								
			
	def CheckZeroScaleKeyframe():
		#Check that animations do not use a invalid value
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				for action in GetActionToExport(obj):
					for fcurve in action.fcurves:
						if fcurve.data_path.split(".")[-1] == "scale":
							for key in fcurve.keyframe_points:
								xCurve, yCurve = key.co
								if key.co[1] == 0:
									MyError = PotentialErrors.add()
									MyError.type = 2
									MyError.text = 'In action "'+action.name+'" at frame '+str(key.co[0])+', the bone named "'+fcurve.data_path.split('"')[1]+'" has a zero value in scale transform. This is invalid in Unreal.'
				
						
	CheckObjType()
	CheckShapeKeys()
	CheckUVMaps()
	CheckBadStaicMeshExportedLikeSkeletalMesh()
	CheckArmatureModNumber()
	CheckArmatureModData()
	CheckArmatureBoneData()
	CheckArmatureValidChild()
	CheckArmatureMultipleRoots()
	CheckMarkerOverlay()
	CheckVertexGroupWeight()
	CheckZeroScaleKeyframe()

	return PotentialErrors


def SelectPotentialErrorObject(errorIndex):
	#Select potential error
	
	if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode = "OBJECT")
	scene = bpy.context.scene
	error = scene.potentialErrorList[errorIndex]
	obj = error.object
	
	bpy.ops.object.select_all(action='DESELECT')
	obj.hide_viewport = False
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj

	#show collection for select object		
	for collection in bpy.data.collections: 
		for ColObj in collection.objects:
			if ColObj == obj:
				SetCollectionUse(collection)
	bpy.ops.view3d.view_selected()
	return obj

def SelectPotentialErrorVertex(errorIndex):
	#Select potential error
	SelectPotentialErrorObject(errorIndex)
	bpy.ops.object.mode_set(mode = "EDIT")
	
	scene = bpy.context.scene
	error = scene.potentialErrorList[errorIndex]
	obj = error.object
	bpy.ops.mesh.select_mode(type="VERT")
	bpy.ops.mesh.select_all(action='DESELECT')
	
	bpy.ops.object.mode_set(mode = 'OBJECT')
	if error.vertexErrorType == "VertexWithZeroWeight":
		for vertex in GetVertexWithZeroWeight(obj.parent, obj):
			vertex.select = True
	bpy.ops.object.mode_set(mode = 'EDIT')
	bpy.ops.view3d.view_selected()
	return obj
	
def TryToCorrectPotentialError(errorIndex):
	#Try to correct potential error
	
	scene = bpy.context.scene
	error = scene.potentialErrorList[errorIndex]
	global successCorrect 
	successCorrect = False
	#----------------------------------------Save data
	UserActive = bpy.context.active_object #Save current active object
	UserMode = None 
	if UserActive and UserActive.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		UserMode = UserActive.mode #Save current mode
		bpy.ops.object.mode_set(mode='OBJECT')
	UserSelected = bpy.context.selected_objects #Save current selected objects
			
	UsedViewLayerCollectionHideViewport = []
	UsedCollectionHideViewport = []
	UsedCollectionHideselect = []
	for collection in bpy.data.collections: #Save previous collections visibility
		try:
			UsedViewLayerCollectionHideViewport.append(view_layer.layer_collection.children[collection.name].hide_viewport)
		except:
			print(collection.name," not found in layer_collection")
			pass
		UsedCollectionHideViewport.append(collection.hide_viewport)
		UsedCollectionHideselect.append(collection.hide_select)
		SetCollectionUse(collection)
	
	#----------------------------------------
	print("Start correct")
	def SelectObj(obj):
		bpy.ops.object.select_all(action='DESELECT')
		obj.select_set(True)
		bpy.context.view_layer.objects.active = obj
			
	
	#Correction list
	
	if error.correctRef == "ConvertToMesh":
		obj = error.object
		SelectObj(obj)
		bpy.ops.object.convert(target='MESH')
		successCorrect = True
		
	if error.correctRef == "SetKeyRangeMin":
		obj = error.object
		key = obj.data.shape_keys.key_blocks[error.itemName]
		key.slider_min = -5
		successCorrect = True
	
	if error.correctRef == "SetKeyRangeMax":
		obj = error.object
		key = obj.data.shape_keys.key_blocks[error.itemName]
		key.slider_max = 5
		successCorrect = True
	
	if error.correctRef == "CreateUV":
		obj = error.object
		SelectObj(obj)
		bpy.ops.uv.smart_project()
		successCorrect = True
		
	if error.correctRef == "RemoveModfier":
		obj = error.object
		mod = obj.modifiers[error.itemName]
		obj.modifiers.remove(mod)
		successCorrect = True
		
	if error.correctRef == "PreserveVolume":
		obj = error.object
		mod = obj.modifiers[error.itemName]
		mod.use_deform_preserve_volume = False
		successCorrect = True
		
	if error.correctRef == "BoneSegments":
		obj = error.object
		bone = obj.data.bones[error.itemName]
		bone.bbone_segments = 1		
		successCorrect = True
	
	if error.correctRef == "InheritScale":
		obj = error.object
		bone = obj.data.bones[error.itemName]
		bone.use_inherit_scale = True		
		successCorrect = True
		
	#----------------------------------------Reset data
	for x, collection in enumerate(bpy.data.collections):
		try:
			view_layer.layer_collection.children[collection.name].hide_viewport = UsedViewLayerCollectionHideViewport[x]
		except:
			print(collection.name," not found in layer_collection")
			pass
		collection.hide_viewport = UsedCollectionHideViewport[x]
		collection.hide_select = UsedCollectionHideselect[x]
	
	bpy.ops.object.select_all(action='DESELECT')
	for obj in UserSelected: #Resets previous selected object if still exist
		print("######",obj)
		if obj.name in scene.objects:
			obj.select_set(True) 
	bpy.context.view_layer.objects.active = UserActive #Resets previous active object
	if UserActive and UserMode and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode=UserMode) #Resets previous mode
	#----------------------------------------
		
	if successCorrect == True:
		scene.potentialErrorList.remove(errorIndex)
		print("end correct, Error: " + error.correctRef)
		return "Corrected"
	print("end correct, Error not found")
	return "Correct fail"