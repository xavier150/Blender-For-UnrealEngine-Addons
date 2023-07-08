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
#  xavierloux.com
# ----------------------------------------------

import os
import string
from pathlib import Path
import bpy
import shutil
import bmesh
import addon_utils
from mathutils import Vector
from mathutils import Quaternion


def is_tweak_mode():
    """
    Checks if the Blender scene is in tweak mode.

    Returns:
        bool: True if the scene is in tweak mode, False otherwise.
    """
    return bpy.context.scene.is_nla_tweakmode


def enter_tweak_mode():
    """
    Enters tweak mode in the Blender NLA editor.

    Returns:
        None
    """
    # TO DO
    # bpy.ops.nla.tweakmode_enter()
    pass


def exit_tweak_mode():
    """
    Exits tweak mode in the Blender NLA editor.

    Returns:
        None
    """
    # TO DO
    # bpy.ops.nla.tweakmode_exit()
    pass


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


def get_current_selection():
    """
    Retrieves the current selection in Blender, including the active object.

    Returns:
        MyClass: An instance of the MyClass object containing the active object and selected objects.
    """
    class MyClass:
        """
        Helper class to store the active object and selected objects.
        """
        def __init__(self):
            self.active = None
            self.selected_objects = []
            self.old_name = []

        def remove_from_list(self, objs):
            """
            Removes objects from the selected_objects and old_name lists.

            Args:
                objs (list): List of objects to remove.

            Returns:
                None
            """
            for x, obj in enumerate(objs):
                if obj in self.selected_objects:
                    self.selected_objects.remove(obj)
                    self.old_name.remove(self.old_name[x])

        def remove_from_list_by_name(self, name_list):
            """
            Removes objects from the selected_objects and old_name lists based on object names.

            Args:
                name_list (list): List of object names to remove.

            Returns:
                None
            """
            for obj_name in name_list:
                if obj_name in self.old_name:
                    x = self.old_name.index(obj_name)
                    del self.selected_objects[x]
                    del self.old_name[x]

        def debug_object_list(self):
            """
            Prints the selected_objects and old_name lists for debugging purposes.

            Returns:
                None
            """
            print("DebugObjectList ##########################################")
            print(self.selected_objects)
            print(self.old_name)

    selected = MyClass()
    selected.active = bpy.context.view_layer.objects.active
    selected.selected_objects = bpy.context.selected_objects.copy()
    for sel in selected.selected_objects:
        selected.old_name.append(sel.name)
    return selected


def set_current_selection(selection):
    """
    Sets the current selection in Blender based on the provided selection object.

    Args:
        selection (MyClass): The selection object containing the active object and selected objects.

    Returns:
        None
    """

    bpy.ops.object.select_all(action='DESELECT')
    for x, obj in enumerate(selection.selected_objects):
        if not is_deleted(obj):
            if obj.name in bpy.context.window.view_layer.objects:
                obj.select_set(True)
    selection.active.select_set(True)
    bpy.context.view_layer.objects.active = selection.active


def select_specific_object(obj):
    """
    Selects a specific object in Blender.

    Args:
        obj (bpy.types.Object): The object to be selected.

    Returns:
        None
    """

    bpy.ops.object.select_all(action='DESELECT')
    if obj.name in bpy.context.window.view_layer.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


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


def next_power_of_two(n):
    """
    Computes the next power of two that is greater than or equal to n.

    Args:
        n (int): The input number.

    Returns:
        int: The next power of two greater than or equal to n.
    """
    # decrement n (to handle cases when n itself
    # is a power of 2)
    n = n - 1

    # do till only one bit is left
    while n & n - 1:
        n = n & n - 1  # unset rightmost bit

    # n is now a power of two (less than n)
    return n << 1


def previous_power_of_two(n):
    """
    Computes the previous power of two that is less than or equal to n.

    Args:
        n (int): The input number.

    Returns:
        int: The previous power of two less than or equal to n.
    """
    # do till only one bit is left
    while (n & n - 1):
        n = n & n - 1		# unset rightmost bit

    # n is now a power of two (less than or equal to n)
    return n


def nearest_power_of_two(value):
    """
    Computes the nearest power of two to the given value.

    Args:
        value (int): The input value.

    Returns:
        int: The nearest power of two.
    """
    if value < 2:
        return 2

    a = previous_power_of_two(value)
    b = next_power_of_two(value)

    if value - a < b - value:
        return a
    else:
        return b


def remove_folder_tree(folder):
    """
    Removes a folder and its entire directory tree.

    Args:
        folder (str): The path to the folder to be removed.

    Returns:
        None
    """
    dirpath = Path(folder)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath, ignore_errors=True)


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
        convex_hull = bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
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


def reset_armature_pose(obj):
    """
    Resets the pose of an armature object.

    Args:
        obj (bpy.types.Object): The armature object.

    Returns:
        None
    """
    for b in obj.pose.bones:
        b.rotation_quaternion = Quaternion((0, 0, 0), 0)
        b.rotation_euler = Vector((0, 0, 0))
        b.scale = Vector((1, 1, 1))
        b.location = Vector((0, 0, 0))


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
