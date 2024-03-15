# ====================== BEGIN GPL LICENSE BLOCK ============================
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
# ======================= END GPL LICENSE BLOCK =============================

import os
import string
from pathlib import Path
import bpy
import shutil
import bmesh
import addon_utils

def GetAddonPrefs():
    return bpy.context.preferences.addons[__package__].preferences


def is_deleted(o):
    if o and o is not None:
        return not (o.name in bpy.data.objects)
    else:
        return True


def CheckPluginIsActivated(PluginName):
    is_enabled, is_loaded = addon_utils.check(PluginName)
    return is_enabled and is_loaded


def ChecksRelationship(arrayA, arrayB):
    # Checks if it exits an identical variable in two lists

    for a in arrayA:
        for b in arrayB:
            if a == b:
                return True
    return False


def nextPowerOfTwo(n):
    # compute power of two greater than or equal to n

    # decrement n (to handle cases when n itself
    # is a power of 2)
    n = n - 1

    # do till only one bit is left
    while n & n - 1:
        n = n & n - 1  # unset rightmost bit

    # n is now a power of two (less than n)
    return n << 1


def previousPowerOfTwo(n):
    # compute power of two less than or equal to n

    # do till only one bit is left
    while (n & n - 1):
        n = n & n - 1		# unset rightmost bit

    # n is now a power of two (less than or equal to n)
    return n


def RemoveFolderTree(folder):
    dirpath = Path(folder)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath, ignore_errors=True)


def GetChilds(obj):
    # Get all direct childs of a object

    ChildsObj = []
    for childObj in bpy.data.objects:
        if childObj.library is None:
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
        if bone.use_deform is True:
            return bone
        else:
            return getFirstDeformBoneParent(bone.parent)
    return bone


def SetCollectionUse(collection):
    # Set if collection is hide and selectable
    collection.hide_viewport = False
    collection.hide_select = False
    layer_collection = bpy.context.view_layer.layer_collection
    if collection.name in layer_collection.children:
        layer_collection.children[collection.name].hide_viewport = False
    else:
        print(collection.name, " not found in view_layer.layer_collection")


def GetRecursiveChilds(obj, include_self = False):
    # Get all recursive childs of a object
    # include_self is True obj is index 0

    saveObjs = []

    def tryAppend(obj):
        if obj.name in bpy.context.scene.objects:
            saveObjs.append(obj)

    if include_self:
        tryAppend(obj)

    for newobj in GetChilds(obj):
        for childs in GetRecursiveChilds(newobj):
            tryAppend(childs)
        tryAppend(newobj)
    return saveObjs


def ConvertToConvexHull(obj):
    # Convert obj to Convex Hull
    mesh = obj.data
    if not mesh.is_editmode:
        bm = bmesh.new()
        bm.from_mesh(mesh)  # Mesh to Bmesh
        convex_hull = bmesh.ops.convex_hull(
            bm, input=bm.verts,
            use_existing_faces=True
        )
        # convex_hull = bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)  # BMesh to Mesh


def VerifiDirs(directory):
    # Check and create a folder if it does not exist

    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False


def ValidDirName(directory):
    # https://gist.github.com/seanh/93666
    # Normalizes string, removes non-alpha characters
    # File name use

    illegal_chars = r':*?"<>|'
    directory = ''.join(c for c in directory if c not in illegal_chars)

    return directory


def ValidFilename(filename):
    # https://gist.github.com/seanh/93666
    # Normalizes string, removes non-alpha characters
    # File name use

    illegal_chars = r'\/:*?"<>|'
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    filename = ''.join(c for c in filename if c not in illegal_chars)
    filename = ''.join(c for c in filename if c in valid_chars)

    return filename


def ValidDefname(filename):
    # https://gist.github.com/seanh/93666
    # Normalizes string, removes non-alpha characters
    # Def name use

    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename


def GetIfActionIsAssociated(action, bone_names):
    for group in action.groups:
        for fcurve in group.channels:
            s = fcurve.data_path
            start = s.find('["')
            end = s.rfind('"]')
            if start > 0 and end > 0:
                substring = s[start+2:end]
                if substring in bone_names:
                    return True
    return False


def GetSurfaceArea(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    area = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return area


def setWindowsClipboard(text):
    bpy.context.window_manager.clipboard = text
    # bpy.context.window_manager.clipboard.encode('utf8')
