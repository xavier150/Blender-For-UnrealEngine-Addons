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
import bmesh
from .bfu_basics import *



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
		print(child.name)
		if child.ExportEnum != "dont_export":
			DesiredObj.append(child)
	return DesiredObj


def GetAllChildSocket(targetObj):
	socket = [obj for obj in GetRecursiveChilds(targetObj) if
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
	
	if obj.animation_data is None:
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
		return (startTime,endTime)
		
	elif obj.AnimStartEndTimeEnum == "with_keyframes":
		startTime = action.frame_range.x #GetFirstActionFrame
		endTime = action.frame_range.y #GetLastActionFrame
		return (startTime,endTime)
		
	elif obj.AnimStartEndTimeEnum == "with_sceneframes":
		startTime = scene.frame_start
		endTime = scene.frame_end
		return (startTime,endTime)
		
	elif obj.AnimStartEndTimeEnum == "with_customframes":
		startTime = obj.AnimCustomStartTime
		endTime = obj.AnimCustomEndTime
		return (startTime,endTime)	
	
	
def GetActionType(action):
	#return action type
	
	if action.frame_range.y - action.frame_range.x == 1:
		return "Pose"
	return "Animation"


def GetAssetType(obj):
	#Return asset type of a object
	
	if obj.type == "ARMATURE":
		if obj.ForceStaticMesh == False:
			return "SkeletalMesh"
		return "StaticMesh"
	elif obj.type == "CAMERA":
		return "Camera"
	else:
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
		selectObj.select = True
	obj.select = True
	bpy.context.scene.objects.active = obj


def GetFinalAssetToExport():
	#Returns all assets that will be exported
	
	scene = bpy.context.scene
	TargetAassetToExport = [] #Obj, Action, type


	for obj in GetAllobjectsByExportType("export_recursive"):
		if GetAssetType(obj) == "SkeletalMesh":
			#SkeletalMesh
			if scene.skeletal_export:
				TargetAassetToExport.append((obj,None,"SkeletalMesh"))
			for action in GetActionToExport(obj):
				#Animation
				if scene.anin_export:
					if GetActionType(action) == "Animation":
						TargetAassetToExport.append((obj,action,"Animation"))
				#Pose
				if scene.pose_export:
					if GetActionType(action) == "Pose":
						TargetAassetToExport.append((obj,action,"Pose"))
		#Camera
		if GetAssetType(obj) == "Camera" and scene.camera_export:
			TargetAassetToExport.append((obj,None,"Camera"))

		#StaticMesh
		if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				TargetAassetToExport.append((obj,None,"StaticMesh"))

	return TargetAassetToExport


def GetObjExportFileName(obj):
	#Generate assset file name

	scene = bpy.context.scene
	assetType = GetAssetType(obj)
	if assetType == "Camera":
		return scene.camera_prefix_export_name+obj.name+".fbx"
	elif assetType == "StaticMesh":
		return scene.static_prefix_export_name+obj.name+".fbx"
	elif assetType == "SkeletalMesh":
		return scene.skeletal_prefix_export_name+obj.name+".fbx"
	else:
		return None
		
		
def GetActionExportFileName(obj, action):
	#Generate action file name

	scene = bpy.context.scene
	animType = GetActionType(action)
	if animType == "Animation":
		return scene.anim_prefix_export_name+obj.name+"_"+action.name+".fbx"
	elif animType == "Pose":
		return scene.pose_prefix_export_name+obj.name+"_"+action.name+".fbx"
	else:
		return None
		
		
def GetCameraTrackFileName(camera):
	#Generate additional camera track file name
	
	scene = bpy.context.scene
	return scene.camera_prefix_export_name+camera.name+"_AdditionalTrack.ini"
	
	
def GenerateUe4Name(name):
	#Generate a new name with suffix number

	def IsValidName(testedName):
		#Checks if an object uses this name. (If not is a valid name)

		for obj in bpy.context.scene.objects:
			if testedName == obj.name:
				return False
		return True

	valid = False
	number = 1
	newName = ""
	if IsValidName(name):
		return name
	else:
		while valid == False:
			newName = name+"_"+str(number)
			if IsValidName(newName):
				return newName
			else:
				number = number+1
	return newName


def ConvertToUe4SubObj(collisionType, objsToConvert, useActiveAsOwner=False):
	#Convect obj to ue4 sub objects (Collisions Shapes or Socket)

	ConvertedObjs = []

	def ApplyConvexHull(obj):
		mesh = obj.data
		if not mesh.is_editmode:
			bm = bmesh.new()
			bm.from_mesh(mesh) #Mesh to Bmesh
			acb = bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
			#acb = bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
			bm.to_mesh(mesh) #BMesh to Mesh

	#Set the name of the Prefix depending on the type of collision in agreement with unreal FBX Pipeline
	if collisionType == "Box":
		prefixName = "UBX_"
	elif collisionType == "Capsule":
		prefixName = "UCP_"
	elif collisionType == "Sphere":
		prefixName = "USP_"
	elif collisionType == "Convex":
		prefixName = "UCX_"

	mat = bpy.data.materials.get("UE4Collision")
	if mat is None:
		mat = bpy.data.materials.new(name="UE4Collision")
	mat.diffuse_color = (0, 0.6, 0)
	mat.alpha = 0.1
	mat.use_transparency = True
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


		#node

	for obj in objsToConvert:
		if useActiveAsOwner == True:
			ownerObj = bpy.context.active_object
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
		else:
			ownerObj = obj.parent
		if ownerObj is not None:
			if obj != ownerObj:
				#Mesh
				if obj.type == 'MESH':
					ApplyConvexHull(obj)
					obj.modifiers.clear()
					obj.data
					obj.data.materials.clear()
					obj.active_material_index = 0
					obj.data.materials.append(mat)
					obj.name = GenerateUe4Name(prefixName+ownerObj.name)
					obj.show_wire = True
					obj.show_transparent = True
					ConvertedObjs.append(obj)
				#Socket
				if obj.type == 'EMPTY' and collisionType == "Socket":
					if ownerObj.type == 'MESH':
						if not obj.name.startswith("SOCKET_"):
							obj.name = GenerateUe4Name("SOCKET_"+obj.name)
							ConvertedObjs.append(obj)
						else:
							print(obj.name+" is already a socket")
							ConvertedObjs.append(obj)
	return ConvertedObjs


def UpdateUnrealPotentialError():
	#Find and reset list of all potential error in scene
	
	
	PotentialErrors = bpy.context.scene.potentialErrorList
	PotentialErrors.clear()

	#prepares the data to avoid unnecessary loops
	objToCheck = []
	for obj in GetAllobjectsByExportType("export_recursive"):
		objToCheck.append(obj)
		for obj2 in GetExportDesiredChilds(obj):
			objToCheck.append(obj2)
			
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
						MyError.type = 1
						MyError.object = obj
						MyError.itemName = key.name
						MyError.text = 'In object "'+obj.name+'" the shape key "'+key.name+'" is out of bounds for Unreal. The min range of must not be inferior to -5.'
						MyError.correctRef = "SetKeyRangeMin"
						MyError.correctlabel = 'Set min range to -5'
					
					#Max
					if key.slider_max > 5:
						MyError = PotentialErrors.add()
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
						MyError.type = 1
						MyError.text = 'In object "'+obj.name+'" the modifier '+modif.type+' named "'+modif.name+'will not be applied when exported with StaticMesh assets.'

	def CheckArmatureModNumber():
		#check that there is no more than one Modifier ARMATURE at the same time
		for obj in MeshTypeToCheck:
			ArmatureModifiers = 0
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					ArmatureModifiers = ArmatureModifiers + 1
			if ArmatureModifiers > 1:
				MyError = PotentialErrors.add()
				MyError.type = 2
				MyError.text = 'In object "'+obj.name+'" there are several Armature modifiers at the same time. Please use only one Armature modifier.'

	def CheckArmatureModData():
		#check the parameter of Modifier ARMATURE
		for obj in MeshTypeToCheck:
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					if modif.use_deform_preserve_volume == True:
						MyError = PotentialErrors.add()
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
						MyError.type = 2
						MyError.text = 'In object3 "'+obj.name+'" the bone named "'+bone.name+'". The parameter Bendy Bones / Segments must be set to 1.'
						MyError.object = obj
						MyError.itemName = bone.name
						MyError.correctRef = "BoneSegments"
						MyError.correctlabel = 'Set Bone Segments to 1'
						
					if bone.use_inherit_scale == False:
						MyError = PotentialErrors.add()
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
					MyError.type = 2
					MyError.text = 'Object "'+obj.name+'" is an Armature and does not have any valid children.'

	def CheckVertexGroupWeight():
		#Check that all vertex have a weight
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				childs = GetExportDesiredChilds(obj)
				for child in childs:
					if child.type == "MESH":	
						#Prepare data
						VertexWithZeroWeight = 0
						for vertex in child.data.vertices:
							cumulateWeight = 0
							if len(vertex.groups) > 0:
								for group in vertex.groups:
									cumulateWeight += group.weight
								if not cumulateWeight > 0:
									VertexWithZeroWeight += 1							
							else:
								VertexWithZeroWeight += 1
						#Result data		
						if VertexWithZeroWeight > 0:
							MyError = PotentialErrors.add()
							MyError.type = 1
							MyError.text = 'Object named "'+child.name+'" contains '+str(VertexWithZeroWeight)+' vertex with zero cumulative weight.'
								
			
	def CheckZeroScaleKeyframe():
		#Check that animations do not use a invalid value
		for action in bpy.data.actions:
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
	CheckVertexGroupWeight()
	CheckZeroScaleKeyframe()
	return PotentialErrors

	
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
	#----------------------------------------
	print("Start correct")
	print("test START: "+error.correctRef)
	def SelectObj(obj):
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.context.scene.objects.active = obj
			
	
	#Correction list
	
	if error.correctRef == "ConvertToMesh":
		obj = error.object
		SelectObj(obj)
		bpy.ops.object.convert(target='MESH')
		successCorrect = True
		
	print("testA: "+error.correctRef)
	if error.correctRef == "SetKeyRangeMin":
		obj = error.object
		key = obj.data.shape_keys.key_blocks[error.itemName]
		key.slider_min = -5
		successCorrect = True
	
	print("testB: "+error.correctRef)
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
	bpy.ops.object.select_all(action='DESELECT')
	for obj in UserSelected: obj.select = True #Resets previous selected object
	scene.objects.active = UserActive #Resets previous active object
	if UserActive and UserMode and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode=UserMode) #Resets previous mode
	#----------------------------------------
		
	if successCorrect == True:
		scene.potentialErrorList.remove(errorIndex)
		print("end correct, Error: " + error.correctRef)
		scene.update()
		return "Corrected"
	print("end correct, Error not found")
	return "Correct fail"

	#Returns all assets that will be exported
	
	scene = bpy.context.scene
	TargetAassetToExport = [] #Obj, Action, type


	for obj in GetAllobjectsByExportType("export_recursive"):
		if GetAssetType(obj) == "SkeletalMesh":
			#SkeletalMesh
			if scene.skeletal_export:
				TargetAassetToExport.append((obj,None,"SkeletalMesh"))
			for action in GetActionToExport(obj):
				#Animation
				if scene.anin_export:
					if GetActionType(action) == "Animation":
						TargetAassetToExport.append((obj,action,"Animation"))
				#Pose
				if scene.pose_export:
					if GetActionType(action) == "Pose":
						TargetAassetToExport.append((obj,action,"Pose"))
		#Camera
		if GetAssetType(obj) == "Camera" and scene.camera_export:
			TargetAassetToExport.append((obj,None,"Camera"))

		#StaticMesh
		if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				TargetAassetToExport.append((obj,None,"StaticMesh"))

	return TargetAassetToExport
