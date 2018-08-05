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

# ----------------------------------------------
#  This addons allows to easily export several objects at the same time in .fbx
#  for use in unreal engine 4 by removing the usual constraints
#  while respecting UE4 naming conventions and a clean tree structure.
#  It also contains a small toolkit for collisions and sockets
#  xavierloux.com
# ----------------------------------------------

bl_info = {
	'name': 'Blender for UnrealEngine',
	'description': "This add-ons allows to easily export several "
	"objects at the same time for use in unreal engine 4.",
	'author': 'Loux Xavier (BleuRaven)',
	'version': (0, 1, 9.1),
	'blender': (2, 79, 0),
	'location': 'View3D > Tool > Unreal Engine 4',
	'warning': '',
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Blender_For_UnrealEngine",
	'tracker_url': '',
	'support': 'COMMUNITY',
	'category': 'Import-Export'}

import os
import bpy
import fnmatch
import math
import bmesh
from mathutils import Vector
from mathutils import Quaternion
from bpy import data as bpy_data
import time

from bpy.props import (
		StringProperty,
		BoolProperty,
		EnumProperty,
		IntProperty,
		BoolVectorProperty,
		CollectionProperty
		)
from bpy.types import Operator

#############################[Functions]#############################


def ChecksRelationship(arrayA, arrayB):
	#Checks if it exits an identical variable in two lists

	for a in arrayA:
		for b in arrayB:
			if a == b:
				return True
	return False


def GetHierarchyExportParent(obj):
	#Get parent "export_recursive" on the top of the hierarchy

	if obj.ExportEnum == "export_recursive":
		return obj
	pare = obj.parent
	if pare is not None:
		FinalObj = GetHierarchyExportParent(pare)
		return FinalObj
	else:
		return None


def GetChilds(obj):
	#Get all direct childs of a object

	ChildsObj = []
	for childObj in bpy.data.objects:
		pare = childObj.parent
		if pare is not None:
			if pare.name == obj.name:
				ChildsObj.append(childObj)

	return ChildsObj


def GetRecursiveChilds(obj):
	#Get all recursive childs of a object

	saveObj = []
	for newobj in GetChilds(obj):
		for childs in GetRecursiveChilds(newobj):
			saveObj.append(childs)
		saveObj.append(newobj)
	return saveObj


def GetExportDesiredChilds(obj):
	#Get only all child objects that must be exported with parent object

	DesiredObj = GetRecursiveChilds(obj)
	for unwantedObj in FindAllobjectsByExportType("dont_export"):
		try:
			DesiredObj.remove(unwantedObj)
		except:
			pass
	return DesiredObj


def SelectParentAndDesiredChilds(obj):
	#Selects only all child objects that must be exported with parent object

	bpy.ops.object.select_all(action='DESELECT')
	for selectObj in GetExportDesiredChilds(obj):
		selectObj.select = True
	obj.select = True
	bpy.context.scene.objects.active = obj


def GetAllCollisionAndSocketsObj():
	#Get any object that can be understood as a collision or a socket by unreal

	colObjs = [obj for obj in bpy.context.scene.objects if
		fnmatch.fnmatchcase(obj.name, "UBX*") or
		fnmatch.fnmatchcase(obj.name, "UCP*") or
		fnmatch.fnmatchcase(obj.name, "USP*") or
		fnmatch.fnmatchcase(obj.name, "UCX*") or
		fnmatch.fnmatchcase(obj.name, "SOCKET*")]
	return colObjs


def ResetArmaturePose(obj):
	#Reset armature pose

	for x in obj.pose.bones:
		x.rotation_quaternion = Quaternion((0,0,0),0)
		x.scale = Vector((1,1,1))
		x.location = Vector((0,0,0))


def VerifiDirs(directory):
	#Check and create a folder if it does not exist

	if not os.path.exists(directory):
		os.makedirs(directory)


def FindAllobjectsByExportType(exportType):
	#Find all objects with a specific ExportEnum property

	targetObj = []
	for obj in bpy.context.scene.objects:
		prop = obj.ExportEnum
		if prop == exportType:
			targetObj.append(obj)
	return(targetObj)


def GenerateUe4Name(name):
	#Generate a new name with suffix number

	def IsValidName(testedName):
		#Checks if an object uses this name. (If not is a valid name)

		for obj in bpy.context.scene.objects:
			if testedName == obj.name:
				return False
		return True

	valid = False
	number = 0
	newName = ""
	while valid == False:
		newName = name+"_"+str(number)
		if IsValidName(newName):
			valid = True
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
			acb = bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
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
		#Mesh
		if obj.type == 'MESH':
			if ownerObj is not None:
				if obj != ownerObj:
					ApplyConvexHull(obj)
					obj.modifiers.clear()
					obj.data
					obj.data.materials.clear()
					obj.data.materials.append(mat)
					obj.name = GenerateUe4Name(prefixName+ownerObj.name)
					obj.show_wire = True
					obj.show_transparent = True
					ConvertedObjs.append(obj)
		#Socket
		if obj.type == 'EMPTY' and collisionType == "Socket":
			if ownerObj is not None:
				if obj != ownerObj:
					obj.name = GenerateUe4Name("SOCKET_"+ownerObj.name)
					obj.scale = (0.01,0.01,0.01)
					obj.empty_draw_size = 100
					ConvertedObjs.append(obj)
	return ConvertedObjs


def GetActionToExport(obj):
	#Returns only the actions that will be exported with the object

	TargetActionToExport = []
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

	
def GetActionIsPose(action):
	#If this action is a pose return True

	if action.frame_range.y - action.frame_range.x == 1:
		return True
	return False

	
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
		

def FindPotentialError():
	#Return all potential error in scene

	PotentialError = []
	objToCheck = []
	for obj in FindAllobjectsByExportType("export_recursive"):
		objToCheck.append(obj)
		for obj2 in GetExportDesiredChilds(obj):
			objToCheck.append(obj2)

	def CheckExportObjType():
		for obj in objToCheck:
			if obj.type == "SURFACE" or obj.type == "META" or obj.type == "FONT":
				PotentialError.append("About object named \""+obj.name+'" ('+obj.type+') the types SURFACE, META and FONT is not recommended.')

	def CheckShapeKeysModifier():
		for obj in objToCheck:
			if obj.type == 'MESH':
				if obj.data.shape_keys is not None:
					if len(obj.data.shape_keys.key_blocks) > 0:
						for modif in obj.modifiers:
							if modif.type != "ARMATURE" :
								PotentialError.append("In object named \""+obj.name+"\" the modifier type ("+modif.type+") named \""+modif.name+"\" can destroy shape keys. Please use only Armature modifier with shape keys.")

	def CheckShapeKeysRange():
		for obj in objToCheck:
			if obj.type == 'MESH':
				if obj.data.shape_keys is not None:
					for key in obj.data.shape_keys.key_blocks:
						if key.slider_min < -5:
							PotentialError.append("In object named \""+obj.name+"\" the min range of the shape key named \""+key.name+"\" must not be inferior to -5.")
						if key.slider_max > 5:
							PotentialError.append("In object named \""+obj.name+"\" the max range of the shape key named \""+key.name+"\" must not be superior to 5.")

	def CheckUVMaps():
		def CheckIsCollision(target):
			for obj in GetAllCollisionAndSocketsObj():
				if obj == target:
					return True
			return False

		for obj in objToCheck:
			if not CheckIsCollision(obj):
				if obj.type == 'MESH':
					if len(obj.data.uv_layers) < 1:
						PotentialError.append("Object named \""+obj.name+"\" does not have any UV Layer.")


	def CheckBadStaicMeshExportedLikeSkeletalMesh():
		for obj in objToCheck:
			if obj.type == 'MESH':
				for modif in obj.modifiers:
					if modif.type == "ARMATURE" :
						if obj.ExportEnum == "export_recursive":
							PotentialError.append("In object named \""+obj.name+"\" the Armature modifier will not be applied when exported with StaticMesh assets.")

	def CheckArmatureNumber():
		for obj in objToCheck:
			if obj.type == 'MESH':
				ArmatureModifiers = 0
				for modif in obj.modifiers:
					if modif.type == "ARMATURE" :
						ArmatureModifiers = ArmatureModifiers + 1
				if ArmatureModifiers > 1:
					PotentialError.append("In object named \""+obj.name+"\" there are several Armature modifiers at the same time. Please use only one Armature modifier.")

	def CheckArmatureValidChild():
		for obj in objToCheck:
			if GetAssetType(obj) == "SkeletalMesh":
				childs = GetExportDesiredChilds(obj)
				validChild = 0
				for child in childs:
					if child.type == "MESH":
						validChild += 1
				if validChild < 1:
					PotentialError.append("The object named \""+obj.name+"\" is an Armature and does not have any valid children.")

	def CheckZeroScaleKeyframe():
		for action in bpy.data.actions:
			for fcurve in action.fcurves:
				if fcurve.data_path.split(".")[-1] == "scale":
					for key in fcurve.keyframe_points:
						xCurve, yCurve = key.co
						if key.co[1] == 0:
							PotentialError.append("In action named \""+action.name+"\" at frame "+str(key.co[0])+", bone named \""+fcurve.data_path.split('"')[1]+"\" has a zero value in scale transform. This is invalid in Unreal. ")

	def CheckCameraName():
		for obj in objToCheck:
			if obj.type == 'CAMERA':
				if not obj.name.startswith("Camera"):
					PotentialError.append("The object named \""+obj.name+"\" is a Camera and must be named \"Camera\" or have the prefix \"Camera\" to be understood by UE4.")

	def CheckDataCameraName():
		for obj in objToCheck:
			if obj.type == 'CAMERA':
				if not obj.name == obj.data.name:
					PotentialError.append("Concerning object named \""+obj.name+"\" it is recommended for UE4 to use the same name for the camera and the data camera. Currently the name of the data camera is \""+obj.data.name+"\".")

	CheckExportObjType()
	CheckShapeKeysModifier()
	CheckShapeKeysRange()
	CheckUVMaps()
	CheckBadStaicMeshExportedLikeSkeletalMesh()
	CheckArmatureNumber()
	CheckArmatureValidChild()
	CheckZeroScaleKeyframe()
	CheckCameraName()
	CheckDataCameraName()
	return PotentialError
		
		
def GetFinalAssetToExport():
	#Returns all assets that will be exported
	
	scene = bpy.context.scene

	TargetAassetToExport = [] #Obj, Action, type


	for obj in FindAllobjectsByExportType("export_recursive"):
		#SkeletalMesh
		if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
			TargetAassetToExport.append((obj,None,"SkeletalMesh"))
			for action in GetActionToExport(obj):
				#Animation
				if scene.anin_export:
					if GetActionIsPose(action) == False:
						TargetAassetToExport.append((obj,action,"Animation"))
				#Pose
				if scene.pose_export:
					if GetActionIsPose(action) == True:
						TargetAassetToExport.append((obj,action,"Pose"))
		#Camera
		if GetAssetType(obj) == "Camera" and scene.camera_export:
			TargetAassetToExport.append((obj,None,"Camera"))

		#StaticMesh
		if GetAssetType(obj) == "StaticMesh" and scene.static_export:
				TargetAassetToExport.append((obj,None,"StaticMesh"))

	#CameraPaked
	if scene.camera_pack_export:
		CameraList = []
		for obj in FindAllobjectsByExportType("export_recursive"):
			if obj.type == "CAMERA":
				CameraList.append("- "+obj.name)
		if len(CameraList) > 0:
			TargetAassetToExport.append((None, None,"CameraPaked"))

	#Others(CameraCuts)
	if scene.other_export:
		CameraCutsCode = GetCameraCutsCode()
		if CameraCutsCode is not None:
			TargetAassetToExport.append((None, None,"CameraCuts"))



	return TargetAassetToExport


def ExportSingleAnimation(obj, targetAction, dirpath, filename):
	#Export a single animation

	animType = "Animation"
	if GetActionIsPose(targetAction):
		animType = "Pose"

	if animType == "Pose" and bpy.context.scene.pose_export == False:
		return None
	if animType == "Animation" and bpy.context.scene.anin_export == False:
		return None

	curr_time = time.process_time()
	UserAction = obj.animation_data.action #Save current action
	bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	ResetArmaturePose(obj)
	obj.animation_data.action = targetAction #Apply desired action
	bpy.context.scene.frame_start = targetAction.frame_range.x #GetFirstActionFrame
	bpy.context.scene.frame_end = targetAction.frame_range.y #GetLastActionFrame

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
		bake_anim_step=bpy.context.scene.fbx_export_sample_anim,
		bake_anim_simplify_factor=bpy.context.scene.fbx_export_simplify_anim
		)
	obj.location = originalLoc #Resets previous object location
	ResetArmaturePose(obj)
	obj.animation_data.action = UserAction #Resets previous action
	exportTime = time.process_time()-curr_time
	return([filename,animType,absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]


def ExportSingleMesh(obj, dirpath, filename):
	#Export a single Mesh

	curr_time = time.process_time()
	bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save current object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	bpy.ops.export_scene.fbx(filepath=fullpath,
		check_existing=False,
		version='BIN7400',
		use_selection=True,
		mesh_smooth_type="FACE",
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=False
		)
	meshType = GetAssetType(obj)
	obj.location = originalLoc #Resets previous object location
	exportTime = time.process_time()-curr_time
	return([filename,meshType,absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]


def ExportCameraPaked(dirpath, filename):
	#Export camera paked

	curr_time = time.process_time()
	bpy.ops.object.mode_set(mode = 'OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	CameraList = []
	for obj in FindAllobjectsByExportType("export_recursive"):
		if obj.type == "CAMERA":
			CameraList.append(obj)

	if len(CameraList) > 0:
		for obj in CameraList:
			obj.select = True
			bpy.context.scene.objects.active = obj

		absdirpath = bpy.path.abspath(dirpath)
		VerifiDirs(absdirpath)
		fullpath = os.path.join( absdirpath , filename )

		bpy.ops.export_scene.fbx(
			filepath=fullpath,
			check_existing=False,
			version='BIN7400',
			use_selection=True,
			object_types={'CAMERA'},
			add_leaf_bones=False,
			use_armature_deform_only=obj.exportDeformOnly,
			bake_anim=True,
			bake_anim_use_nla_strips=False,
			bake_anim_use_all_actions=False,
			bake_anim_force_startend_keying=True,
			bake_anim_step=bpy.context.scene.fbx_export_sample_cam_anim,
			bake_anim_simplify_factor=bpy.context.scene.fbx_export_simplify_cam_anim,
			use_custom_props=True
			)

		exportTime = time.process_time()-curr_time
		return([filename,"CameraPacked",absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]
	return None


def ExportSingleCamera(obj, dirpath, filename):
	#Export single camera

	if obj.type != 'CAMERA':
		return;
	curr_time = time.process_time()
	bpy.ops.object.mode_set(mode = 'OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for selectObj in GetExportDesiredChilds(obj):
		selectObj.select = True
	obj.select = True
	bpy.context.scene.objects.active = obj

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	bpy.ops.export_scene.fbx(
		filepath=fullpath,
		check_existing=False,
		version='BIN7400',
		use_selection=True,
		object_types={'CAMERA'},
		add_leaf_bones=False,
		use_armature_deform_only=obj.exportDeformOnly,
		bake_anim=True,
		bake_anim_use_nla_strips=False,
		bake_anim_use_all_actions=False,
		bake_anim_force_startend_keying=True,
		bake_anim_step=bpy.context.scene.fbx_export_sample_cam_anim,
		bake_anim_simplify_factor=bpy.context.scene.fbx_export_simplify_cam_anim,
		use_metadata=True
		)

	exportTime = time.process_time()-curr_time
	return([filename,"Camera",absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]


def ExportSingleText(text, dirpath, filename):
	#Export single text

	curr_time = time.process_time()

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	with open(fullpath, "w") as file:
		file.write(text)

	exportTime = time.process_time()-curr_time
	return([filename,"TextFile",absdirpath,exportTime]) #[AssetName , AssetType , ExportPath, ExportTime]


def ExportAllByList(targetobjects):
	#Export all objects that need to be exported from a list
	
	scene = bpy.context.scene
	wm = bpy.context.window_manager
	wm.progress_begin(0, len(GetFinalAssetToExport()))

	exportedAssets = [] #List of exported objects [AssetName , AssetType , ExportPath, ExportTime]
	def AppendExportedAsset(asset):
		exportedAssets.append(asset)
		wm.progress_update(len(exportedAssets))
	if len(targetobjects) > 0:
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

		if bpy.context.object is None:
			scene.objects.active = bpy.data.objects[0]

		UserMode = bpy.context.object.mode #Save current mode
		UserActive = bpy.context.active_object #Save current active object
		UserSelected = bpy.context.selected_objects #Save current selected objects

		#----------------------------------------

		smPrefix = scene.static_prefix_export_name
		skPrefix = scene.skeletal_prefix_export_name
		animPrefix = scene.anim_prefix_export_name
		camPrefix = scene.camera_prefix_export_name

		for obj in targetobjects:
			if obj.ExportEnum == "export_recursive":

				#SkeletalMesh
				if GetAssetType(obj) == "SkeletalMesh" and scene.skeletal_export:
					exportDir = os.path.join( scene.export_skeletal_file_path , obj.exportFolderName , obj.name )
					AppendExportedAsset(ExportSingleMesh(obj, exportDir, skPrefix+obj.name+".fbx"))

					UserStartFrame = scene.frame_start #Save current start frame
					UserEndFrame = scene.frame_end #Save current end frame

					#Animation and pose
					for action in GetActionToExport(obj):
						animExportDir = os.path.join( exportDir, "Anim" )
						animFilename = animPrefix+obj.name+"_"+action.name+".fbx"
						AppendExportedAsset(ExportSingleAnimation(obj, action, animExportDir, animFilename))

						scene.frame_start = UserStartFrame #Resets previous start frame
						scene.frame_end = UserEndFrame #Resets previous end frame

				#Camera
				if GetAssetType(obj) == "Camera" and scene.camera_export:
					exportDir = os.path.join( scene.export_camera_file_path, obj.exportFolderName )
					AppendExportedAsset(ExportSingleCamera(obj, exportDir, camPrefix+obj.name+".fbx"))

				#StaticMesh
				if GetAssetType(obj) == "StaticMesh" and scene.static_export:
					exportDir = os.path.join( scene.export_static_file_path, obj.exportFolderName )
					AppendExportedAsset(ExportSingleMesh(obj, exportDir, smPrefix+obj.name+".fbx"))

		#CameraPaked
		if scene.camera_pack_export:
			exportDir = os.path.join( scene.export_camera_file_path)
			AppendExportedAsset(ExportCameraPaked(exportDir, camPrefix+"SceneCameraPacked"+".fbx"))

		#Other(CameraCuts)
		if scene.other_export:
			CameraCutsCode = GetCameraCutsCode()
			if CameraCutsCode is not None:
				CutFilename = "Ue4Sequencer_CameraCuts.txt"
				AppendExportedAsset(ExportSingleText(CameraCutsCode, scene.export_camera_file_path, CutFilename))
		#----------------------------------------Reset data
		for x in range(20):
			scene.layers[x] = LayerVisibility[x]
		bpy.ops.object.select_all(action='DESELECT')
		for obj in UserSelected: obj.select = True #Resets previous active object
		scene.objects.active = UserActive #Resets previous active object
		if bpy.context.object is not None:
			if bpy.context.object is None:
				bpy.ops.object.mode_set(mode = UserMode) #Resets previous mode
		for x, obj in enumerate(scene.objects):
			obj.hide = UserObjHide[x] #Resets previous object visibility
			obj.hide_select = UserObjHideSelect[x] #Resets previous object visibility(select)
		#----------------------------------------
	wm.progress_end()
	return exportedAssets


def GetCameraCutsCode():
	#Generate a CutsCode text for paste in Unreal
	scene = bpy.context.scene
	markers = scene.timeline_markers
	markersOrderly = []
	def addSection(markerName, CutNumber, StartTime, EndTime):
		
		print("Section("+str(CutNumber)+") = \""+markerName+"\"")
		sectionName = 'BlenderSceneMarker_'+markerName+"_"+str(CutNumber)
		def GetSectionClass():
			secClass = '   Begin Object Class=/Script/MovieSceneTracks.MovieSceneCameraCutSection '
			secClass += 'Name="'+sectionName+'"'+"\n"
			secClass += '   End Object'+"\n"
			return secClass

		def GetSectionProp(): #Property
			prop = '   Begin Object Name="'+sectionName+'"'+"\n"
			prop += "      StartTime="+str(StartTime)+"\n"
			prop += "      EndTime="+str(EndTime)+"\n"
			prop += '   End Object'+"\n"
			return prop
		def GetSectionIndex():
			secIndex = "   Sections("+str(CutNumber)+")=MovieSceneCameraCutSection'\""
			secIndex += sectionName+"\"'"+"\n"
			return secIndex
		return (GetSectionClass(),GetSectionProp(),GetSectionIndex())

	#Start code
	CopyScript = 'Begin Object Class=/Script/MovieSceneTracks.MovieSceneCameraCutTrack Name="CameraCuts"' + "\n"
	sectionCuts = []
	for x in range(scene.frame_start, scene.frame_end+1):
		for marker in markers:
			if marker.frame == x:
				markersOrderly.append(marker)


	for x in range(len(markersOrderly)):
		if scene.frame_end > markersOrderly[x].frame:
			startTime = markersOrderly[x].frame/scene.render.fps
			if x+1 != len(markersOrderly):
				EndTime = markersOrderly[x+1].frame/scene.render.fps
			else:
				EndTime = bpy.context.scene.frame_end/scene.render.fps
			sectionCuts.append(addSection(markersOrderly[x].name ,x, startTime, EndTime))
	
	for section in sectionCuts:
		CopyScript += section[0]
		CopyScript += section[1]
		CopyScript += section[2]
	CopyScript += "End Object"
	if len(sectionCuts) < 1:
		return None
	return CopyScript


def UpdateExportActionList():
	#Update the provisional action list known by the object

	def SetUseFromLast(list, ActionName):
		for item in list:
			if item[0] == ActionName:
				if item[1] == True:
					return True
		return False

	AnimSave = [["", False]]
	for Anim in bpy.context.object.exportActionList: #CollectionProperty
		name = Anim.name
		use = Anim.use
		AnimSave.append([name, use])
	bpy.context.object.exportActionList.clear()
	for action in bpy.data.actions:
		bpy.context.object.exportActionList.add().name = action.name
		bpy.context.object.exportActionList[action.name].use = SetUseFromLast(AnimSave, action.name)

#############################[Visual and UI]#############################


class ue4PropertiesPanel(bpy.types.Panel):
	#Is Object Properties panel

	bl_idname = "panel.ue4.obj-properties"
	bl_label = "Object Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class UpdateObjActionButton(bpy.types.Operator):
		bl_label = "Update action list"
		bl_idname = "object.updateobjaction"
		bl_description = "Update action list"

		def execute(self, context):
			UpdateExportActionList()
			return {'FINISHED'}

	class ShowActionToExport(bpy.types.Operator):
		bl_label = "Show action(s)"
		bl_idname = "object.showobjaction"
		bl_description = "Click to show actions that are to be exported with this armature."

		def execute(self, context):
			obj = context.object
			actions = GetActionToExport(obj)
			popup_title = "Action list"
			if len(actions) > 1:
				popup_title = str(len(actions))+' action(s) found for obj named "'+obj.name+'".'
			else:
				popup_title = 'No actions found for obj named "'+obj.name+'".'

			def draw(self, context):
				col = self.layout.column()
				for action in actions:
					action_type = " (Animation)"
					if GetActionIsPose(action):
						action_type = " (Pose)"
					row = col.row()
					row.label("- "+action.name+action_type)
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='ACTION')
			return {'FINISHED'}


	class ACTION_UL_ExportTarget(bpy.types.UIList):
		def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
			ActionIsValid = False
			try:
				bpy.data.actions[item.name]
				ActionIsValid = True
			except:
				pass

			if self.layout_type in {'DEFAULT', 'COMPACT'}:
				if ActionIsValid: #If action is valid
					#layout.prop(item, "name", text="", emboss=False, icon="ACTION") #Debug only for see target line
					layout.prop(bpy.data.actions[item.name], "name", text="", emboss=False, icon="ACTION")
					layout.prop(item, "use", text="")
				else:
					dataText = ('Action data named "' + item.name + '" Not Found. Please clic on update')
					layout.label(text=dataText, icon="ERROR")
			# Not optimised for 'GRID' layout type.
			elif self.layout_type in {'GRID'}:
				layout.alignment = 'CENTER'
				layout.label(text="", icon_value=icon)


	class ObjExportAction(bpy.types.PropertyGroup):
		name = StringProperty(name="Action data name", default="Unknown")
		use = BoolProperty(name="use this action", default=False)

	bpy.utils.register_class(ACTION_UL_ExportTarget)
	bpy.utils.register_class(ObjExportAction)

	bpy.types.Object.ExportEnum = EnumProperty(
		name = "Export type",
		description	 = "Export procedure",
		items = [
			("auto", "Auto", "Exports only if one of the parents is \"Export recursive\"", "KEY_HLT", 1),
			("export_recursive", "Export recursive", "Export self object and all children", "KEYINGSET", 2),
			("dont_export", "Not exported", "Will never export", "KEY_DEHLT", 3)
			]
		)
	bpy.types.Object.ForceStaticMesh = BoolProperty(
		name="Force staticMesh",
		description="Force export asset like a StaticMesh.",
		default=False
		)

	bpy.types.Object.exportActionEnum = EnumProperty(
		name = "Export action types",
		description	 = "Export procedure for actions (Animations and poses)",
		items = [
			("export_auto", "Export auto", "Export all actions connected to the bones names", "FILE_SCRIPT", 1),
			("export_specific_list", "Export specific list", "Export only actions that are checked in the list", "LINENUMBERS_ON", 2),
			("export_specific_prefix", "Export specific prefix", "Export only actions with a specific prefix or the beginning of the actions names", "SYNTAX_ON", 3),
			("dont_export", "Not exported", "No action will be exported", "MATPLANE", 4)
			]
		)

	bpy.types.Object.exportFolderName = StringProperty(
		name = "Sub folder name",
		description	 = 'Sub folder name. No Sub folder created if left empty',
		maxlen = 64,
		default = "",
		subtype = 'FILE_NAME'
		)

	bpy.types.Object.exportDeformOnly = BoolProperty(
		name="Export only deform Bones",
		description="Only write deforming bones (and non-deforming ones when they have deforming children)",
		default=True
		)

	#properties used with ""export_specific_list" on exportActionEnum
	bpy.types.Object.exportActionList = CollectionProperty(
		type=ObjExportAction
		)

	bpy.types.Object.active_ObjectAction = IntProperty(
		name="Active Scene Action",
		description="Index of the currently active object action",
		default=0
		)

	#properties used with ""export_specific_prefix" on exportActionEnum
	bpy.types.Object.PrefixNameToExport = StringProperty(
		name = "Prefix name",
		description	 = "Indicate the prefix of the actions that must be exported",
		maxlen = 32,
		default = "Example_",
		)

	def draw(self, context):


		layout = self.layout
		row = layout.row()
		column = layout.column()
		obj = context.object
		if obj is not None:

			AssetType = row
			AssetType.label('', icon='OBJECT_DATA') #Show asset type
			AssetType.prop(obj, 'name', text="")
			AssetType.label('('+ GetAssetType(obj)+')') #Show asset type
			if obj.type == "ARMATURE":
				AssetType2 = layout.column()
				AssetType2.prop(obj, "ForceStaticMesh") #Show asset type
			ExportType = layout.column()
			ExportType.prop(obj, 'ExportEnum')

			if obj.ExportEnum == "export_recursive":
				if GetAssetType(obj) == "SkeletalMesh":
					armatureProperty = layout.column()
					armatureProperty.prop(obj, 'exportActionEnum')
					if obj.exportActionEnum == "export_specific_list":
						armatureProperty.template_list(
							"ACTION_UL_ExportTarget", "",  # type and unique id
							obj, "exportActionList",  # pointer to the CollectionProperty
							obj, "active_ObjectAction",	 # pointer to the active identifier
							maxrows=5,
							rows=5
						)
						armatureProperty.operator("object.updateobjaction", icon='RECOVER_LAST')
					if obj.exportActionEnum == "export_specific_prefix":
						armatureProperty.prop(obj, 'PrefixNameToExport')


					armatureProperty.prop(obj, 'exportDeformOnly')
				folderNameProperty = layout.column()
				folderNameProperty.prop(obj, 'exportFolderName')
				if GetAssetType(obj) == "SkeletalMesh":
					ActionNum = len(GetActionToExport(obj))
					armaturePropertyInfo = layout.row().box().split(percentage = 0.75 )
					actionFeedback = str(ActionNum) + " Action(s) will be exported with this armature."
					armaturePropertyInfo.label( actionFeedback, icon='INFO')
					armaturePropertyInfo.operator("object.showobjaction")


		else:
			layout.label('Pleas select obj for show properties.')


class ue4CollisionsAndSocketsPanel(bpy.types.Panel):
	#Is Collisions And Sockets panel

	bl_idname = "panel.ue4.collisionsandsockets"
	bl_label = "Collisions And Sockets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class ConvertToUECollisionButtonBox(bpy.types.Operator):
		bl_label = "Convert to box (UBX)"
		bl_idname = "object.converttoboxcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Boxes type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Box", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Box collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonCapsule(bpy.types.Operator):
		bl_label = "Convert to capsule (UCP)"
		bl_idname = "object.converttocapsulecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Capsules type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Capsule", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Capsule collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonSphere(bpy.types.Operator):
		bl_label = "Convert to sphere (USP)"
		bl_idname = "object.converttospherecollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Spheres type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Sphere", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Sphere collisions." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUECollisionButtonConvex(bpy.types.Operator):
		bl_label = "Convert to convex shape (UCX)"
		bl_idname = "object.converttoconvexcollision"
		bl_description = "Convert selected mesh(es) to Unreal collision ready for export (Convex shapes type)"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Convex", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to UE4 Convex Shape collisions.")
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}


	class ConvertToUESocketButton(bpy.types.Operator):
		bl_label = "Convert to socket (SOCKET)"
		bl_idname = "object.converttosocket"
		bl_description = "Convert selected Empty(s) to Unreal sockets ready for export"

		def execute(self, context):
			ConvertedObj = ConvertToUe4SubObj("Socket", bpy.context.selected_objects, True)
			if len(ConvertedObj) > 0 :
				self.report({'INFO'}, str(len(ConvertedObj)) + " object(s) of the selection have be converted to to UE4 Socket." )
			else :
				self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
			return {'FINISHED'}

	def draw(self, context):

		def FoundTypeInSelect(targetType): #Return True is a specific type is found
			for obj in bpy.context.selected_objects:
				if obj.type == targetType:
					return True
			return False

		self.layout.label("Convert selected object to Unreal collision or socket (Static Mesh only)", icon='PHYSICS')

		convertMeshButtons = self.layout.row().split(percentage = 0.80 )
		convertMeshButtons = convertMeshButtons.column()
		convertMeshButtons.enabled = FoundTypeInSelect("MESH")
		convertMeshButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
		convertMeshButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
		convertMeshButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
		convertMeshButtons.operator("object.converttospherecollision", icon='SOLID')

		convertMeshButtons = self.layout.row().split(percentage = 0.80 )
		convertEmptyButtons = convertMeshButtons.column()
		convertEmptyButtons.enabled = FoundTypeInSelect("EMPTY")
		convertEmptyButtons.operator("object.converttosocket", icon='OUTLINER_DATA_EMPTY')


class ue4CheckCorrectPanel(bpy.types.Panel):
	#Is Check and correct panel

	bl_idname = "panel.ue4.CheckCorrect"
	bl_label = "Check and correct"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class CheckPotentialErrorButton(bpy.types.Operator):
		bl_label = "Check potential errors"
		bl_idname = "object.checkpotentialerror"
		bl_description = "Check potential errors"

		def execute(self, context):

			potentialerrors = FindPotentialError()
			if len(potentialerrors) > 0 :
				for error in potentialerrors:
					self.report({'WARNING'}, "WARNING: "+error)
			else:
				self.report({'INFO'}, "No potential error to correct!")
			return {'FINISHED'}


	class CorrectBadPropertyButton(bpy.types.Operator):
		bl_label = "Correct bad properties"
		bl_idname = "object.correctproperty"
		bl_description = "Corrects bad properties"

		def execute(self, context):
			def CorrectBadProperty():

				correctedProperty = 0
				for obj in GetAllCollisionAndSocketsObj():
					if obj.ExportEnum == "export_recursive":
						obj.ExportEnum = "auto"
						correctedProperty = correctedProperty + 1

				return correctedProperty
			corrected = CorrectBadProperty()
			if corrected > 0 :
				self.report({'INFO'}, str(corrected) + " properties corrected")
			else:
				self.report({'INFO'}, "No properties to correct!")
			return {'FINISHED'}

	class UpdateNameHierarchyButton(bpy.types.Operator):
		bl_label = "Update hierarchy names"
		bl_idname = "object.correcthierarchy"
		bl_description = "Updates hierarchy names"

		def execute(self, context):
			def UpdateNameHierarchy():

				for obj in GetAllCollisionAndSocketsObj():
					if fnmatch.fnmatchcase(obj.name, "UBX*"):
						ConvertToUe4SubObj("Box", [obj])
					if fnmatch.fnmatchcase(obj.name, "UCP*"):
						ConvertToUe4SubObj("Capsule", [obj])
					if fnmatch.fnmatchcase(obj.name, "USP*"):
						ConvertToUe4SubObj("Sphere", [obj])
					if fnmatch.fnmatchcase(obj.name, "UCX*"):
						ConvertToUe4SubObj("Convex", [obj])
					if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
						ConvertToUe4SubObj("Socket", [obj])
			UpdateNameHierarchy()
			self.report({'INFO'}, "Hierarchy names updated!")
			return {'FINISHED'}


	def draw(self, context):
		button = self.layout.row()
		button = button.column()
		button.operator("object.checkpotentialerror", icon='QUESTION')
		button.operator("object.correctproperty", icon='FILE_TICK')
		button.operator("object.correcthierarchy", icon='OOPS')


class ue4FbxExportPanel(bpy.types.Panel):
	#Is FPS Export panel

	bl_idname = "panel.ue4.exportfbx"
	bl_label = "Export (FBX property)"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	#Animation :
	bpy.types.Scene.fbx_export_sample_anim = bpy.props.FloatProperty(
		name="Sampling Rate",
		description="How often to evaluate animated values (in frames)",
		min=0.01, max=100.0,
		soft_min=0.01, soft_max=100.0,
		default=1.0,
		)
	bpy.types.Scene.fbx_export_simplify_anim = bpy.props.FloatProperty(
		name="Simplify animations",
		description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
		min=0.0, max=100.0,	 # No simplification to up to 10% of current magnitude tolerance.
		soft_min=0.0, soft_max=10.0,
		default=1.0,
		)

	bpy.types.Scene.fbx_export_sample_cam_anim = bpy.props.FloatProperty(
		name="Sampling Rate (Camera)",
		description="How often to evaluate animated values (in frames)",
		min=0.01, max=100.0,
		soft_min=0.01, soft_max=100.0,
		default=0.8,
		)
	bpy.types.Scene.fbx_export_simplify_cam_anim = bpy.props.FloatProperty(
		name="Simplify animations (Camera)",
		description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
		min=0.0, max=100.0,	 # No simplification to up to 10% of current magnitude tolerance.
		soft_min=0.0, soft_max=10.0,
		default=1.0,
		)

	#Nomenclature :
	bpy.types.Scene.static_prefix_export_name = bpy.props.StringProperty(
		name = "StaticMesh Prefix",
		description	 = "Prefix of staticMesh",
		maxlen = 32,
		default = "SM_")

	bpy.types.Scene.skeletal_prefix_export_name = bpy.props.StringProperty(
		name = "SkeletalMesh Prefix ",
		description	 = "Prefix of SkeletalMesh",
		maxlen = 32,
		default = "SK_")

	bpy.types.Scene.anim_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence Prefix",
		description	 = "Prefix of AnimationSequence",
		maxlen = 32,
		default = "Anim_")

	bpy.types.Scene.pose_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence(Pose) Prefix",
		description	 = "Prefix of AnimationSequence with only one frame",
		maxlen = 32,
		default = "Pose_")

	bpy.types.Scene.camera_prefix_export_name = bpy.props.StringProperty(
		name = "Camera anim Prefix",
		description	 = "Prefix of camera animations",
		maxlen = 32,
		default = "Cam_")

	bpy.types.Scene.export_static_file_path = bpy.props.StringProperty(
		name = "StaticMesh export file path",
		description = "Choose a directory to export StaticMesh(s)",
		maxlen = 512,
		default = "//ExportedFbx\StaticMesh\\",
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_skeletal_file_path = bpy.props.StringProperty(
		name = "SkeletalMesh export file path",
		description = "Choose a directory to export SkeletalMesh(s)",
		maxlen = 512,
		default = "//ExportedFbx\SkeletalMesh\\",
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_camera_file_path = bpy.props.StringProperty(
		name = "Camera export file path",
		description = "Choose a directory to export Camera(s)",
		maxlen = 512,
		default = "//ExportedFbx\Sequencer\\",
		subtype = 'DIR_PATH')


	def draw(self, context):
		scn = context.scene

		propsFbx = self.layout.row()
		propsFbx = propsFbx.column()

		#Animation :
		split = propsFbx.split(percentage=0.5)
		propsFbx = split.column()
		propsFbx.prop(scn, 'fbx_export_sample_anim')
		propsFbx.prop(scn, 'fbx_export_simplify_anim')
		split = split.split(percentage=1)
		propsFbx = split.column()
		propsFbx.prop(scn, 'fbx_export_sample_cam_anim')
		propsFbx.prop(scn, 'fbx_export_simplify_cam_anim')

		#Nomenclature :
		propsPrefix = self.layout.row()
		propsPrefix = propsPrefix.column()
		propsPath = self.layout.row()
		propsPath = propsPath.column()

		propsPrefix.prop(scn, 'static_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'skeletal_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'anim_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'pose_prefix_export_name', icon='OBJECT_DATA')
		propsPrefix.prop(scn, 'camera_prefix_export_name', icon='OBJECT_DATA')
		propsPath.prop(scn, 'export_static_file_path')
		propsPath.prop(scn, 'export_skeletal_file_path')
		propsPath.prop(scn, 'export_camera_file_path')

class ue4ExportPanel(bpy.types.Panel):
	#Is Export panel

	bl_idname = "panel.ue4.export"
	bl_label = "Export"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	class ShowAssetToExport(bpy.types.Operator):
		bl_label = "Show asset(s)"
		bl_idname = "object.showasset"
		bl_description = "Click to show assets that are to be exported."

		def execute(self, context):
			obj = context.object
			assets = GetFinalAssetToExport()
			popup_title = "Assets list"
			if len(assets) > 1:
				popup_title = str(len(assets))+' asset(s) will be exported.'
			else:
				popup_title = 'No exportable assets were found.'

			def draw(self, context):
				col = self.layout.column()
				for asset in assets:
					row = col.row()
					if asset[0] is not None:
						if asset[1] is not None:
							row.label("		   --> "+asset[1].name+" ("+asset[2]+")")
						else:
							row.label("- "+asset[0].name+" ("+asset[2]+")")
					else:
						row.label("- ("+asset[2]+")")
			bpy.context.window_manager.popup_menu(draw, title=popup_title, icon='EXTERNAL_DATA')
			return {'FINISHED'}

	class ExportForUnrealEngineButton(bpy.types.Operator):
		bl_label = "Export for UnrealEngine 4"
		bl_idname = "object.exportforunreal"
		bl_description = "Export all assets of this scene."

		def execute(self, context):
			def GetIfOneTypeCheck():
				Scene = bpy.context.scene
				if Scene.static_export or Scene.skeletal_export or Scene.anin_export or Scene.pose_export or Scene.camera_export or Scene.camera_pack_export or Scene.other_export:
					return True
				else:
					return False

			def GetNumberWith(exportedAssets, targetName):
				foundNumber = 0
				for assets in exportedAssets:
					if assets[1] == targetName:
						foundNumber = foundNumber + 1
				return foundNumber

			def	GetValidOnly(Array):
				GoodArray=[]
				for item in Array:
					if item is not None:
						GoodArray.append(item)
				return GoodArray

			if GetIfOneTypeCheck():
				#Primary check  if file is saved to avoid windows PermissionError  
				if bpy.data.is_saved:
					curr_time = time.process_time()
					#Return [AssetName , AssetType , ExportPath, ExportTime]
					exportedAssets = GetValidOnly(ExportAllByList(FindAllobjectsByExportType("export_recursive")))
					if len(exportedAssets) > 0:
						self.report({'INFO'}, "Export of "+str(len(exportedAssets))+
						" asset(s) has been finalized in "+str(time.process_time()-curr_time)+" sec. Look in console for more info.")

						print ("========================= Exported asset(s) =========================")
						print ("")
						for asset in exportedAssets:
							print("["+asset[1]+"] -> "+"\""+asset[0]+"\" exported in "+str(asset[3])+" sec.")
							print(asset[2])
							print("--------------")
						print ("")
						print ("------------------------------------------")
						print ("")
						StaticNum = GetNumberWith(exportedAssets,"StaticMesh")
						SkeletalNum = GetNumberWith(exportedAssets,"SkeletalMesh")
						AnimNum = GetNumberWith(exportedAssets,"Animation")
						PoseNum = GetNumberWith(exportedAssets,"Pose")
						OtherNum = len(exportedAssets)-(StaticNum+SkeletalNum+AnimNum+PoseNum)
						print ("-> "+str(StaticNum)+" StaticMesh(s) | "+str(SkeletalNum)+" SkeletalMesh(s) | "+str(AnimNum)+" Animation(s) | "+str(PoseNum)+" Pose(s) | "+str(OtherNum)+" Other(s)")
						print ("")
						print ("========================= Exported asset(s) =========================")
						print ("")
					else:
						self.report({'WARNING'}, "Not found assets. with \"Export and child\" properties.")
						self.report({'WARNING'}, "No asset type is checked.")
				else:
					self.report({'WARNING'}, "Please save this blend file before export")
			else:
				self.report({'WARNING'}, "No asset type is checked.")
			return {'FINISHED'}


	class CopyCameraCutsButton(bpy.types.Operator):
		bl_label = "Copy Camera Cuts to clipboard"
		bl_idname = "object.copycameracuts"
		bl_description = "Copies Camera Cuts to clipboard. You can paste them into the Camera Cuts of UE4 Sequencer."


		def execute(self, context):
			Copy = GetCameraCutsCode()
			if Copy is not None:
				bpy.context.window_manager.clipboard = Copy
				self.report({'INFO'}, "Camera cuts code set to clipboard! (You can paste it in ue4 sequencer)")
			else:
				self.report({'WARNING'}, "WARNING: No marker found in scene frame range ")
			return {'FINISHED'}


	#Categories :
	bpy.types.Scene.static_export = bpy.props.BoolProperty(
		name = "StaticMesh(s)",
		description = "Check mark to export StaticMesh(es)",
		default = True
		)

	bpy.types.Scene.skeletal_export = bpy.props.BoolProperty(
		name = "SkeletalMesh(s)",
		description = "Check mark to export SkeletalMesh(es)",
		default = True
		)

	bpy.types.Scene.anin_export = bpy.props.BoolProperty(
		name = "Animation(s)",
		description = "Check mark to export Animation(s)",
		default = True
		)

	bpy.types.Scene.pose_export = bpy.props.BoolProperty(
		name = "Pose(s)",
		description = "Check mark to export Pose(s)",
		default = True
		)

	bpy.types.Scene.camera_export = bpy.props.BoolProperty(
		name = "Camera(s)",
		description = "Check mark to export Camera(s)",
		default = False
		)

	bpy.types.Scene.camera_pack_export = bpy.props.BoolProperty(
		name = "Camera packed",
		description = "Check mark to export Camera(s) in one pack",
		default = True
		)

	bpy.types.Scene.other_export = bpy.props.BoolProperty(
		name = "Other (CameraCuts)",
		description = "Check mark to export other assets (CameraCuts)",
		default = True
		)


	def draw(self, context):
		scn = context.scene

		#Categories :
		layout = self.layout
		selectType = layout.row()
		selectType = selectType.column()
		selectType.label("Asset types to export", icon='EXTERNAL_DATA')
		selectType.prop(scn, 'static_export')
		selectType.prop(scn, 'skeletal_export')
		sequence = selectType.column()
		sequence.active = bpy.context.scene.skeletal_export
		sequence.prop(scn, 'anin_export')
		sequence.prop(scn, 'pose_export')
		selectType.prop(scn, 'camera_export')
		selectType.prop(scn, 'camera_pack_export')
		selectType.prop(scn, 'other_export')

		#Feedback info :
		AssetNum = len(GetFinalAssetToExport())
		AssetInfo = layout.row().box().split(percentage = 0.75 )
		AssetFeedback = str(AssetNum) + " Asset(s) will be exported."
		AssetInfo.label( AssetFeedback, icon='INFO')
		AssetInfo.operator("object.showasset")
		#Export button :
		button = self.layout.row()
		button = button.column()
		button.operator("object.exportforunreal", icon='EXPORT')
		button.operator("object.copycameracuts", icon='COPYDOWN')


#############################[...]#############################


def register():

	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_prop = bpy.props.StringProperty(default="default value")


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()