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

import json
import copy
import bpy
import mathutils


class SavedObject():
    """
    Saved data from a blender object.
    """

    def __init__(self, obj: bpy.types.Object):
        if obj:
            self.ref = obj
            self.name = obj.name
            self.select = obj.select_get()
            self.hide = obj.hide_get()
            self.hide_select = obj.hide_select
            self.hide_viewport = obj.hide_viewport


class SavedBones():
    """
    Saved data from a blender armature bone.
    """

    def __init__(self, bone):
        if bone:
            self.name = bone.name
            self.select = bone.select
            self.hide = bone.hide


class SavedCollection():
    """
    Saved data from a blender collection.
    """

    def __init__(self, col):
        if col:
            self.ref = col
            self.name = col.name
            self.hide_select = col.hide_select
            self.hide_viewport = col.hide_viewport


class SavedViewLayerChildren():
    """
    Saved data from a blender ViewLayerChildren.
    """

    def __init__(self, vlayer, childCol):
        if childCol:
            self.vlayer_name = vlayer.name
            self.name = childCol.name
            self.exclude = childCol.exclude
            self.hide_viewport = childCol.hide_viewport


class UserSelectSave():
    """
    Manager for user selection.
    """

    def __init__(self):
        # Select
        self.user_active = None
        self.user_active_name = ""
        self.user_selecteds = []
        self.user_selected_names = []

        # Stats
        self.user_mode = None

    def save_current_select(self):
        """
        Save user selection.
        """

        # Save data (This can take time)

        # Select
        self.user_active = bpy.context.active_object  # Save current active object
        if self.user_active:
            self.user_active_name = self.user_active.name

        self.user_selecteds = bpy.context.selected_objects  # Save current selected objects
        self.user_selected_names = [obj.name for obj in bpy.context.selected_objects]


    def reset_select_by_ref(self):
        """
        Reset user selection at the last save. (Use objects refs)
        """

        self.save_mode()
        safe_mode_set("OBJECT", bpy.ops.object)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:  # Resets previous selected object if still exist
            if obj in self.user_selecteds:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = self.user_active

        self.reset_mode_at_save()

    def reset_select_by_name(self):
        """
        Reset user selection at the last save. (Use objects names)
        """

        self.save_mode()
        safe_mode_set("OBJECT", bpy.ops.object)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.name in self.user_selected_names:
                if obj.name in bpy.context.view_layer.objects:
                    bpy.data.objects[obj.name].select_set(True)  # Use the name because can be duplicated name

        if self.user_active_name != "":
            if self.user_active_name in bpy.data.objects:
                if self.user_active_name in bpy.context.view_layer.objects:
                    bpy.context.view_layer.objects.active = bpy.data.objects[self.user_active_name]

        self.reset_mode_at_save()

    def save_mode(self):
        """
        Save user mode.
        """
        if self.user_active:
            if bpy.ops.object.mode_set.poll():
                self.user_mode = self.user_active.mode  # Save current mode

    def reset_mode_at_save(self):
        """
        Reset user mode at the last save.
        """
        if self.user_mode:
            safe_mode_set(self.user_mode, bpy.ops.object)

def select_specific_object(obj: bpy.types.Object):
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


class UserSceneSave():
    """
    Manager for saving and resetting the user scene.
    """

    def __init__(self):
        # Select
        self.user_select_class = UserSelectSave()

        self.user_bone_active = None
        self.user_bone_active_name = ""

        # Stats
        self.user_mode = None
        self.use_simplify = False

        # Data
        self.objects = []
        self.object_bones = []
        self.collections = []
        self.view_layer_collections = []
        self.action_names = []
        self.collection_names = []

    def save_current_scene(self):
        """
        Save the current scene data.
        """
        # Save data (This can take time)
        c = bpy.context
        # Select
        self.user_select_class.save_current_select()

        # Stats
        if self.user_select_class.user_active:
            if bpy.ops.object.mode_set.poll():
                self.user_mode = self.user_select_class.user_active.mode  # Save current mode
        self.use_simplify = bpy.context.scene.render.use_simplify

        # Data
        for obj in bpy.data.objects:
            self.objects.append(SavedObject(obj))
        for col in bpy.data.collections:
            self.collections.append(SavedCollection(col))
        for vlayer in c.scene.view_layers:
            layer_collections = get_layer_collections_recursive(vlayer.layer_collection)
            for layer_collection in layer_collections:
                self.view_layer_collections.append(SavedViewLayerChildren(vlayer, layer_collection))
        for action in bpy.data.actions:
            self.action_names.append(action.name)
        for collection in bpy.data.collections:
            self.collection_names.append(collection.name)

        # Data for armature
        if self.user_select_class.user_active:
            if self.user_select_class.user_active.type == "ARMATURE":
                if self.user_select_class.user_active.data.bones.active:
                    self.user_bone_active = self.user_select_class.user_active.data.bones.active
                    self.user_bone_active_name = self.user_select_class.user_active.data.bones.active.name
                for bone in self.user_select_class.user_active.data.bones:
                    self.object_bones.append(SavedBones(bone))

    def reset_select_by_ref(self):
        """
        Reset the user selection based on object references.
        """
        self.user_select_class.reset_select_by_ref()
        self.reset_bones_select_by_name()

    def reset_select_by_name(self):
        """
        Reset the user selection based on object names.
        """
        self.user_select_class.reset_select_by_name()
        self.reset_bones_select_by_name()

    def reset_bones_select_by_name(self):
        """
        Reset bone selection by name (works only in pose mode).
        """
        # Work only in pose mode!
        if len(self.object_bones) > 0:
            if self.user_select_class.user_active:
                if bpy.ops.object.mode_set.poll():
                    if self.user_select_class.user_active.mode == "POSE":
                        bpy.ops.pose.select_all(action='DESELECT')
                        for bone in self.object_bones:
                            if bone.select:
                                if bone.name in self.user_select_class.user_active.data.bones:
                                    self.user_select_class.user_active.data.bones[bone.name].select = True

                        if self.user_bone_active_name is not None:
                            if self.user_bone_active_name in self.user_select_class.user_active.data.bones:
                                new_active = self.user_select_class.user_active.data.bones[self.user_bone_active_name]
                                self.user_select_class.user_active.data.bones.active = new_active

    def reset_mode_at_save(self):
        """
        Reset the user mode at the last save.
        """
        if self.user_mode:
            safe_mode_set(self.user_mode, bpy.ops.object)

    def reset_scene_at_save(self, print_removed_items = False):
        """
        Reset the user scene to at the last save.
        """
        scene = bpy.context.scene
        self.reset_mode_at_save()

        bpy.context.scene.render.use_simplify = self.use_simplify

        # Reset hide and select (bpy.data.objects)
        for obj in self.objects:
            try:
                if obj.ref:
                    if obj.ref.hide_select != obj.hide_select:
                        obj.ref.hide_select = obj.hide_select
                    if obj.ref.hide_viewport != obj.hide_viewport:
                        obj.ref.hide_viewport = obj.hide_viewport
                    if obj.ref.hide_get() != obj.hide:
                        obj.ref.hide_set(obj.hide)
                else:
                    if print_removed_items:
                        print(f"/!\\ {obj.name} not found.")
            except ReferenceError:
                if print_removed_items:
                    print(f"/!\\ {obj.name} has been removed.")

        # Reset hide and select (bpy.data.collections)
        for col in self.collections:
            try:
                if col.ref.name in bpy.data.collections:
                    if col.ref.hide_select != col.hide_select:
                        col.ref.hide_select = col.hide_select
                    if col.ref.hide_viewport != col.hide_viewport:
                        col.ref.hide_viewport = col.hide_viewport
                else:
                    if print_removed_items:
                        print(f"/!\\ {col.name} not found.")
            except ReferenceError:
                if print_removed_items:
                    print(f"/!\\ {col.name} has been removed.")

        # Reset hide and viewport (collections from view_layers)
        for vlayer in scene.view_layers:
            layer_collections = get_layer_collections_recursive(vlayer.layer_collection)

            def get_layer_collection_in_list(name, collections):
                for layer_collection in collections:
                    if layer_collection.name == name:
                        return layer_collection

            for view_layer_collection in self.view_layer_collections:
                if view_layer_collection.vlayer_name == vlayer.name:
                    layer_collection = get_layer_collection_in_list(view_layer_collection.name, layer_collections)
                    if layer_collection:
                        if layer_collection.exclude != view_layer_collection.exclude:
                            layer_collection.exclude = view_layer_collection.exclude
                        if layer_collection.hide_viewport != view_layer_collection.hide_viewport:
                            layer_collection.hide_viewport = view_layer_collection.hide_viewport


class UserArmatureDataSave():
    """
    Manager for saving and resetting an armature.
    """
        
    def __init__(self, armature):
        # Select
        self.armature = armature

        # Stats
        # Data
        self.use_mirror_x = False

    def save_current_armature(self):
        """
        Save the current armature data.
        """
        if self.armature is None:
            return
        # Select
        # Stats
        # Data
        self.use_mirror_x = self.armature.data.use_mirror_x

    def reset_armature_at_save(self):
        """
        Reset the armature to the state at the last save.
        """
        if self.armature is None:
            return

        # Select
        # Stats
        # Data
        self.armature.data.use_mirror_x = self.use_mirror_x

def mode_set_on_target(target_object=None, target_mode='OBJECT'):
    """
    Set the target object to the specified mode.
    """
    # Exit current mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if target_object:
        target_object.select_set(state=True)
        bpy.context.view_layer.objects.active = target_object

    # Enter new mode
    if bpy.context.active_object:
        bpy.ops.object.mode_set(mode=target_mode)
        return True
    return False

def safe_mode_set(target_mode='OBJECT', obj=None):
    """
    Set the mode of the target object to the specified mode if possible.
    """
    if bpy.ops.object.mode_set.poll():
        if obj:
            if obj.mode != target_mode:
                bpy.ops.object.mode_set(mode=target_mode)
                return True
        else:
            bpy.ops.object.mode_set(mode=target_mode)
            return True

    return False

def json_list(string):
    """
    Convert a JSON string to a list of dictionaries.
    """
    if string is None or string == "":
        return []

    jdata = json.loads(string)
    return list(jdata)

def clear_driver_var(d):
    """
    Clear all variables from a driver.
    """
    #d.variables.clear()
    for var in d.variables:
        d.variables.remove(var)

def update_bone_rot_mode(armature, bone_name, rotation_mode):
    """
    Update the rotation mode of a specific bone in an armature.
    """
    armature.pose.bones[bone_name].rotation_mode = rotation_mode

def get_visual_bone_pos(obj, bone):
    """
    Get the visual position, rotation, and scale of a bone in object space.
    """
    matrix_pose = obj.matrix_world @ bone.matrix
    loc = matrix_pose @ mathutils.Vector((0, 0, 0))
    rot = matrix_pose.to_euler()
    scale = bone.scale
    return loc, rot, scale

def get_visual_bones_pos_packed(obj, target_bones):
    """
    Get the visual positions, rotations, and scales of multiple bones in object space and pack them into a list.
    """
    position_list = []
    for bone in target_bones:
        loc, rot, scale = get_visual_bone_pos(obj, bone)
        position_list.append((bone.name, loc, rot, scale))
    return position_list

def apply_real_matrix_world_bones(bone, obj, matrix):
    """
    Apply the real matrix world to a bone, considering constraints.
    """
    for cons in bone.constraints:
        if cons.type == "CHILD_OF" and not cons.mute and cons.target is not None:
            child = cons.inverse_matrix
            if cons.target.type == "ARMATURE":
                parent = obj.matrix_world @ obj.pose.bones[cons.subtarget].matrix
            else:
                parent = cons.target.matrix_world
            bone.matrix = obj.matrix_world.inverted() @ (child.inverted() @ parent.inverted() @ matrix)
            return
    bone.matrix = obj.matrix_world.inverted() @ matrix

def set_visual_bone_pos(obj, bone, loc, rot, scale, use_loc, use_rot, use_scale):
    """
    Set the visual position, rotation, and scale of a bone, allowing control over which values to apply.
    """
    # Save
    base_loc = copy.deepcopy(bone.location)
    base_scale = copy.deepcopy(bone.scale)
    rot_mode_base = copy.deepcopy(bone.rotation_mode)
    base_rot = copy.deepcopy(bone.rotation_euler)
    base_quaternion = copy.deepcopy(bone.rotation_quaternion)

    # ApplyPos
    mat_loc = mathutils.Matrix.Translation(loc)
    mat_rot = rot.to_matrix().to_4x4()
    matrix = mat_loc @ mat_rot
    apply_real_matrix_world_bones(bone, obj, matrix)
    bone.scale = scale

    # ResetNotDesiredValue
    if not use_loc:
        bone.location = base_loc
    if not use_rot:
        bone.rotation_euler = base_rot
        bone.rotation_quaternion = base_quaternion
        bone.rotation_mode = rot_mode_base
    if not use_scale:
        bone.scale = base_scale

def find_item_in_list_by_name(item, lst):
    """
    Find an item in a list by its name.
    """
    for target_item in lst:
        if target_item.name == item:
            return target_item
    return None

def set_visual_bones_pos_packed(obj, target_bones, position_list, use_loc, use_rot, use_scale):
    """
    Set the visual positions, rotations, and scales of multiple bones using a packed position list,
    allowing control over which values to apply.
    """
    for pl in position_list:
        target_bone = find_item_in_list_by_name(pl[0], target_bones)
        if target_bone is not None:
            loc = mathutils.Vector(pl[1])
            rot = mathutils.Euler(pl[2], 'XYZ')
            scale = mathutils.Vector(pl[3])
            set_visual_bone_pos(obj, target_bone, loc, rot, scale, use_loc, use_rot, use_scale)

def get_safe_collection(collection_name):
    """
    Get an existing collection with the given name, or create a new one if it doesn't exist.
    """
    if collection_name in bpy.data.collections:
        my_col = bpy.data.collections[collection_name]
    else:
        my_col = bpy.data.collections.new(collection_name)
    return my_col

def get_recursive_layer_collection(layer_collection):
    """
    Get all recursive child collections of a layer collection.
    """
    all_childs = []
    for child in layer_collection.children:
        all_childs.append(child)
        all_childs += get_recursive_layer_collection(child)
    return all_childs

def set_collection_exclude(collection, exclude):
    """
    Set the exclude property for a collection in all view layers.
    """
    scene = bpy.context.scene
    for vl in scene.view_layers:
        for layer in get_recursive_layer_collection(vl.layer_collection):
            if layer.collection == collection:
                layer.exclude = exclude

def get_rig_collection(armature, col_type="RIG"):
    """
    Get the rig collection for an armature, optionally creating additional sub-collections based on col_type.
    """
    #TO DO: Move this in Modular Auto Rig Addon.
    rig_col = get_safe_collection(armature.users_collection[0].name)

    if col_type == "RIG":
        return rig_col
    elif col_type == "SHAPE":
        shape_col = get_safe_collection(armature.name + "_RigShapes")
        if shape_col.name not in rig_col.children:
            rig_col.children.link(shape_col)
        return shape_col
    elif col_type == "CURVE":
        curve_col = get_safe_collection(armature.name + "_RigCurves")
        if curve_col.name not in rig_col.children:
            rig_col.children.link(curve_col)
        return curve_col
    elif col_type == "CAMERA":
        camera_col = get_safe_collection(armature.name + "_RigCameras")
        if camera_col.name not in rig_col.children:
            rig_col.children.link(camera_col)
        return camera_col
    else:
        print("In get_rig_collection() " + col_type + " not found!")

def get_vertex_colors(obj):
    """
    Get the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes
    else:
        return obj.data.vertex_colors

def get_vertex_colors_render_color_index(obj):
    """
    Get the render color index of the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.render_color_index
    else:
        for index, vertex_color in enumerate(obj.data.vertex_colors):
            if vertex_color.active_render:
                return index

def get_vertex_color_active_color_index(obj):
    """
    Get the active color index of the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.active_color_index
    else:
        return obj.data.vertex_colors.active_index

def get_layer_collections_recursive(layer_collection):
    """
    Get all recursive child layer collections of a layer collection.
    """
    layer_collections = []
    layer_collections.append(layer_collection)  # Add current
    for child_col in layer_collection.children:
        layer_collections.extend(get_layer_collections_recursive(child_col))  # Add child collections recursively

    return layer_collections

def get_mirror_object_name(original_objects):
    """
    Get the mirror object name for the given objects(s).
    """
    objects = []
    new_objects = []

    if not isinstance(original_objects, list):
        objects = [original_objects]  # Convert to list
    else:
        objects = original_objects

    def try_to_invert_bones(bone):
        def invert(bone, old, new):
            if bone.endswith(old):
                new_object_name = bone[:-len(old)]
                new_object_name = new_object_name + new
                return new_object_name
            return None

        change = [
            ["_l", "_r"],
            ["_L", "_R"]
        ]
        for c in change:
            a = invert(bone, c[0], c[1])
            if a:
                return a
            b = invert(bone, c[1], c[0])
            if b:
                return b

        # Return original If no invert found.
        return bone

    for bone in objects:
        new_objects.append(try_to_invert_bones(bone))

    # Can return same bone when don't found mirror
    if not isinstance(original_objects, list):
        return new_objects[0]
    else:
        return new_objects


class SaveTransformObject():
    def __init__(self, obj: bpy.types.Object):
        self.init_object = obj
        self.transform_matrix = obj.matrix_world.copy()

    def reset_object_transform(self):
        self.init_object.matrix_world = self.transform_matrix

    def apply_object_transform(self, obj):
        obj.matrix_world = self.transform_matrix

def make_override_library_object(obj):
    select_specific_object(obj)
    bpy.ops.object.make_override_library()

def recursive_delete_collection(collection: bpy.types.Collection):
    """
    Recursively deletes a Blender collection and its contents, including objects and their data,
    as well as any child collections.

    Parameters:
    - collection (bpy.types.Collection): The Blender collection to be deleted.

    Returns:
    None
    """
    # First, prepare a list of objects and their data to remove from the collection
    objects_to_remove = [obj for obj in collection.objects]
    data_to_remove = [obj.data for obj in collection.objects if obj.data is not None]

    # Use Blender's batch_remove to efficiently delete objects and their data
    bpy.data.batch_remove(objects_to_remove)
    bpy.data.batch_remove(data_to_remove)
    
    # Recursively delete any child collections
    for sub_collection in collection.children:
        recursive_delete_collection(sub_collection)
    
    # Finally, delete the collection itself
    bpy.data.collections.remove(collection)

class SaveUserRenderSimplify():
    def __init__(self):
        self.use_simplify = bpy.context.scene.render.use_simplify

    def LoadUserRenderSimplify(self):
        bpy.context.scene.render.use_simplify = self.use_simplify


class SaveObjectReferanceUser():
    """
    This class is used to save and update references to an object in constraints 
    across all bones in all armatures within a Blender scene.
    """

    def __init__(self):
        """
        Initializes the instance with an empty list to store constraints using the specified object.
        """
        self.using_constraints = []

    def save_refs_from_object(self, obj: bpy.types.Object):
        """
        Scans all objects in the Blender scene to find and save constraints in armature bones
        that reference the specified object.

        :param obj: The target bpy.types.Object to find references to.
        """
        for objet in bpy.data.objects:
            if objet.type == 'ARMATURE':
                for bone in objet.pose.bones:
                    for contrainte in bone.constraints:
                        if hasattr(contrainte, 'target') and contrainte.target and contrainte.target.name == obj.name:
                            constraint_info = {
                                'armature_object': objet.name,
                                'bone': bone.name,
                                'constraint': contrainte.name
                            }
                            self.using_constraints.append(constraint_info)
    
    def update_refs_with_object(self, obj: bpy.types.Object):
        """
        Updates all previously found constraints to reference a new object.

        :param obj: The new bpy.types.Object to be used as the target for the saved constraints.
        """
        for info in self.using_constraints:
            if info['armature_object'] in bpy.data.objects:
                armature_object = bpy.data.objects[info['armature_object']]
                if info['bone'] in armature_object.pose.bones:
                    bone = armature_object.pose.bones[info['bone']]
                    if info['constraint'] in bone.constraints:
                        constraint = bone.constraints[info['constraint']]
                        constraint.target = obj

def active_mode_is(targetMode):
    # Return True is active obj mode == targetMode
    obj = bpy.context.active_object
    if obj is not None:
        if obj.mode == targetMode:
            return True
    return False

def active_type_is(targetType):
    # Return True is active obj type == targetType
    obj = bpy.context.active_object
    if obj is not None:
        if obj.type == targetType:
            return True
    return False

def active_type_is_not(targetType):
    # Return True is active obj type != targetType
    obj = bpy.context.active_object
    if obj is not None:
        if obj.type != targetType:
            return True
    return False

def found_type_in_selection(targetType, include_active=True):
    # Return True if a specific type is found in current user selection
    select = bpy.context.selected_objects
    if not include_active:
        if bpy.context.active_object:
            if bpy.context.active_object in select:
                select.remove(bpy.context.active_object)

    for obj in select:
        if obj.type == targetType:
            return True
    return False