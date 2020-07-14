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

import sys
import bpy
import os
import string
import shutil
import bmesh
import requests 
import json
import addon_utils
from mathutils import Vector
from mathutils import Quaternion

def GetCurrentAddonRelase():
	#addon_ = bpy.context.preferences.addons["blender-for-unrealengine"]
	mod = sys.modules["blender-for-unrealengine"]
	v = mod.bl_info.get('version')
	letter = ""
	if len(v) > 3:
		if  v[3] == 1: letter = "b"
		if  v[3] == 2: letter = "c"
		if  v[3] == 3: letter = "d"
		if  v[3] == 4: letter = "e"
		if  v[3] == 5: letter = "f"
		if  v[3] == 6: letter = "g"
		
	return "v."+str(v[0])+"."+str(v[1])+"."+str(v[2])+letter

def is_deleted(o):
	try:
		return not (o.name in bpy.data.objects)
	except:
		return True
    

def GetCurrentSelect():
	#Return array for selected and the active

	activeObj = bpy.context.view_layer.objects.active
	SelectedObjs = bpy.context.selected_objects.copy()
	return([activeObj, SelectedObjs])

def SetCurrentSelect(SelectArray):
	#Get array select object and the active
	
	bpy.ops.object.select_all(action='DESELECT')
	for obj in SelectArray[1]:
		if not is_deleted(obj):
			if obj.name in bpy.context.window.view_layer.objects:
				obj.select_set(True)
	SelectArray[0].select_set(True)
	bpy.context.view_layer.objects.active = SelectArray[0]
	
def SelectSpecificObject(obj):
	
	bpy.ops.object.select_all(action='DESELECT')
	if obj.name in bpy.context.window.view_layer.objects:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = obj	
	


def ChecksRelationship(arrayA, arrayB):
	#Checks if it exits an identical variable in two lists
	
	for a in arrayA:
		for b in arrayB:
			if a == b:
				return True
	return False
	

def RemoveFolderTree(folder):
	try:
		if os.path.isdir(folder):
			shutil.rmtree(folder)
	except:
		print("remove folder fail. "+folder)

def GetChilds(obj):
	#Get all direct childs of a object

	ChildsObj = []
	for childObj in bpy.data.objects:
		if childObj.library == None:
			pare = childObj.parent
			if pare is not None:
				if pare.name == obj.name:
					ChildsObj.append(childObj)

	return ChildsObj

def getRootBoneParent(bone):
	if bone.parent is not None:
		return getRootBoneParent(bone.parent)
	return bone

def getFirstDeformBoneParent(bone):
	if bone.parent is not None:
		if bone.use_deform == True:
			return bone
		else:
			return getFirstDeformBoneParent(bone.parent)
	return bone

def SetCollectionUse(collection):
	#Set if collection is hide and selectable
	collection.hide_viewport = False
	collection.hide_select = False
	try:
		bpy.context.view_layer.layer_collection.children[collection.name].hide_viewport = False
	except:
		print(collection.name," not found in view_layer.layer_collection")
		pass

def GetRecursiveChilds(obj):
	#Get all recursive childs of a object

	saveObjs = []

	def tryAppend(obj):
		if obj.name in bpy.context.scene.objects:
			saveObjs.append(obj)

	for newobj in GetChilds(obj):
		for childs in GetRecursiveChilds(newobj):
			tryAppend(childs)
		tryAppend(newobj)
	return saveObjs

def ConvertToConvexHull(obj):
	#Convert obj to Convex Hull
	mesh = obj.data
	if not mesh.is_editmode:
		bm = bmesh.new()
		bm.from_mesh(mesh) #Mesh to Bmesh
		acb = bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
		#acb = bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
		bm.to_mesh(mesh) #BMesh to Mesh

def VerifiDirs(directory):
	#Check and create a folder if it does not exist

	if not os.path.exists(directory):
		os.makedirs(directory)


def ValidFilename(filename):
	# remove not allowed characters

	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in filename if c in valid_chars)
	return filename


def ResetArmaturePose(obj):
	#Reset armature pose

	for b in obj.pose.bones:
		b.rotation_quaternion = Quaternion((0,0,0),0)
		b.rotation_euler = Vector((0,0,0))
		b.scale = Vector((1,1,1))
		b.location = Vector((0,0,0))

def GetIfActionIsAssociated(action, boneNames):
	print(boneNames)
	for group in action.groups:
		for fcurve in group.channels:
			s=fcurve.data_path
			start = s.find('["')
			end = s.rfind('"]')
			if start>0 and end>0:
				substring = s[start+2:end]
				print(s)
				print(substring)
				if substring in boneNames:
					return True
	return False
	pass

def setWindowsClipboard(text):
	bpy.context.window_manager.clipboard = text
	#bpy.context.window_manager.clipboard.encode('utf8')

