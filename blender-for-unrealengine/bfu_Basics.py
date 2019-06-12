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
import os
import string
import bmesh
from mathutils import Vector
from mathutils import Quaternion

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
		pare = childObj.parent
		if pare is not None:
			if pare.name == obj.name:
				ChildsObj.append(childObj)

	return ChildsObj

def getFirstDeformBoneParent(bone):
	if bone.parent is not None:
		if bone.use_deform == True:
			return bone
		else:
			return getFirstDeformBoneParent(bone.parent)
	return bone

def GetRecursiveChilds(obj):
	#Get all recursive childs of a object
	
	saveObjs = []
	
	def tryAppend(obj):
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

	for x in obj.pose.bones:
		x.rotation_quaternion = Quaternion((0,0,0),0)
		x.rotation_euler = Vector((0,0,0))
		x.scale = Vector((1,1,1))
		x.location = Vector((0,0,0))
	bpy.context.scene.update()
		
def setWindowsClipboard(text):
	bpy.context.window_manager.clipboard = text
	#bpy.context.window_manager.clipboard.encode('utf8') 
	
	