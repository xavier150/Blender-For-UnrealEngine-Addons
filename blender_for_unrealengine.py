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
	'version': (0, 1, 8),
	'blender': (2, 79, 0),
	'location': 'View3D > Tool > Unreal Engine 4',
	'warning': '',
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
				"Scripts/Import-Export/Blender_For_UnrealEngine",
	'tracker_url': '',
	'support': 'COMMUNITY',
	'category': 'Import-Export'}

import os
from mathutils import Vector
from mathutils import Quaternion
import bpy
import fnmatch
from bpy.props import *
from bpy.types import Operator
import math
import mathutils
from bpy import data as bpy_data
import time

#############################[Debug variables]#############################

UseRealExport = True

#############################[Functions]#############################


def ChecksRelationship(arrayA, arrayB): #Checks if it exits an identical variable in two lists
	for a in arrayA:
		for b in arrayB:
			if a == b:
				return True
	return False

	
def GetHierarchyExportParent(obj): #Get first parent export in hierarchy
	

	if obj.ExportEnum == "export_and_childs":
		return obj
	pare = obj.parent
	if pare is not None:		
		FinalObj = GetHierarchyExportParent(pare)
		return FinalObj
	else:
		return None

def GetChilds(obj): #Get all direct childs of a object
	ChildsObj = []
	for childObj in bpy.data.objects:
		pare = childObj.parent
		if pare is not None:
			if pare.name == obj.name:
				ChildsObj.append(childObj)

	return ChildsObj


def GetRecursiveChilds(obj): #Get all recursive childs of a object
	saveObj = []
	for newobj in GetChilds(obj):
		for childs in GetRecursiveChilds(newobj):
			saveObj.append(childs)
		saveObj.append(newobj)
	return saveObj

def GetDesiredChilds(obj): #Get only all child objects that must be exported with parent objet
	DesiredObj = GetRecursiveChilds(obj)
	for unwantedObj in FindAllObjetsByExportType("dont_export"):
		try:
			DesiredObj.remove(unwantedObj)
		except:
			pass
	return DesiredObj


def SelectParentAndDesiredChilds(obj): #Selects only all child objects that must be exported with parent objet
	bpy.ops.object.select_all(action='DESELECT')
	for selectObj in GetDesiredChilds(obj):
		selectObj.select = True
	obj.select = True
	bpy.context.scene.objects.active = obj


def ResetArmaturePose(obj): #Reset armature pose
	for x in obj.pose.bones:
		x.rotation_quaternion = Quaternion((0,0,0),0)
		x.scale = Vector((1,1,1))
		x.location = Vector((0,0,0))


def VerifiDirs(directory): #check and create a folder if it does not exist
	if not os.path.exists(directory):
		os.makedirs(directory)


def ExportSingleAnimation(obj, targetAction, dirpath, filename): #Export a single animation
	def GetLastActionFrame(action):
		keyframes = []
		LastFrames = 0
		for fcu in action.fcurves:
			for keyframe in fcu.keyframe_points:
				xCurve, yCurve = keyframe.co
				keyframes.append(xCurve)
		for frame in keyframes:
			if frame > LastFrames:
				LastFrames = frame
		return LastFrames

	curr_time = time.process_time()
	
	if obj.type == 'ARMATURE':
		UserAction = obj.animation_data.action #Save current action
		bpy.ops.object.mode_set(mode = 'OBJECT')
		originalLoc = Vector((0,0,0))
		originalLoc = originalLoc + obj.location #Save objet location
		
		obj.location = (0,0,0) #Moves object to the center of the scene for export

		SelectParentAndDesiredChilds(obj)
		
		ResetArmaturePose(obj)
		obj.animation_data.action = targetAction #Apply desired action
		bpy.context.scene.frame_start = 0
		bpy.context.scene.frame_end = max(GetLastActionFrame(targetAction),1) #Set end_frame on the final key the current action
		
		
		absdirpath = bpy.path.abspath(dirpath)
		VerifiDirs(absdirpath)
		fullpath = os.path.join( absdirpath , filename )
		
		if UseRealExport == True:
			bpy.ops.export_scene.fbx(
				filepath=fullpath,
				check_existing=False,
				version='BIN7400',
				use_selection=True,
				object_types={'ARMATURE', 'MESH'},
				add_leaf_bones=False,
				use_armature_deform_only=bpy.context.scene.fbx_export_deform_only,
				bake_anim=True,
				bake_anim_use_nla_strips=False,
				bake_anim_use_all_actions=False,
				bake_anim_force_startend_keying=True,
				bake_anim_simplify_factor=bpy.context.scene.fbx_export_simplify_anim
				)
		obj.location = originalLoc #Resets previous object location
		ResetArmaturePose(obj)
		obj.animation_data.action = UserAction #Resets previous action
		exportTime = time.process_time()-curr_time
		return(["Animation",fullpath,exportTime])


def ExportSingleMesh(obj, dirpath, filename): #Export a single Mesh
	curr_time = time.process_time()
	bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc = originalLoc + obj.location #Save current object location

	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	absdirpath = bpy.path.abspath(dirpath)
	VerifiDirs(absdirpath)
	fullpath = os.path.join( absdirpath , filename )

	if UseRealExport == True:
		bpy.ops.export_scene.fbx(filepath=fullpath,
			check_existing=False,
			version='BIN7400',
			use_selection=True,
			mesh_smooth_type="FACE",
			add_leaf_bones=False,
			use_armature_deform_only=bpy.context.scene.fbx_export_deform_only,
			bake_anim=False
			)
	meshType = "StaticMesh"
	if obj.type == 'ARMATURE':
		meshType = "SkeletalMesh"
	obj.location = originalLoc #Resets previous object location
	exportTime = time.process_time()-curr_time
	return([meshType,fullpath,exportTime])


def FindAllObjetsByExportType(exportType): #Find all objets with a ExportEnum property desired
	targetObj = []
	for obj in bpy.context.scene.objects:
		prop = obj.ExportEnum
		if prop == exportType:
			targetObj.append(obj)

	return(targetObj)


def GenerateUe4Name(name): #From a objet name generate a new name with by adding a suffix number


	def IsValidName(testedName): #Checks if an object uses this name. If not is a valid name
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


def ConvertToUe4Socket(objsToConvert, ownerObj): #Convert all selected empty to unreal socket

	#----------------------------------------Save data
	UserObjHide = []
	for obj in bpy.context.scene.objects:
		UserObjHide.append(obj.hide) #Save previous object visibility
		obj.hide = False
	if bpy.context.object is None:
		bpy.context.scene.objects.active = bpy.data.objects[0]

	UserMode = bpy.context.object.mode #Save current mode
	UserActive = bpy.context.active_object #Save current active object
	UserSelected = bpy.context.selected_objects #Save current selected objects
	#----------------------------------------

	bpy.ops.object.mode_set(mode = 'OBJECT')

	for obj in objsToConvert:
		if obj != ownerObj:
			if obj.type == 'EMPTY':
				obj.name = GenerateUe4Name("SOCKET_"+ownerObj.name)
				obj.scale = (0.01,0.01,0.01)
				obj.empty_draw_size = 100
				if obj.parent != ownerObj.name:
					bpy.ops.object.select_all(action='DESELECT')
					obj.select = True
					bpy.context.scene.objects.active = ownerObj
					bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

	#----------------------------------------Reset data
	bpy.ops.object.select_all(action='DESELECT')
	for obj in UserSelected: obj.select = True #Resets previous active object
	bpy.context.scene.objects.active = UserActive #Resets previous active object
	bpy.ops.object.mode_set(mode = UserMode) #Resets previous mode
	for x, obj in enumerate(bpy.context.scene.objects):
		obj.hide = UserObjHide[x] #Resets previous object visibility


def CheckIfCollisionAndSocketOwnerIsValid():
	for obj in bpy.data.objects:
		if bpy.context.scene.collision_and_socket_owner == obj.name:
			owner = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			if owner.type != "ARMATURE":
				return True
	return False


def ConvertToUe4Collision(collisionType, objsToConvert, ownerObj): #Convert all selected objets to unreal collisions
	
	#----------------------------------------Save data
	UserObjHide = []
	for obj in bpy.context.scene.objects:
		UserObjHide.append(obj.hide) #Save previous object visibility
		obj.hide = False
	if bpy.context.object is None:
		bpy.context.scene.objects.active = bpy.data.objects[0]

	UserMode = bpy.context.object.mode #Save current mode
	UserActive = bpy.context.active_object #Save current active object
	UserSelected = bpy.context.selected_objects #Save current selected objects
	#----------------------------------------

	bpy.ops.object.mode_set(mode = 'OBJECT')
	#Set the name of the Prefix depending on the type of collision in agreement with unreal FBX Pipeline
	prefixName = ""
	if collisionType == "Box":
		prefixName = "UBX_"
	elif collisionType == "Capsule":
		prefixName = "UCP_"
	elif collisionType == "Sphere":
		prefixName = "USP_"
	elif collisionType == "Convex":
		prefixName = "UCX_"
	else:
		return

	mat = bpy.data.materials.get("UE4Collision")
	if mat is None:
		mat = bpy.data.materials.new(name="UE4Collision")
	mat.diffuse_color = (0, 0.6, 0)
	mat.alpha = 0.1
	mat.use_transparency = True
	mat.use_nodes = False

	for obj in objsToConvert:
		if obj != ownerObj:
			if obj.type == 'MESH':
				obj.data.materials.clear()
				obj.data.materials.append(mat)
				obj.name = GenerateUe4Name(prefixName+ownerObj.name)
				obj.show_wire = True
				obj.show_transparent = True
				if obj.parent != ownerObj.name:
					bpy.ops.object.select_all(action='DESELECT')
					obj.select = True
					bpy.context.scene.objects.active = ownerObj
					bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

	#----------------------------------------Reset data
	bpy.ops.object.select_all(action='DESELECT')
	for obj in UserSelected: obj.select = True #Resets previous active object
	bpy.context.scene.objects.active = UserActive #Resets previous active object
	bpy.ops.object.mode_set(mode = UserMode) #Resets previous mode
	for x, obj in enumerate(bpy.context.scene.objects):
		obj.hide = UserObjHide[x] #Resets previous object visibility

			
def CorrectBadProperty():
	Scene = bpy.context.scene
	colObjs = [obj for obj in Scene.objects if
		fnmatch.fnmatchcase(obj.name, "UBX*") or
		fnmatch.fnmatchcase(obj.name, "UCP*") or
		fnmatch.fnmatchcase(obj.name, "USP*") or
		fnmatch.fnmatchcase(obj.name, "UCX*") or
		fnmatch.fnmatchcase(obj.name, "SOCKET*")]
		
	correctedProperty = 0
	for obj in colObjs:
		if obj.ExportEnum == "export_and_childs":
			obj.ExportEnum = "auto"
			correctedProperty = correctedProperty + 1
		exportPare = GetHierarchyExportParent(obj)
		if exportPare is not None:
			if fnmatch.fnmatchcase(obj.name, "UBX*"):
				ConvertToUe4Collision("Box", [obj], exportPare)
			if fnmatch.fnmatchcase(obj.name, "UCP*"):
				ConvertToUe4Collision("Capsule", [obj], exportPare)
			if fnmatch.fnmatchcase(obj.name, "USP*"):
				ConvertToUe4Collision("Sphere", [obj], exportPare)
			if fnmatch.fnmatchcase(obj.name, "UCX*"):
				ConvertToUe4Collision("Convex", [obj], exportPare)
			if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
				ConvertToUe4Socket([obj], exportPare)
	for obj in Scene.objects:
		if obj.ExportEnum != "export_and_childs" and obj.exportFolderName != "":
			obj.exportFolderName = ""
			correctedProperty = correctedProperty + 1
			
			
	return correctedProperty
	
def	FindPotentialError():
	PotentialError = []
	for obj in bpy.context.scene.objects:
		if obj.type == 'MESH':
			if obj.data.shape_keys is not None:
				if len(obj.data.shape_keys.key_blocks) > 0:
					for modif in obj.modifiers:
						if modif.type != "ARMATURE" :
							PotentialError.append("In object named \""+obj.name+"\" the modifier type ("+modif.type+") named \""+modif.name+"\" can destroy shape keys. Pleas use only Armature modifier with shape keys")
			ArmatureModifiers = 0
			for modif in obj.modifiers:
				if modif.type == "ARMATURE" :
					if obj.ExportEnum == "export_and_childs":
						PotentialError.append("In object named \""+obj.name+"\" the modifier Armature will not apply when exported with StaticMesh assets")
					ArmatureModifiers = ArmatureModifiers + 1
			if ArmatureModifiers > 1:
				PotentialError.append("In object named \""+obj.name+"\" there are several times the modifier Armature. Pleas use only one Armature modifier ")
		if obj.type == 'ARMATURE':
			childs = GetDesiredChilds(obj)
			if len(childs) < 1:
				PotentialError.append("In object named \""+obj.name+"\" is a (ARMATURE) and dont have any valid child ")
	for action in bpy.data.actions:
		for fcurve in action.fcurves:
			#animBonesName.append(fcurve.data_path.split('"')[1])
			if fcurve.data_path.split(".")[-1] == "scale":
				for key in fcurve.keyframe_points:
					xCurve, yCurve = key.co
					if key.co[1] == 0:
						PotentialError.append("In action named \""+action.name+"\" at frame "+str(key.co[0])+", bone named \""+fcurve.data_path.split('"')[1]+"\" use zero scale transform. this is invalid in Unreal. ")
						
	return PotentialError
	
def ExportAllByList(targetObjets): #Export all objects that need to be exported
	exportedAssets = [] #List of exported objects [Assetsype , ExportPath] Reset with each export
	if len(targetObjets) > 0:

		#----------------------------------------Save data
		UserObjHide = []
		for obj in bpy.context.scene.objects:
			UserObjHide.append(obj.hide) #Save previous object visibility
			obj.hide = False
		if bpy.context.object is None:
			bpy.context.scene.objects.active = bpy.data.objects[0]

		UserMode = bpy.context.object.mode #Save current mode
		UserActive = bpy.context.active_object #Save current active object
		UserSelected = bpy.context.selected_objects #Save current selected objects
		LayerVisibility = []
		for x in range(20):
			LayerVisibility.append(bpy.context.scene.layers[x])
		#----------------------------------------
		for x in range(20):
			bpy.context.scene.layers[x] = True
		Scene = bpy.context.scene
		blendFileLoc = os.path.dirname(bpy.data.filepath)
		smPrefix = bpy.context.scene.static_prefix_export_name
		skPrefix = bpy.context.scene.skeletal_prefix_export_name
		animPrefix = bpy.context.scene.anim_prefix_export_name
		for obj in targetObjets:
			if obj.type == 'ARMATURE':
				exportDir = os.path.join( bpy.context.scene.export_skeletal_file_path , obj.exportFolderName , obj.name )
				exportedAssets.append(ExportSingleMesh(obj, exportDir, skPrefix+obj.name+".fbx"))

				UserStartFrame = bpy.context.scene.frame_start #Save current start frame
				UserEndFrame = bpy.context.scene.frame_end #Save current end frame
				
				for action in bpy.data.actions:

					objBonesName = [bone.name for bone in obj.pose.bones]
					animBonesName = []
					for fcurve in action.fcurves:
						try:
							animBonesName.append(fcurve.data_path.split('"')[1])
						except:
							pass
						
						
					if ChecksRelationship(objBonesName, animBonesName):
						animExportDir = os.path.join( exportDir, "Anim" )
						exportedAssets.append(ExportSingleAnimation(obj, action, animExportDir, animPrefix+obj.name+"_"+action.name+".fbx"))

				bpy.context.scene.frame_start = UserStartFrame #Resets previous start frame
				bpy.context.scene.frame_end = UserEndFrame #Resets previous end frame

			else:
				exportDir = os.path.join( bpy.context.scene.export_static_file_path, obj.exportFolderName )
				exportedAssets.append(ExportSingleMesh(obj, exportDir, smPrefix+obj.name+".fbx"))

		#----------------------------------------Reset data
		for x in range(20):
			bpy.context.scene.layers[x] = LayerVisibility[x]
		bpy.ops.object.select_all(action='DESELECT')
		for obj in UserSelected: obj.select = True #Resets previous active object
		bpy.context.scene.objects.active = UserActive #Resets previous active object
		bpy.ops.object.mode_set(mode = UserMode) #Resets previous mode
		for x, obj in enumerate(bpy.context.scene.objects):
			obj.hide = UserObjHide[x] #Resets previous object visibility
	return exportedAssets


#############################[Visual and UI]#############################


#### Panels
class ue4PropertiesPanel(bpy.types.Panel): #Is Objet Properties panel

	bpy.types.Object.ExportEnum = EnumProperty(
	name = "Export type",
	description	 = "Export type of active object",
	items = [("auto", "Auto", "Export only if one parents is \"Export and child\"", "KEY_HLT", 1),
		("export_and_childs", "Export and childs", "Export self objet and all childs", "KEYINGSET", 2),
		("dont_export", "Dont export", "Will never export", "KEY_DEHLT", 3)])
		
	bpy.types.Object.exportFolderName = StringProperty(
	name = "Folder name",
	description	 = "Export type of active object",
	maxlen = 64,
	default = "",
	subtype = 'FILE_NAME')

	bl_idname = "panel.ue4.properties"
	bl_label = "Objet Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		layout = self.layout
		if context.object is not None:
			
			layout.prop(context.object, 'ExportEnum')
			folderNameProperty = layout.column()
			folderNameProperty.prop(context.object, 'exportFolderName')
			
			if context.object.ExportEnum == "export_and_childs":
				folderNameProperty.active = True
				folderNameProperty.enabled = True
			else:
				folderNameProperty.active = False
				folderNameProperty.enabled = False
			
		row = self.layout.row().split(percentage = 0.80 )
		row = row.column()

		row.operator("object.selectexport", icon='MARKER_HLT')
		row.operator("object.deselectexport", icon='MARKER')
		row.operator("object.selectexportchild", icon='SPACE2')
		row.operator("object.deselectexportchild", icon='SPACE3')


class ue4CollisionsAndSocketsPanel(bpy.types.Panel): #Is Collisions And Sockets panel

	bpy.types.Scene.collision_and_socket_owner = bpy.props.StringProperty(
		name = "Owner",
		description	 = "Enter the owner name of the collision or socket",
		maxlen = 64,
		default = "")

	bl_idname = "panel.ue4.collisionsandsockets"
	bl_label = "Collisions And Sockets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):

		scene = context.scene
		layout = self.layout

		ownerSelect = layout.row().split(align=True, percentage=0.9)
		ownerSelect.prop_search(scene, "collision_and_socket_owner", scene, "objects")
		ownerSelect.operator("object.setownerbyactive", text="", icon='EYEDROPPER')

		layout.label("Convert selected objet to Unreal collision or socket", icon='PHYSICS')

		convertButtons = layout.row().split(percentage = 0.80 )

		convertButtons.active = CheckIfCollisionAndSocketOwnerIsValid()
		convertButtons.enabled = CheckIfCollisionAndSocketOwnerIsValid()
		convertButtons = convertButtons.column()
		convertButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
		convertButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
		convertButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
		convertButtons.operator("object.converttospherecollision", icon='SOLID')
		convertButtons.operator("object.converttosocket", icon='OUTLINER_DATA_EMPTY')


class ue4CheckCorrect(bpy.types.Panel): #Is Check and correct panel
	bl_idname = "panel.ue4.CheckCorrect"
	bl_label = "Check and correct"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		scn = context.scene
		props = self.layout.row().operator("object.correctproperty", icon='FILE_TICK')
		props = self.layout.row().operator("object.checkpotentialerror", icon='QUESTION')

		
class ue4ExportPanel(bpy.types.Panel): #Is Export panel
	
	bpy.types.Scene.fbx_export_deform_only = bpy.props.BoolProperty(
		name="Only Deform Bones",
        description="Only write deforming bones (and non-deforming ones when they have deforming children)",
        default=False,
		)
	
	bpy.types.Scene.fbx_export_simplify_anim = bpy.props.FloatProperty(
		name="Simplify animations",
		description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
		min=0.0, max=100.0,	 # No simplification to up to 10% of current magnitude tolerance.
		soft_min=0.0, soft_max=10.0,
		default=1.0,  # default: min slope: 0.005, max frame step: 10.
		)

	bl_idname = "panel.ue4.exportfbx"
	bl_label = "Export (FBX property)"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		scn = context.scene
		prop = bpy.types.Scene
		self.layout.prop(scn, 'fbx_export_deform_only')
		self.layout.prop(scn, 'fbx_export_simplify_anim')
		
		
class ue4ExportPanel(bpy.types.Panel): #Is Export panel

	bpy.types.Scene.static_prefix_export_name = bpy.props.StringProperty(
		name = "StaticMesh Prefix",
		description	 = "Prefix of staticMesh when exported",
		maxlen = 255,
		default = "SM_")

	bpy.types.Scene.skeletal_prefix_export_name = bpy.props.StringProperty(
		name = "SkeletalMesh Prefix ",
		description	 = "Prefix of SkeletalMesh when exported",
		maxlen = 255,
		default = "SK_")

	bpy.types.Scene.anim_prefix_export_name = bpy.props.StringProperty(
		name = "AnimationSequence Prefix",
		description	 = "Prefix of AnimationSequence when exported",
		maxlen = 255,
		default = "Anim_")

	bpy.types.Scene.export_static_file_path = bpy.props.StringProperty(
		name = "StaticMesh export file path",
		description = "Choose a directory for export StaticMesh(s)",
		maxlen = 1024,
		default = "//ExportedFbx\StaticMesh\\",
		subtype = 'DIR_PATH')

	bpy.types.Scene.export_skeletal_file_path = bpy.props.StringProperty(
		name = "SkeletalMesh export file path",
		description = "Choose a directory for export SkeletalMesh(s)",
		maxlen = 1024,
		default = "//ExportedFbx\SkeletalMesh\\",
		subtype = 'DIR_PATH')

	bl_idname = "panel.ue4.export"
	bl_label = "Export"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		scn = context.scene
		prop = bpy.types.Scene
		self.layout.prop(scn, 'static_prefix_export_name', icon='OBJECT_DATA')
		self.layout.prop(scn, 'skeletal_prefix_export_name', icon='OBJECT_DATA')
		self.layout.prop(scn, 'anim_prefix_export_name', icon='OBJECT_DATA')
		self.layout.prop(scn, 'export_static_file_path')
		self.layout.prop(scn, 'export_skeletal_file_path')
		props = self.layout.row().operator("object.exportforunreal", icon='EXPORT')

#### Buttons
class SelectExportButton(bpy.types.Operator):
	bl_label = "Select all export objects root"
	bl_idname = "object.selectexport"
	bl_description = "Select all root objects that will be exported"

	def execute(self, context):		
		for obj in FindAllObjetsByExportType("export_and_childs"):
			obj.select = True
		return {'FINISHED'}


class DeselectExportButton(bpy.types.Operator):
	bl_label = "Deselect all export objects root"
	bl_idname = "object.deselectexport"
	bl_description = "Deselect all root objects that will be exported"

	def execute(self, context):
		for obj in FindAllObjetsByExportType("export_and_childs"):
			obj.select = False
		return {'FINISHED'}


class SelectExportAndChildButton(bpy.types.Operator):
	bl_label = "Select all export childs objects"
	bl_idname = "object.selectexportchild"
	bl_description = "Select all root objects that will be exported"

	def execute(self, context):
		for obj in FindAllObjetsByExportType("export_and_childs"):
			for obj2 in GetDesiredChilds(obj):
				obj2.select = True
		return {'FINISHED'}


class DeselectExportAndChildButton(bpy.types.Operator):
	bl_label = "Deselect all export childs objects"
	bl_idname = "object.deselectexportchild"
	bl_description = "Deselect all root objects that will be exported"

	def execute(self, context):
		for obj in FindAllObjetsByExportType("export_and_childs"):
			for obj2 in GetDesiredChilds(obj):
				obj2.select = False
		return {'FINISHED'}


class SetOwnerByActive(bpy.types.Operator):
	bl_label = "Set owner by active selection"
	bl_idname = "object.setownerbyactive"
	bl_description = "Set owner by active selection"

	def execute(self, context):
		if bpy.context.active_object is not None:
			bpy.context.scene.collision_and_socket_owner = bpy.context.active_object.name
		else:
			bpy.context.scene.collision_and_socket_owner = ""
		return {'FINISHED'}


class ConvertToUECollisionButtonBox(bpy.types.Operator):
	bl_label = "Convert to box (UBX)"
	bl_idname = "object.converttoboxcollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Boxes type)"

	def execute(self, context):
		if CheckIfCollisionAndSocketOwnerIsValid():
			ownerObj = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			ConvertToUe4Collision("Box", bpy.context.selected_objects, ownerObj)
			self.report({'INFO'}, "Selected objet(s) have be converted to UE4 Box collisions")
		return {'FINISHED'}


class ConvertToUECollisionButtonCapsule(bpy.types.Operator):
	bl_label = "Convert to capsule (UCP)"
	bl_idname = "object.converttocapsulecollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Capsules type)"

	def execute(self, context):
		if CheckIfCollisionAndSocketOwnerIsValid():
			ownerObj = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			ConvertToUe4Collision("Capsule", bpy.context.selected_objects, ownerObj)
			self.report({'INFO'}, "Selected objet(s) have be converted to UE4 Capsule collisions")
		return {'FINISHED'}


class ConvertToUECollisionButtonSphere(bpy.types.Operator):
	bl_label = "Convert to sphere (USP)"
	bl_idname = "object.converttospherecollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Spheres type)"

	def execute(self, context):
		if CheckIfCollisionAndSocketOwnerIsValid():
			ownerObj = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			ConvertToUe4Collision("Sphere", bpy.context.selected_objects, ownerObj)
			self.report({'INFO'}, "Selected objet(s) have be converted to UE4 Sphere collisions")
		return {'FINISHED'}


class ConvertToUECollisionButtonConvex(bpy.types.Operator):
	bl_label = "Convert to convex shape (UCX)"
	bl_idname = "object.converttoconvexcollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Convex shapes type)"

	def execute(self, context):
		if CheckIfCollisionAndSocketOwnerIsValid():
			ownerObj = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			ConvertToUe4Collision("Convex", bpy.context.selected_objects, ownerObj)
			self.report({'INFO'}, "Selected objet(s) have be converted to UE4 Convex collisions")
		return {'FINISHED'}


class ConvertToUESocketButton(bpy.types.Operator):
	bl_label = "Convert to socket (SOCKET)"
	bl_idname = "object.converttosocket"
	bl_description = "Convert selected empty(s) to Unreal sockets ready for export"

	def execute(self, context):
		if CheckIfCollisionAndSocketOwnerIsValid():
			ownerObj = bpy.data.objects[bpy.context.scene.collision_and_socket_owner]
			ConvertToUe4Socket(bpy.context.selected_objects, ownerObj)
			self.report({'INFO'}, "Selected empty(s) have be converted to UE4 Socket")
		return {'FINISHED'}
		
		
class CorrectBadPropertyButton(bpy.types.Operator):
	bl_label = "Correct bad propertys"
	bl_idname = "object.correctproperty"
	bl_description = "Corrects bad properties"

	def execute(self, context):
		corrected = CorrectBadProperty()
		if corrected > 0 :
			self.report({'INFO'}, str(corrected) + " property corected")
		else:
			self.report({'INFO'}, "No property to correct !")
		return {'FINISHED'}
		
		
class CheckPotentialErrorButton(bpy.types.Operator):
	bl_label = "Check potential errors"
	bl_idname = "object.checkpotentialerror"
	bl_description = "Check potential errors"

	def execute(self, context):
		potentialerrors = FindPotentialError()
		if len(potentialerrors) > 0 :
			for error in potentialerrors:
				self.report({'WARNING'}, "WARNING : "+error)
		else:
			self.report({'INFO'}, "No potential error to correct !")
		return {'FINISHED'}	
		
		
class ExportForUnrealEngineButton(bpy.types.Operator):
	bl_label = "Export for UnrealEngine 4"
	bl_idname = "object.exportforunreal"
	bl_description = "Export all objet intended for export in scene to fbx"

	def execute(self, context):
		curr_time = time.process_time()
		exportedAssets = ExportAllByList(FindAllObjetsByExportType("export_and_childs"))
		if len(exportedAssets) > 0:
			self.report({'INFO'}, "Export of "+str(len(exportedAssets))+
			" asset(s) has been finalized in "+str(time.process_time()-curr_time)+" sec. Look in console for more info.")
			print ("################## Exported asset(s) ##################")
			for asset in exportedAssets:
				print(asset[0]+" exported in "+str(asset[2])+" sec here:")
				print(asset[1])
				print("--------------")
				#print (asset[0]+" --> "+asset[1]+" --> Exported in "+str(asset[2])+" sec.")
			print ("################## Exported asset(s) ##################")
		else:
			self.report({'WARNING'}, "Not found assets. with \"Export and child\" properties.")
			self.report({'OPERATOR'}, "Pleas select at least one object and set \"Export and child\" properties.")	
		return {'FINISHED'}


#############################[...]#############################


def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_prop = bpy.props.StringProperty(default="default value")


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
