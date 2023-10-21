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

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import os
import string
import shutil
import bpy
import bmesh
import addon_utils
import pathlib

def is_deleted(obj):
    """
    Checks if the specified Blender object has been deleted.

    Args:
        obj (bpy.types.Object): The Blender object to check.

    Returns:
        bool: True if the object has been deleted, False otherwise.
    """
    if obj and obj is not None:
        return obj.name not in bpy.data.objects
    else:
        return True


def check_plugin_is_activated(plugin_name):
    """
    Checks if a Blender plugin is activated.

    Args:
        plugin_name (str): The name of the plugin.

    Returns:
        bool: True if the plugin is enabled and loaded, False otherwise.
    """
    is_enabled, is_loaded = addon_utils.check(plugin_name)
    return is_enabled and is_loaded



def move_to_global_view():
    """
    Moves the active Blender viewport to the global view.

    Returns:
        None
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            if space.local_view:  # check if using local view
                for region in area.regions:
                    if region.type == 'WINDOW':
                        # override context and switch to global view
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.localview(override)





def checks_relationship(arrayA, arrayB):
    """
    Checks if there is an identical variable between two lists.

    Args:
        arrayA (list): The first list.
        arrayB (list): The second list.

    Returns:
        bool: True if an identical variable exists, False otherwise.
    """

    for a in arrayA:
        for b in arrayB:
            if a == b:
                return True
    return False


def remove_folder_tree(folder):
    """
    Removes a folder and its entire directory tree.

    Args:
        folder (str): The path to the folder to be removed.

    Returns:
        None
    """
    dirig_prefixath = pathlib.Path(folder)
    if dirig_prefixath.exists() and dirig_prefixath.is_dir():
        shutil.rmtree(dirig_prefixath, ignore_errors=True)


def get_childs(obj):
    """
    Retrieves all direct children of an object.

    Args:
        obj (bpy.types.Object): The parent object.

    Returns:
        list: A list of direct children objects.
    """
    childs_obj = []
    for child_obj in bpy.data.objects:
        if child_obj.library is None:
            parent = child_obj.parent
            if parent is not None:
                if parent.name == obj.name:
                    childs_obj.append(child_obj)

    return childs_obj


def get_root_bone_parent(bone):
    """
    Retrieves the root bone parent of a given bone.

    Args:
        bone (bpy.types.Bone): The bone to find the root bone parent for.

    Returns:
        bpy.types.Bone: The root bone parent.
    """
    if bone.parent is not None:
        return get_root_bone_parent(bone.parent)
    return bone


def get_first_deform_bone_parent(bone):
    """
    Retrieves the first deform bone parent of a given bone.

    Args:
        bone (bpy.types.Bone): The bone to find the first deform bone parent for.

    Returns:
        bpy.types.Bone: The first deform bone parent.
    """
    if bone.parent is not None:
        if bone.use_deform is True:
            return bone
        else:
            return get_first_deform_bone_parent(bone.parent)
    return bone


def set_collection_use(collection):
    """
    Sets the visibility and selectability of a collection.

    Args:
        collection (bpy.types.Collection): The collection to modify.

    Returns:
        None
    """
    collection.hide_viewport = False
    collection.hide_select = False
    layer_collection = bpy.context.view_layer.layer_collection
    if collection.name in layer_collection.children:
        layer_collection.children[collection.name].hide_viewport = False
    else:
        print(collection.name, "not found in view_layer.layer_collection")


def get_recursive_childs(obj):
    """
    Retrieves all recursive children of an object.

    Args:
        obj (bpy.types.Object): The parent object.

    Returns:
        list: A list of recursive children objects.
    """

    save_objs = []

    def try_append(obj):
        if obj.name in bpy.context.scene.objects:
            save_objs.append(obj)

    for new_obj in get_childs(obj):
        for child in get_recursive_childs(new_obj):
            try_append(child)
        try_append(new_obj)

    return save_objs


def convert_to_convex_hull(obj):
    """
    Converts an object to a convex hull.

    Args:
        obj (bpy.types.Object): The object to convert.

    Returns:
        None
    """
    mesh = obj.data
    if not mesh.is_editmode:
        bm = bmesh.new()
        bm.from_mesh(mesh)  # Mesh to Bmesh
        bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
        # convex_hull = bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
        # convex_hull = bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)  # BMesh to Mesh


def verify_dirs(directory):
    """
    Checks if a directory exists and creates it if it doesn't.

    Args:
        directory (str): The directory path to check.

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def valid_filename(filename):
    """
    Normalizes a string by removing non-alphanumeric characters for file name use.

    Args:
        filename (str): The input filename.

    Returns:
        str: The normalized filename.
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename


def valid_defname(filename):
    """
    Normalizes a string by removing non-alphanumeric characters for function name use.

    Args:
        filename (str): The input filename.

    Returns:
        str: The normalized filename.
    """
    valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename


def get_if_action_is_associated(action, bone_names):
    """
    Checks if the given action is associated with any of the specified bone names.

    Args:
        action (bpy.types.Action): The action to check.
        bone_names (list): List of bone names.

    Returns:
        bool: True if the action is associated with any bone in the list, False otherwise.
    """
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


def get_surface_area(obj):
    """
    Computes the surface area of a mesh object.

    Args:
        obj (bpy.types.Object): The mesh object.

    Returns:
        float: The surface area of the mesh object.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    area = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return area


def set_windows_clipboard(text):
    """
    Sets the text content to the clipboard.

    Args:
        text (str): The text to be set to the clipboard.

    Returns:
        None
    """
    bpy.context.window_manager.clipboard = text
    # bpy.context.window_manager.clipboard.encode('utf8')
