# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import json
import copy
import bpy
import mathutils
from typing import List, Optional, Dict, Any, Tuple, Union

def select_specific_object_list(active: Optional[bpy.types.Object], objs: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """
    - Deselect all
    - Selects a specific list object in Blender.

    Args:
        obj (bpy.types.Object): The object to be selected.

    Returns:
        None
    """
    view_layer = bpy.context.view_layer
    if view_layer is None:
        print("In select_specific_object_list the view_layer is None!")
        return []
    if active is None:
        print("In select_specific_object_list the active object is None!")
        return []
    if active.name not in view_layer.objects:
        print(f"The active object {active.name} not found in bpy.context.view_layer.objects!")
        return []

    selected_objs: List[bpy.types.Object] = []

    # Deselect all
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    view_layer.objects.active = None

    # Select specific objects
    for obj in objs:
        if obj.name in view_layer.objects:
            obj.select_set(True)  # type: ignore
            selected_objs.append(obj)

    # Set active at end
    active.select_set(True)  # type: ignore
    view_layer.objects.active = active
    selected_objs.append(active)

    return selected_objs

def select_specific_object(active: Optional[bpy.types.Object]) -> Optional[bpy.types.Object]:
    """
    - Deselect all
    - Selects a specific object in Blender.

    Args:
        obj (bpy.types.Object): The object to be selected.

    Returns:
        None
    """

    view_layer = bpy.context.view_layer
    if view_layer is None:
        print("In select_specific_object the view_layer is None!")
        return None
    if active is None:
        print("In select_specific_object the active object is None!")
        return None
    if active.name not in view_layer.objects:
        print(f"The active object {active.name} not found in bpy.context.view_layer.objects!")
        return None

    # Deselect all
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    view_layer.objects.active = None

    # Select specific object and set active
    active.select_set(True)  # type: ignore
    view_layer.objects.active = active
    return active

class UserArmatureDataSave():
    """
    Manager for saving and resetting an armature.
    """

    def __init__(self, armature: Optional[bpy.types.Object]):
        # Select
        self.armature: Optional[bpy.types.Object] = armature

        # Stats
        # Data
        self.use_mirror_x: bool = False

    def save_current_armature(self):
        """
        Save the current armature data.
        """
        if self.armature is None:
            return
        # Select
        # Stats
        # Data
        self.use_mirror_x = self.armature.data.use_mirror_x  # type: ignore

    def reset_armature_at_save(self):
        """
        Reset the armature to the state at the last save.
        """
        if self.armature is None:
            return

        # Select
        # Stats
        # Data
        self.armature.data.use_mirror_x = self.use_mirror_x  # type: ignore

def mode_set_on_target(target_object: Optional[bpy.types.Object] = None, target_mode: str = 'OBJECT'):
    """
    Set the target object to the specified mode.
    """
    if bpy.context.view_layer:
        # Exit current mode
        if bpy.ops.object.mode_set.poll():  # type: ignore
            bpy.ops.object.mode_set(mode='OBJECT')  # type: ignore

        if target_object:
            target_object.select_set(state=True)  # type: ignore
            bpy.context.view_layer.objects.active = target_object

        # Enter new mode
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode=target_mode)  # type: ignore
            return True
    return False

def safe_mode_set(target_mode: str = 'OBJECT', obj: Optional[bpy.types.Object] = None):
    """
    Set the mode of the target object to the specified mode if possible.
    """
    if bpy.ops.object.mode_set.poll():  # type: ignore
        if obj:
            if obj.mode != target_mode:  # type: ignore
                bpy.ops.object.mode_set(mode=target_mode)  # type: ignore
                return True
        else:
            bpy.ops.object.mode_set(mode=target_mode)  # type: ignore
            return True

    return False

def json_list(string: Optional[str]) -> List[Dict[str, Any]]:
    """
    Convert a JSON string to a list of dictionaries.
    """
    if string is None or string == "":
        return []

    json_data = json.loads(string)
    return list(json_data)

def clear_driver_var(driver: bpy.types.Driver):
    """
    Clear all variables from a driver.
    """
    for var in driver.variables:
        driver.variables.remove(var)  # type: ignore

def update_bone_rot_mode(armature: bpy.types.Object, bone_name: str, rotation_mode: str) -> None:
    """
    Update the rotation mode of a specific bone in an armature.
    """
    if armature.pose:
        armature.pose.bones[bone_name].rotation_mode = rotation_mode  # type: ignore

def get_visual_bone_pos(obj: bpy.types.Object, bone: bpy.types.PoseBone) -> Tuple[mathutils.Vector, mathutils.Euler, mathutils.Vector]:
    """
    Get the visual position, rotation, and scale of a bone in object space.
    """
    matrix_pose = obj.matrix_world @ bone.matrix
    loc = matrix_pose @ mathutils.Vector((0, 0, 0))
    rot = matrix_pose.to_euler()
    scale = bone.scale
    return loc, rot, scale

def get_visual_bones_pos_packed(obj: bpy.types.Object, target_bones: List[bpy.types.PoseBone]) -> List[Tuple[str, mathutils.Vector, mathutils.Euler, mathutils.Vector]]:
    """
    Get the visual positions, rotations, and scales of multiple bones in object space and pack them into a list.
    """
    position_list: List[Tuple[str, mathutils.Vector, mathutils.Euler, mathutils.Vector]] = []
    for bone in target_bones:
        loc, rot, scale = get_visual_bone_pos(obj, bone)
        position_list.append((bone.name, loc, rot, scale))
    return position_list

def apply_real_matrix_world_bones(bone: bpy.types.PoseBone, obj: bpy.types.Object, matrix: mathutils.Matrix):
    """
    Apply the real matrix world to a bone, considering constraints.
    """
    for cons in bone.constraints:
        if cons.type == "CHILD_OF" and not cons.mute and cons.target is not None:  # type: ignore
            child = cons.inverse_matrix  # type: ignore
            child: mathutils.Matrix
            if cons.target.type == "ARMATURE":  # type: ignore
                parent = obj.matrix_world @ obj.pose.bones[cons.subtarget].matrix  # type: ignore
                parent: mathutils.Matrix
            else:
                parent = cons.target.matrix_world  # type: ignore
                parent: mathutils.Matrix
            bone.matrix = obj.matrix_world.inverted() @ (child.inverted() @ parent.inverted() @ matrix)  # type: ignore
            return
    bone.matrix = obj.matrix_world.inverted() @ matrix

def set_visual_bone_pos(
    obj: bpy.types.Object, 
    bone: bpy.types.PoseBone, 
    loc: mathutils.Vector, 
    rot: mathutils.Euler, 
    scale: mathutils.Vector, 
    use_loc: bool, 
    use_rot: bool, 
    use_scale: bool
):
    """
    Set the visual position, rotation, and scale of a bone, allowing control over which values to apply.
    """
    # Save
    base_loc = copy.deepcopy(bone.location)
    base_scale = copy.deepcopy(bone.scale)
    rot_mode_base = copy.deepcopy(bone.rotation_mode)  # type: ignore
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
        bone.rotation_mode = rot_mode_base  # type: ignore
    if not use_scale:
        bone.scale = base_scale

def find_item_in_list_by_name(item: str, lst: List[bpy.types.PoseBone]) -> Optional[bpy.types.PoseBone]:
    """
    Find an item in a list by its name.
    """
    for target_item in lst:
        if target_item.name == item:
            return target_item
    return None

def set_visual_bones_pos_packed(
    obj: bpy.types.Object, 
    target_bones: List[bpy.types.PoseBone], 
    position_list: List[Tuple[str, mathutils.Vector, mathutils.Euler, mathutils.Vector]], 
    use_loc: bool, 
    use_rot: bool, 
    use_scale: bool
) -> None:
    """
    Set the visual positions, rotations, and scales of multiple bones using a packed position list,
    allowing control over which values to apply.
    """
    for pl in position_list:
        target_bone = find_item_in_list_by_name(pl[0], target_bones)
        if target_bone is not None:
            loc = mathutils.Vector(pl[1])  # type: ignore
            rot = mathutils.Euler(pl[2], 'XYZ')  # type: ignore
            scale = mathutils.Vector(pl[3])  # type: ignore
            set_visual_bone_pos(obj, target_bone, loc, rot, scale, use_loc, use_rot, use_scale)

def get_safe_collection(collection_name: str) -> bpy.types.Collection:
    """
    Get an existing collection with the given name, or create a new one if it doesn't exist.
    """
    if collection_name in bpy.data.collections:
        my_col = bpy.data.collections[collection_name]
    else:
        my_col = bpy.data.collections.new(collection_name)
    return my_col

def get_recursive_layer_collection(layer_collection: bpy.types.LayerCollection) -> List[bpy.types.LayerCollection]:
    """
    Get all recursive child collections of a layer collection.
    """
    all_childs: List[bpy.types.LayerCollection] = []
    for child in layer_collection.children:
        all_childs.append(child)
        all_childs += get_recursive_layer_collection(child)
    return all_childs

def set_collection_exclude(collection: bpy.types.Collection, exclude: bool):
    """
    Set the exclude property for a collection in all view layers.
    """
    scene = bpy.context.scene
    if scene is None:
        return

    if bpy.context:
        for vl in scene.view_layers:
            for layer in get_recursive_layer_collection(vl.layer_collection):
                if layer.collection == collection:
                    layer.exclude = exclude

def get_vertex_colors(obj: bpy.types.Object) -> List[bpy.types.MeshLoopColorLayer]:
    """
    Get the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes # type: ignore
    else:
        return obj.data.vertex_colors # type: ignore

def get_vertex_colors_render_color_index(obj: bpy.types.Object) -> Optional[int]:
    """
    Get the render color index of the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.render_color_index # type: ignore
    else:
        for index, vertex_color in enumerate(obj.data.vertex_colors):  # type: ignore
            if vertex_color.active_render:
                return index

def get_vertex_color_active_color_index(obj: bpy.types.Object) -> Optional[int]:
    """
    Get the active color index of the vertex colors of an object.
    """
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.active_color_index  # type: ignore
    else:
        return obj.data.vertex_colors.active_index  # type: ignore

def get_layer_collections_recursive(layer_collection: bpy.types.LayerCollection) -> List[bpy.types.LayerCollection]:
    """
    Get all recursive child layer collections of a layer collection.
    """
    layer_collections: List[bpy.types.LayerCollection] = []
    layer_collections.append(layer_collection)  # Add current
    for child_col in layer_collection.children:
        layer_collections.extend(get_layer_collections_recursive(child_col))  # Add child collections recursively

    return layer_collections


class SaveTransformObject():
    def __init__(self, obj: bpy.types.Object):
        self.init_object = obj
        self.transform_matrix = obj.matrix_world.copy()

    def reset_object_transform(self):
        self.init_object.matrix_world = self.transform_matrix

    def apply_object_transform(self, obj: bpy.types.Object):
        obj.matrix_world = self.transform_matrix

def make_override_library_object(obj: bpy.types.Object):
    select_specific_object(obj)
    bpy.ops.object.make_override_library() # type: ignore

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
    bpy.data.batch_remove(objects_to_remove)  # type: ignore
    bpy.data.batch_remove(data_to_remove)  # type: ignore

    # Recursively delete any child collections
    for sub_collection in collection.children:
        recursive_delete_collection(sub_collection)
    
    # Finally, delete the collection itself
    if collection.name in bpy.data.collections:
        bpy.data.collections.remove(collection)  # type: ignore

class SaveUserRenderSimplify():
    def __init__(self):
        scene = bpy.context.scene
        if scene is None:
            return

        # General
        self.use_simplify: bool = False

        # Viewport
        self.simplify_subdivision: int = 6
        self.simplify_child_particles: float = 1.0
        if bpy.app.version >= (2, 90, 0): # simplify_volumes was added in Blender 2.90
            self.simplify_volumes: float = 1.0
        if bpy.app.version >= (4, 1, 0): # use_simplify_normals was added in Blender 4.1
            self.use_simplify_normals: bool = False

        # Render
        self.simplify_subdivision_render: int = 6
        self.simplify_child_particles_render: float = 1.0

    def save_scene(self):
        """
        Save the current scene render simplify settings.
        """
        scene = bpy.context.scene
        if scene is None:
            return

        # General
        self.use_simplify = scene.render.use_simplify

        # Viewport
        self.simplify_subdivision = scene.render.simplify_subdivision
        self.simplify_child_particles = scene.render.simplify_child_particles
        if bpy.app.version >= (2, 90, 0):  # simplify_volumes was added in Blender 2.90
            self.simplify_volumes = scene.render.simplify_volumes
        if bpy.app.version >= (4, 1, 0):  # use_simplify_normals was added in Blender 4.1
            self.use_simplify_normals = scene.render.use_simplify_normals

        # Render
        self.simplify_subdivision_render = scene.render.simplify_subdivision_render
        self.simplify_child_particles_render = scene.render.simplify_child_particles_render

    def simplify_scene(self):
        """
        Simplifies the current scene render settings.
        """
        scene = bpy.context.scene
        if scene is None:
            return

        # General
        scene.render.use_simplify = True

        # Viewport
        scene.render.simplify_subdivision = 0
        scene.render.simplify_child_particles = 0
        if bpy.app.version >= (2, 90, 0):  # simplify_volumes was added in Blender 2.90
            scene.render.simplify_volumes = 0
        if bpy.app.version >= (4, 1, 0):  # use_simplify_normals was added in Blender 4.1
            scene.render.use_simplify_normals = False

        # Render
        scene.render.simplify_subdivision_render = 0
        scene.render.simplify_child_particles_render = 0

    def unsimplify_scene(self):
        """
        Resets the scene render settings to saved original values.
        """
        scene = bpy.context.scene
        if scene is None:
            return

        # General
        scene.render.use_simplify = False

    def reset_scene(self):
        """
        Resets the scene to the saved scene.
        """
        scene = bpy.context.scene
        if scene is None:
            return

        # General
        scene.render.use_simplify = self.use_simplify

        # Viewport
        scene.render.simplify_subdivision = self.simplify_subdivision
        scene.render.simplify_child_particles = self.simplify_child_particles
        if bpy.app.version >= (2, 90, 0):  # simplify_volumes was added in Blender 2.90
            scene.render.simplify_volumes = self.simplify_volumes
        if bpy.app.version >= (4, 1, 0):  # use_simplify_normals was added in Blender 4.1
            scene.render.use_simplify_normals = self.use_simplify_normals

        # Render
        scene.render.simplify_subdivision_render = self.simplify_subdivision_render
        scene.render.simplify_child_particles_render = self.simplify_child_particles_render

class SaveObjectReferanceUser():
    """
    This class is used to save and update references to an object in constraints 
    across all bones in all armatures within a Blender scene.
    """

    def __init__(self):
        """
        Initializes the instance with an empty list to store constraints using the specified object.
        """
        self.using_constraints: List[Dict[str, str]] = []

    def save_refs_from_object(self, targe_obj: bpy.types.Object):
        """
        Scans all objects in the Blender scene to find and save constraints in armature bones
        that reference the specified object.

        :param obj: The target bpy.types.Object to find references to.
        """
        
        scene = bpy.context.scene
        if scene is None:
            return

        for obj in scene.objects:
            if obj.type == 'ARMATURE':  # type: ignore
                if obj.pose:
                    for bone in obj.pose.bones:
                        for contrainte in bone.constraints:
                            if hasattr(contrainte, 'target') and contrainte.target and contrainte.target.name == targe_obj.name:  # type: ignore
                                constraint_info = {
                                    'armature_object': obj.name,
                                    'bone': bone.name,
                                    'constraint': contrainte.name
                                }
                                self.using_constraints.append(constraint_info)
    
    def update_refs_with_object(self, targe_obj: bpy.types.Object):
        """
        Updates all previously found constraints to reference a new object.

        :param obj: The new bpy.types.Object to be used as the target for the saved constraints.
        """
        
        scene = bpy.context.scene
        if scene is None:
            return

        for info in self.using_constraints:
            if info['armature_object'] in scene.objects:
                armature_object = scene.objects.get(info['armature_object'])
                if info['bone'] in armature_object.pose.bones:  # type: ignore
                    bone = armature_object.pose.bones[info['bone']]  # type: ignore
                    if info['constraint'] in bone.constraints:
                        constraint = bone.constraints[info['constraint']]
                        constraint.target = targe_obj  # type: ignore

def active_mode_is(target_mode: str):
    # Return True is active obj mode == target_mode

    obj = bpy.context.active_object
    if obj is not None:
        if obj.mode == target_mode:  # type: ignore
            return True
    return False

def active_type_is(target_type: str):
    # Return True is active obj type == target_type

    obj = bpy.context.active_object
    if obj is not None:
        if obj.type == target_type:  # type: ignore
            return True
    return False

def active_type_is_not(target_type: str):
    # Return True is active obj type != target_type

    obj = bpy.context.active_object
    if obj is not None:
        if obj.type != target_type:  # type: ignore
            return True
    return False

def found_type_in_selection(target_type: str, include_active: bool = True):
    # Return True if a specific type is found in current user selection

    select = bpy.context.selected_objects
    if not include_active:
        if bpy.context.active_object:
            if bpy.context.active_object in select:
                select.remove(bpy.context.active_object)

    for obj in select:
        if obj.type == target_type:  # type: ignore
            return True
    return False

def get_bones_from_armature(armature: bpy.types.Object) -> Union[bpy.types.EditBone, bpy.types.PoseBone, bpy.types.Bone]:
    """
    Returns the appropriate list of bones from an armature depending on its mode.
    - In EDIT mode: returns armature.data.edit_bones.
    - In POSE mode: returns armature.pose.bones.
    - Otherwise: returns pose bones or regular bones.
    """
    if armature.mode == 'EDIT':  # type: ignore
        return armature.data.edit_bones  # type: ignore
    elif armature.mode == 'POSE':  # type: ignore
        return armature.pose.bones  # type: ignore
    else:
        return armature.data.bones  # type: ignore

def get_bone_path(armature: bpy.types.Object, start_bone_name: str, end_bone_name: str) -> Optional[List[str]]:
    """
    Returns a list of bone names between start_bone and end_bone in an armature.
    
    :param armature: The armature object.
    :param start_bone_name: The name of the starting bone.
    :param end_bone_name: The name of the ending bone.
    :return: List of bone names between start_bone and end_bone, or an empty list if no path is found.
    """

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    # Initialize the bones
    if start_bone_name not in bones or end_bone_name not in bones:
        return []

    start_bone = bones[start_bone_name]
    end_bone = bones[end_bone_name]


    # Depth-First Search to find the path from start_bone to end_bone
    def find_path(current_bone: Union[bpy.types.EditBone, bpy.types.PoseBone, bpy.types.Bone], path: List[str]) -> Optional[List[str]]:
        path.append(current_bone.name)

        # Check if we've reached the end bone
        if current_bone == end_bone:
            return path

        # Explore each child recursively
        for child in current_bone.children:
            result = find_path(child, path[:])  # Use a copy of the current path
            if result:  # If a valid path is found, return it
                return result
        
        return None  # Return None if no path is found from this branch

    # Start the recursive search
    all_bones = find_path(start_bone, [])
    return all_bones
    
def get_bone_path_to_end(armature: bpy.types.Object, start_bone_name: str) -> List[str]:
    """
    Returns a list of bone names from the start_bone to the last child in a chain.
    
    :param armature: The armature object.
    :param start_bone_name: The name of the starting bone.
    :return: List of bone names from start_bone to the last child.
    """

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    # Initialize the bones
    start_bone = bones[start_bone_name]

    # Traverse bones from start_bone to the last child in the chain
    current_bone = start_bone
    bone_path = [current_bone.name]

    while current_bone.children:
        # Use first child only
        current_bone = current_bone.children[0]
        bone_path.append(current_bone.name)

    return bone_path

def get_bone_and_children(armature: bpy.types.Object, start_bone_name: str) -> List[str]:
    """
    Returns a list of all descendant bones of the specified start_bone, including all children recursively.
    
    :param armature: The armature object.
    :param start_bone_name: The name of the starting bone.
    :return: List of bone names, including the start bone and all its descendants.
    """

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    # Initialize the bones
    start_bone = bones[start_bone_name]
    

    # Recursive function to collect all children bones
    def collect_children(bone: Union[bpy.types.EditBone, bpy.types.PoseBone, bpy.types.Bone]) -> List[str]:
        bone_list = [bone.name]
        for child in bone.children:
            bone_list.extend(collect_children(child))
        return bone_list

    # Get all bones starting from the start_bone
    all_bones = collect_children(start_bone)
    return all_bones

def get_bones_name_contains(armature: bpy.types.Object, name_filter: str) -> List[str]:
    """
    Returns a list of bones whose names contain the specified substring.
    """
    if not name_filter:
        return []

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    return [bone.name for bone in bones if name_filter in bone.name]

def get_bones_name_starts_with(armature: bpy.types.Object, name_filter: str) -> List[str]:
    """
    Returns a list of bones whose names start with the specified string.
    """
    if not name_filter:
        return []

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    return [bone.name for bone in bones if bone.name.startswith(name_filter)]

def get_bones_name_ends_with(armature: bpy.types.Object, name_filter: str) -> List[str]:
    """
    Returns a list of bones whose names end with the specified string.
    """
    if not name_filter:
        return []

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    return [bone.name for bone in bones if bone.name.endswith(name_filter)]

def get_bones_name_contains_starts_with(armature: bpy.types.Object, contains_filter: str, startswith_filter: str) -> List[str]:
    """
    Match bones whose names contain one string and start with another.
    """
    if not contains_filter or not startswith_filter:
        return []

    # Access bones directly.
    bones = get_bones_from_armature(armature)
    
    return [
        b.name for b in bones
        if contains_filter in b.name and b.name.startswith(startswith_filter)
    ]

def get_bones_name_contains_ends_with(armature: bpy.types.Object, contains_filter: str, endswith_filter: str) -> List[str]:
    """
    Match bones whose names contain one string and end with another.
    """
    if not contains_filter or not endswith_filter:
        return []

    # Access bones directly.
    bones = get_bones_from_armature(armature)

    return [
        b.name for b in bones
        if contains_filter in b.name and b.name.endswith(endswith_filter)
    ]