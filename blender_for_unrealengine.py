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
# ----------------------------------------------

bl_info = {
	'name': 'Blender for UnrealEngine',
	'description': "This add-ons allows to easily export several "
	"objects at the same time for use in unreal engine 4.",
	'author': 'Loux Xavier (BleuRaven)',
	'version': (0, 1, 3),
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

#############################[Variables]#############################


exportedAssets = [] #List of exported objects [Assetsype , ExportPath] Reset with each export


#############################[Functions]#############################


def GetStringSceneProperty(properties): #Allows to get StringSceneProperty with properties name.
	prop = ""
	try:
		prop = bpy.context.scene[properties]
		return prop
	except:
		pass
	return prop


def ChecksRelationship(arrayA, arrayB): #Checks if it exits an identical variable in two lists
	for a in arrayA:
		for b in arrayB:
			if a == b:
				return True
	return False


def SelectParentAndDesiredChilds(obj): #Selects only all child objects that must be exported with parent objet
	bpy.ops.object.select_all(action='DESELECT')
	bpy.context.scene.objects.active = obj
	bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')

	for unwantedObj in FindAllObjetsByExportType("dont_export"): #Deselect all objects that should not be exported
		unwantedObj.select = False
	obj.select = True


def ResetArmaturePose(obj): #Reset armature pose
	for x in obj.pose.bones:
		x.rotation_quaternion = Quaternion((0,0,0),0)
		x.scale = Vector((1,1,1))
		x.location = Vector((0,0,0))


def VerifiDirs(directory): #check and create a folder if it does not exist
	if not os.path.exists(directory):
		os.makedirs(directory)

print (max(0, 1))
def ExportSingleAnimation(obj, targetAction, dirpath, filename): #Export a single animation
	if obj.type == 'ARMATURE':
		bpy.ops.object.mode_set(mode = 'OBJECT')
		originalLoc = Vector((0,0,0))
		originalLoc =	originalLoc + obj.location #Save objet location
		obj.location = (0,0,0) #Moves object to the center of the scene for export

		SelectParentAndDesiredChilds(obj)
		ResetArmaturePose(obj)

		obj.animation_data.action = targetAction #Apply desired action
		keyframes = []
		for fcu in obj.animation_data.action.fcurves:
			for keyframe in fcu.keyframe_points:
				xCurve, yCurve = keyframe.co
				keyframes.append(xCurve)
		bpy.context.scene.frame_start = 0
		bpy.context.scene.frame_end = max(keyframes[-1],1) #Set end_frame on the final key the current action
		VerifiDirs(dirpath)
		fullpath = os.path.join( dirpath , filename )
		bpy.ops.export_scene.fbx(
			filepath=fullpath,
			check_existing=False,
			version='BIN7400',
			use_selection=True,
			object_types={'ARMATURE'},
			bake_anim=True,
			bake_anim_use_nla_strips=False,
			bake_anim_use_all_actions=False,
			bake_anim_force_startend_keying=True,
			)
		exportedAssets.append(["Animation", fullpath])
		obj.location = originalLoc #Move object to this saved location


def ExportSingleMesh(obj, dirpath, filename): #Export a single Mesh
	if bpy.context.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode = 'OBJECT')
	originalLoc = Vector((0,0,0))
	originalLoc =	originalLoc + obj.location #Save objet location
	obj.location = (0,0,0) #Moves object to the center of the scene for export

	SelectParentAndDesiredChilds(obj)

	VerifiDirs(dirpath)
	fullpath = os.path.join( dirpath , filename )
	bpy.ops.export_scene.fbx(filepath=fullpath,
		check_existing=False,
		version='BIN7400',
		use_selection=True,
		bake_anim=False,
		)
	meshType = "StaticMesh"
	if obj.type == 'ARMATURE':
		meshType = "SkeletalMesh"
	exportedAssets.append([meshType , fullpath])
	obj.location = originalLoc #Move object to this saved location


def FindAllObjetsByExportType(exportType): #Find all objets with a ExportEnum property desired
	targetObj = []
	for obj in bpy.context.scene.objects:
		try:
			prop = obj.ExportEnum
			if prop == exportType:
				targetObj.append(obj)
		except:
			pass
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


def ConvertEmptyToUe4Socket(): #Convert all selected empty to unreal socket
	if CheckIfCollisionAndSocketOwnerIsValid():
		ownerObjName = GetStringSceneProperty("CollisionAndSocketOwner")
		bpy.ops.object.mode_set(mode = 'OBJECT')
		ownerObj = bpy.data.objects[ownerObjName]
		for obj in bpy.context.selected_objects:
			if obj != ownerObj:
				if obj.type == 'EMPTY':
					obj.name = GenerateUe4Name("SOCKET_"+ownerObjName)
					obj.scale = (0.01,0.01,0.01)
					obj.empty_draw_size = 100
					if obj.parent != ownerObj.name:
						bpy.ops.object.select_all(action='DESELECT')
						obj.select = True
						bpy.context.scene.objects.active = ownerObj
						bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


def ConvertMeshToUe4Collision(collisionType): #Convert all selected mesh to unreal collisions
	ownerObjName = GetStringSceneProperty("CollisionAndSocketOwner")
	if CheckIfCollisionAndSocketOwnerIsValid():
		bpy.ops.object.mode_set(mode = 'OBJECT')
		ownerObj = bpy.data.objects[ownerObjName]
		prefixName = ""

		#Set the name of the Prefix depending on the type of collision in agreement with unreal FBX Pipeline
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

		for obj in bpy.context.selected_objects:
			if obj != ownerObj:
				if obj.type == 'MESH':
					obj.data.materials.clear()
					obj.data.materials.append(mat)
					obj.name = GenerateUe4Name(prefixName+ownerObjName)
					obj.show_wire = True
					obj.show_transparent = True
					if obj.parent != ownerObj.name:
						bpy.ops.object.select_all(action='DESELECT')
						obj.select = True
						bpy.context.scene.objects.active = ownerObj
						bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


def ExportAllByList(targetObjets): #Export all objects that need to be exported
	if len(targetObjets) > 0:
		Scene = bpy.context.scene
		blendFileLoc = os.path.dirname(bpy.data.filepath)
		smPrefix = GetStringSceneProperty("StaticPrefixExportName")
		skPrefix = GetStringSceneProperty("SkeletalPrefixExportName")
		animPrefix = GetStringSceneProperty("AnimPrefixExportName")
		for obj in targetObjets:
			if obj.type == 'ARMATURE':
				exportDir = os.path.join( blendFileLoc, "ExportedFbx" , "SkeletalMesh", obj.name )
				ExportSingleMesh(obj, exportDir, skPrefix+obj.name+".fbx")
				for Action in bpy.data.actions:

					objBonesName = [bone.name for bone in obj.pose.bones]
					animBonesName = []
					for curve in Action.fcurves:
						try:
							animBonesName.append(curve.data_path.split('"')[1])
						except:
							pass

					if ChecksRelationship(objBonesName, animBonesName):
						animExportDir = os.path.join( exportDir, "Anim" )
						ExportSingleAnimation(obj, Action, animExportDir, animPrefix+obj.name+"_"+Action.name+".fbx")
			else:
				exportDir = os.path.join( blendFileLoc, "ExportedFbx" , "StaticMesh" )
				ExportSingleMesh(obj, exportDir, smPrefix+obj.name+".fbx")

def	CorrectBadProperty():
	Scene = bpy.context.scene
	foo_objs1 = [obj for obj in Scene.objects if
		fnmatch.fnmatchcase(obj.name, "UBX*") or
		fnmatch.fnmatchcase(obj.name, "UCX*") or
		fnmatch.fnmatchcase(obj.name, "UCP*") or
		fnmatch.fnmatchcase(obj.name, "USP*") or
		fnmatch.fnmatchcase(obj.name, "SOCKET*")]

	for u in foo_objs1:
		try:

			if u.ExportEnum == "export_and_childs":
				u.ExportEnum = "auto"
		except:
			pass


def ExportComplete(self): #Display a summary at the end of the export and reset "exportedAssets"
	if len(exportedAssets) > 0:
		self.report({'INFO'}, "Export of "+str(len(exportedAssets))+" asset(s) has been finalized ! ")
		self.report({'INFO'}, "Look in th console for more info.")
		print ("################## Exported asset(s) ##################")
		for asset in exportedAssets:
			print (asset[0]+" --> "+asset[1])
		print ("################## Exported asset(s) ##################")
	else:
		self.report({'WARNING'}, "Not found assets. with \"Export and child\" properties.")
		self.report({'OPERATOR'}, "Pleas select at least one object and set \"Export and child\" properties.")
	del exportedAssets[:]


#############################[Visual and UI]#############################

#### UI Function
def CheckIfCollisionAndSocketOwnerIsValid():
	for obj in bpy.data.objects:
		if GetStringSceneProperty("CollisionAndSocketOwner") == obj.name:
			owner = bpy.data.objects[GetStringSceneProperty("CollisionAndSocketOwner")]
			if owner.type != "ARMATURE":
				return True
	return False

#### Propertys
def initObjectProperties():
	bpy.types.Object.ExportEnum = EnumProperty(
	name = "Type of export ",
	description	 = "Export type of active object",
	items = [("auto", "Auto", "Export only if one parents is \"Export and child\"", "KEY_HLT", 1),
		("export_and_childs", "Export and childs", "Export self objet and all childs", "KEYINGSET", 2),
		("dont_export", "Dont export", "Will never export", "KEY_DEHLT", 3)])


def initSceneProperties():
	bpy.types.Scene.CollisionAndSocketOwner = StringProperty(
		name = "Owner",
		description	 = "Enter the owner name of the collision or socket",
		default = "")

	bpy.types.Scene.StaticPrefixExportName = StringProperty(
		name = "StaticMesh Prefix",
		description	 = "Prefix of staticMesh when exported",
		maxlen = 255,
		default = "SM_")

	bpy.types.Scene.SkeletalPrefixExportName = StringProperty(
		name = "SkeletalMesh Prefix ",
		description	 = "Prefix of SkeletalMesh when exported",
		maxlen = 255,
		default = "SK_")

	bpy.types.Scene.AnimPrefixExportName = StringProperty(
		name = "AnimationSequence Prefix",
		description	 = "Prefix of AnimationSequence when exported",
		maxlen = 255,
		default = "Anim_")
	return


def ChecksProp(prop):
	try:
		value = prop["StaticPrefixExportName"]
	except:
		pass
		prop["StaticPrefixExportName"] = "SM_"
	try:
		value = prop["SkeletalPrefixExportName"]
	except:
		pass
		prop["SkeletalPrefixExportName"] = "SK_"
	try:
		value = prop["AnimPrefixExportName"]
	except:
		pass
		prop["AnimPrefixExportName"] = "Anim_"

	return

#### Panels
class ue4PropertiesPanel(bpy.types.Panel): #Is Objet Properties panel
	bl_idname = "panel.ue4.properties"
	bl_label = "Objet Properties"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		layout = self.layout
		try:
			ob = context.object
			layout.prop(ob, 'ExportEnum')
		except:
			pass
		row = self.layout.row().split(percentage = 0.80 )
		row = row.column()

		row.operator("object.selectexport")
		row.operator("object.deselectexport")


class ue4CollisionsAndSocketsPanel(bpy.types.Panel): #Is Collisions And Sockets panel
	bl_idname = "panel.ue4.collisionsandsockets"
	bl_label = "Collisions And Sockets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):

		scene = context.scene
		layout = self.layout

		ownerSelect = layout.row().split(align=True, percentage=0.9)
		ownerSelect.prop_search(scene, "CollisionAndSocketOwner", scene, "objects")
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

class ue4ExportPanel(bpy.types.Panel): #Is Export panel
	bl_idname = "panel.ue4.export"
	bl_label = "Export"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Unreal Engine 4"

	def draw(self, context):
		scn = context.scene
		self.layout.prop(scn, 'StaticPrefixExportName', icon='OBJECT_DATA')
		self.layout.prop(scn, 'SkeletalPrefixExportName', icon='OBJECT_DATA')
		self.layout.prop(scn, 'AnimPrefixExportName', icon='OBJECT_DATA')
		props = self.layout.row().operator("object.exportforunreal", icon='EXPORT')

#### Buttons
class SelectExportAndChildButton(bpy.types.Operator):
	bl_label = "Select all \"Export and childs\" objects"
	bl_idname = "object.selectexport"
	bl_description = "Select all root objects that will be exported"

	def execute(self, context):
		for obj in FindAllObjetsByExportType("export_and_childs"):
			obj.select = True
		return {'FINISHED'}


class DeselectExportAndChildButton(bpy.types.Operator):
	bl_label = "Deselect all \"Export and childs\" objects"
	bl_idname = "object.deselectexport"
	bl_description = "Deselect all root objects that will be exported"

	def execute(self, context):
		for obj in FindAllObjetsByExportType("export_and_childs"):
			obj.select = False
		return {'FINISHED'}

class SetOwnerByActive(bpy.types.Operator):
	bl_label = "Set owner by active selection"
	bl_idname = "object.setownerbyactive"
	bl_description = "Set owner by active selection"

	def execute(self, context):
		try:
			bpy.context.scene["CollisionAndSocketOwner"] = bpy.context.active_object.name
		except:
			pass
			bpy.context.scene["CollisionAndSocketOwner"] = ""
		return {'FINISHED'}

class ConvertToUECollisionButtonBox(bpy.types.Operator):
	bl_label = "Convert to box (UBX)"
	bl_idname = "object.converttoboxcollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Boxes type)"

	def execute(self, context):
		ConvertMeshToUe4Collision("Box")
		return {'FINISHED'}


class ConvertToUECollisionButtonCapsule(bpy.types.Operator):
	bl_label = "Convert to capsule (UCP)"
	bl_idname = "object.converttocapsulecollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Capsules type)"

	def execute(self, context):
		ConvertMeshToUe4Collision("Capsule")
		return {'FINISHED'}


class ConvertToUECollisionButtonSphere(bpy.types.Operator):
	bl_label = "Convert to sphere (USP)"
	bl_idname = "object.converttospherecollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Spheres type)"

	def execute(self, context):
		ConvertMeshToUe4Collision("Sphere")
		return {'FINISHED'}


class ConvertToUECollisionButtonConvex(bpy.types.Operator):
	bl_label = "Convert to convex shape (UCX)"
	bl_idname = "object.converttoconvexcollision"
	bl_description = "Convert selected mesh(s) to Unreal collision ready for export (Convex shapes type)"

	def execute(self, context):
		ConvertMeshToUe4Collision("Convex")
		return {'FINISHED'}


class ConvertToUESocketButton(bpy.types.Operator):
	bl_label = "Convert to socket (SOCKET)"
	bl_idname = "object.converttosocket"
	bl_description = "Convert selected empty(s) to Unreal sockets ready for export"

	def execute(self, context):
		ConvertEmptyToUe4Socket()
		return {'FINISHED'}


class ExportForUnrealEngineButton(bpy.types.Operator):
	bl_label = "Export for UnrealEngine 4"
	bl_idname = "object.exportforunreal"
	bl_description = "Export all objet intended for export in scene to fbx"

	def execute(self, context):
		ChecksProp(bpy.context.scene)
		ExportAllByList(FindAllObjetsByExportType("export_and_childs"))
		ExportComplete(self)
		return {'FINISHED'}

class CorrectBadPropertyButton(bpy.types.Operator):
	bl_label = "Correct bad property"
	bl_idname = "object.correctproperty"
	bl_description = "Corrects bad properties"

	def execute(self, context):
		CorrectBadProperty()
		return {'FINISHED'}


#############################[...]#############################


def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_prop = bpy.props.StringProperty(default="default value")
	initObjectProperties()
	initSceneProperties()


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()