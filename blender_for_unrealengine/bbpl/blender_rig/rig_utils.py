# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import mathutils
from typing import Optional, List, Union, Tuple
from .. import utils


def create_safe_bone(armature: bpy.types.Object, bone_name: str, collection_name: str = "") -> Optional[bpy.types.EditBone]:
    """
    Create a bone in the armature.
    Blender 4.0 -> context_id is the bone collection name.
    Blender 3.6 and older -> context_id is the bone layer index.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        return None

    if bone_name in armature.data.edit_bones:
        print("Bone already exists! : " + bone_name)
        raise TypeError("Bone already exists! : " + bone_name)

    name_length = len(bone_name)
    if name_length > 63:
        print("Name length is bigger than Blender character limit! ("+str(name_length)+"/63) : " + bone_name)
        raise TypeError("Name length is bigger than Blender character limit! ("+str(name_length)+"/63) : " + bone_name)

    bone = armature.data.edit_bones.new(bone_name)
    bone.tail = bone.head + mathutils.Vector((0, 0, 1))

    if collection_name:
        if bpy.app.version >= (4, 0, 0):
            add_bone_to_collection(armature, bone_name, collection_name)
        else:
            layer_index = int(collection_name)
            change_current_layer(0, bpy.context.object.data)  # type: ignore
            change_current_layer(layer_index, bone)

    return bone

def get_mirror_bone_name(original_bones: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Returns the mirror name of a bone or a list of bones.
    Automatically handles .l/.r, .L/.R, _l/_r, _L/_R, _left/_right, Left/Right, etc.
    """
    bones: List[str] = [original_bones] if isinstance(original_bones, str) else original_bones

    def mirror_name(bone: str) -> str:
        bases = [("l", "r"), ("left", "right")]
        seps = [".", "_", ""]
        patterns: List[Tuple[str, str]] = []
        for sep in seps:
            for l, r in bases:
                for lcase, rcase in [
                    (l.lower(), r.lower()),
                    (l.upper(), r.upper()),
                    (l.capitalize(), r.capitalize()),
                ]:
                    patterns.append((sep + lcase, sep + rcase))
        patterns.sort(key=lambda x: len(x[0]), reverse=True)
        for lpat, rpat in patterns:
            if bone.endswith(lpat):
                if len(lpat) == 1 and lpat in "lr" and len(bone) > 1 and bone[-2].isalnum():
                    continue
                return bone[:-len(lpat)] + rpat
            if bone.endswith(rpat):
                if len(rpat) == 1 and rpat in "lr" and len(bone) > 1 and bone[-2].isalnum():
                    continue
                return bone[:-len(rpat)] + lpat
            if lpat.startswith(("Left", "RIGHT", "LEFT", "Right")):
                if bone.startswith(lpat):
                    return rpat + bone[len(lpat):]
                if bone.startswith(rpat):
                    return lpat + bone[len(rpat):]
        return bone

    mirrored = [mirror_name(b) for b in bones]
    return mirrored[0] if isinstance(original_bones, str) else mirrored

def get_name_with_new_prefix(name: str, old_prefix: str, new_prefix: str) -> str:
    """
    Replace a prefix and add a new prefix to a name.
    """

    new_bone_name = name
    if new_bone_name.startswith(old_prefix):
        new_bone_name = new_bone_name[len(old_prefix):]
        new_bone_name = new_prefix + new_bone_name
    else:
        raise TypeError('"' + old_prefix + '" not found as prefix in "' + name + '".')
    return new_bone_name

def get_name_list_with_new_prefix(name_list: List[str], old_prefix: str, new_prefix: str) -> List[str]:
    """
    Replace a prefix and add a new prefix to each name in a list.
    """

    new_list: List[str] = []
    for name in name_list:
        new_list.append(get_name_with_new_prefix(name, old_prefix, new_prefix))
    return new_list

def no_num(name: str) -> str:
    """
    Remove the number index from a bone name.
    """
    suffix = name[-4:]
    if suffix == ".000" or suffix == ".001" or suffix == ".002" or suffix == ".003":
        return name[:-4]
    return name

if bpy.app.version >= (4, 0, 0):
    def add_bone_to_collection(armature: bpy.types.Object, bone_name: str, collection_name: str) -> bpy.types.BoneCollection:
        #Add bone to collection and create if not exist

        if not isinstance(armature.data, bpy.types.Armature):
            raise TypeError("The provided object is not an armature.")

        if bpy.app.version >= (4, 1, 0):
            # Need to use collections_all for include all collections childs.
            if collection_name in armature.data.collections_all:
                col = armature.data.collections_all[collection_name]
            else:
                col = armature.data.collections.new(name=collection_name)
        else:
            if collection_name in armature.data.collections:
                col = armature.data.collections[collection_name]
            else:
                col = armature.data.collections.new(name=collection_name)


        bone = armature.data.edit_bones[bone_name]
        col.assign(bone)
        return col

    def remove_bone_from_collection(armature: bpy.types.Object, bone_name: str, collection_name: str) -> Optional[bpy.types.BoneCollection]:
        if not isinstance(armature.data, bpy.types.Armature):
            raise TypeError("The provided object is not an armature.")

        #Remove bone from collection.
        if bpy.app.version >= (4, 1, 0):
            # Need to use collections_all for include all collections childs.
            if collection_name in armature.data.collections_all:
                col = armature.data.collections_all[collection_name]
                bone = armature.data.edit_bones[bone_name]
                col.unassign(bone)
                return col
        else:
            if collection_name in armature.data.collections:
                col = armature.data.collections[collection_name]
                bone = armature.data.edit_bones[bone_name]
                col.unassign(bone)
                return col

if bpy.app.version <= (3, 6, 0):

    def change_current_layer(layer: int, source: bpy.types.Armature):
        """
        Change the current active layer to the specified layer.
        Deprecated in new version of Blender.
        """
        source.layers[layer] = True
        for i in range(0, 32):
            if i != layer:
                source.layers[i] = False

    def change_select_layer(layer):
        """
        Change the active bone layer in the armature to the specified layer.
        Deprecated in new version of Blender.
        """
        layer_values = [layer == i for i in range(32)]
        bpy.ops.armature.bone_layers(layers=layer_values)  # type: ignore

    def change_user_view_layer(layer):
        """
        Change the active layer in the user view to the specified layer.
        Deprecated in new version of Blender.
        """
        change_current_layer(layer, bpy.context.object.data)  # type: ignore

    def duplicate_rig_layer(armature: bpy.types.Object, original_layer: int, new_layer: int, old_prefix: str, new_prefix: str) -> List[str]:
        """
        Deprecated in new version of Blender.
        Duplicates the bones in the specified original layer of the armature and moves them to the new layer.
        The bone names are modified by replacing the old prefix with the new prefix.

        Args:
            armature (bpy.types.Object): The armature object.
            original_layer (int): The original layer index.
            new_layer (int): The new layer index.
            old_prefix (str): The old prefix to replace in bone names.
            new_prefix (str): The new prefix to use in bone names.

        Returns:
            list: A list of the names of the duplicated bones.
        """

        if not isinstance(armature.data, bpy.types.Armature):
            raise TypeError("The provided object is not an armature.")

        utils.safe_mode_set(armature, "EDIT")  # Set the armature to edit mode safely  # type: ignore
        # Change the current active layer to the original layer
        change_current_layer(original_layer, bpy.context.object.data)  # type: ignore
        bpy.ops.armature.select_all(action='SELECT')  # Select all bones
        bpy.ops.armature.duplicate()  # Duplicate the selected bones
        change_select_layer(new_layer)  # Move the duplicated bones to the new layer
        change_user_view_layer(new_layer)  # Set the user view to the new layer

        new_bone_names: List[str] = []
        for bone in bpy.context.selected_bones:  # type: ignore
            new_bone_names .append(bone.name)

        armature.data.pose_position = 'REST'  # Set the pose position to rest
        utils.safe_mode_set(armature, "OBJECT")  # Set the armature to object mode safely  # type: ignore
        for bone_name in new_bone_names:
            new_bone_name = get_name_with_new_prefix(bone_name, old_prefix, new_prefix)  # Modify the bone name
            new_bone_name = no_num(new_bone_name)  # Remove the number index from the bone name
            armature.data.bones[bone_name].name = new_bone_name  # Rename the bone

        armature.data.pose_position = 'POSE'  # Set the pose position back to pose mode
        return new_bone_names


class Orig_prefixhanBone():
    """
    Create a new Orig_prefixhanBone instance.
    """

    def __init__(self, armature: bpy.types.Object, child_bone: bpy.types.Bone):
        if not isinstance(armature.data, bpy.types.Armature):
            raise TypeError("The provided object is not an armature.")
        
        self.armature = armature
        self.name = child_bone.name
        if child_bone.parent:
            self.old_parent_name = child_bone.parent.name
        else:
            self.old_parent_name = ""
        self.new_parent_name = ""

    def apply_new_parent(self):
        """
        Apply the new parent bone to the child bone.
        """
        if not isinstance(self.armature.data, bpy.types.Armature):
            raise TypeError("The provided object is not an armature.")

        if self.new_parent_name != "":
            for bone in self.armature.data.edit_bones:
                if bone.name == self.name:
                    bone.parent = self.armature.data.edit_bones[self.new_parent_name]
                    # print(bone.name, " child for ", self.new_parent_name)  # Debug
        else:
            print("Error: new_parent not set in Orig_prefixhanBone for " + self.name)


def set_bone_orientation(armature: bpy.types.Object, bone_name: str, vector: mathutils.Vector, roll: float):
    """
    Sets the orientation of a bone in the armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    bone = armature.data.edit_bones[bone_name]
    length = bone.length
    bone.tail = bone.head + vector * length
    bone.roll = roll

def get_bone_with_length(armature: bpy.types.Object, bone_name: str, new_length: float, apply_tail: bool = True) -> mathutils.Vector:
    """
    Evaluate the edit_bone tail position with specific length
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head
    vector.normalize()

    new_tail = bone.head + (vector * new_length)
    return new_tail

def set_bone_length(armature: bpy.types.Object, bone_name: str, new_length: float) -> mathutils.Vector:
    """
    Sets the length of a bone in the armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head
    vector.normalize()

    new_tail = bone.head + (vector * new_length)

    bone.tail = new_tail
    return new_tail

def get_bone_vector(armature: bpy.types.Object, bone_name: str) -> mathutils.Vector:
    """
    Retrieves the vector (direction) of a bone in the armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    head = armature.data.edit_bones[bone_name].head
    tail = armature.data.edit_bones[bone_name].tail
    return head - tail

def set_bone_scale(armature: bpy.types.Object, bone_name: str, new_scale: float, apply_tail: bool = True) -> mathutils.Vector:
    """
    Sets the scale of a bone in the armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head

    new_tail = bone.head + (vector * new_scale)
    if apply_tail:
        bone.tail = new_tail
    return new_tail


class BoneDataSave:
    """
    Defines the orientation mode of the bone in the armature.
    """
    def __init__(self, armature: bpy.types.Object, saved_bone: bpy.types.Bone):
        self.name = saved_bone.name
        self.parent = saved_bone.parent.name
        self.childs = [bone for bone in armature if bone.parent == saved_bone]


def get_first_parent(bone: bpy.types.Bone) -> bpy.types.Bone:
    """
    Recursively retrieves the first parent bone of the given bone.
    """
    if bone.parent:
        return get_first_parent(bone.parent)
    else:
        return bone

def create_simple_stretch(armature: bpy.types.Object, bone: str, target_bone_name: str, name: str):
    """
    Create a simple stretch constraint for a bone in an armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    bpy.ops.object.mode_set(mode='POSE')
    if armature.pose is None:
        raise TypeError("The armature has no pose data.")

    constraint: bpy.types.Constraint = armature.pose.bones[bone].constraints.new('STRETCH_TO')
    if isinstance(constraint, bpy.types.StretchToConstraint):
        constraint.target = armature
        constraint.subtarget = target_bone_name
        constraint.name = name
        bpy.ops.object.mode_set(mode='EDIT')
        constraint.rest_length = (
            armature.data.edit_bones[target_bone_name].head - armature.data.edit_bones[bone].tail
        ).length


class DriverPropertyHelper:
    """
    Helper class for applying drivers to custom properties in Blender.
    """

    def __init__(self, armature: bpy.types.Object, bone_const_name: str, constraint_name: str, name: str ="NoPropertyName"):

        self.armature = armature
        self.bone_const_name = bone_const_name
        self.constraint_name = constraint_name
        self.description = ""
        self.property_name = name
        self.default = 0.0
        self.min = 0.0
        self.max = 1.0

    def apply_driver(self, bone_name: str):
        """
        Applies a driver to the custom property.

        Args:
            bone_name (str): The name of the bone to which the driver is applied.
            constraint (bpy.types.Constraint): The constraint object to which the driver is applied.
        """
        if not (self.bone_const_name or self.constraint_name):
            print("bone_const_name or constraint_name not set!")
            return

        create_bone_custom_property(
            armature=self.armature,
            property_bone_name=bone_name,
            property_name=self.property_name,
            default=self.default,
            value_min=self.min,
            value_max=self.max,
            description=self.description,
            overridable=True)

        escaped_bone_const = bpy.utils.escape_identifier(self.bone_const_name)
        escaped_constraints = bpy.utils.escape_identifier(self.constraint_name)
        driver_value = f'pose.bones["{escaped_bone_const}"].constraints["{escaped_constraints}"].influence'
        driver = self.armature.driver_add(driver_value).driver
        set_driver(self.armature, driver, bone_name, self.property_name)


def create_bone_custom_property(armature: bpy.types.Object, property_bone_name: str, property_name: str, default: float = 0.0, value_min: float = 0.0, value_max: float = 1.0, description: str = '..', overridable: bool = True):
    """
    Creates a custom property for the specified bone in the armature.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")
    if armature.pose is None:
        raise TypeError("The armature has no pose data.")

    property_bone = armature.pose.bones[property_bone_name]
    property_bone[property_name] = default
    ui_data = property_bone.id_properties_ui(property_name)
    ui_data.update(
        default=default,
        min=value_min,
        max=value_max,
        soft_min=value_min,
        soft_max=value_max,
        description=description
    )
    escaped_property_name = bpy.utils.escape_identifier(property_name)
    escaped_property_bone_name = bpy.utils.escape_identifier(property_bone_name)
    property_bone.property_overridable_library_set(f'["{escaped_property_name}"]', overridable)
    data_path = f'pose.bones["{escaped_property_bone_name}"]["{escaped_property_name}"]'
    return data_path

def set_driver(armature: bpy.types.Object, driver: bpy.types.Driver, bone_name: str, driver_name: str, clean_previous: bool = True):
    """
    Sets up a driver for the specified bone and property in the armature.
    """
    if clean_previous:
        utils.clear_driver_var(driver)

    # Escape bone and driver names for safe use in data_path
    escaped_bone_name = bpy.utils.escape_identifier(bone_name)
    escaped_driver_name = bpy.utils.escape_identifier(driver_name)

    v = driver.variables.new()
    v.name = driver_name.replace(" ", "_")
    v.targets[0].id = armature
    v.targets[0].data_path = f'pose.bones["{escaped_bone_name}"]["{escaped_driver_name}"]'
    driver.expression = v.name
    return v

def subdivise_one_bone(armature: bpy.types.Object, bone_name: str, subdivise_prefix_name: str ="Subdivise_", split_number: int =2, keep_parent: bool = True) -> List[str]:
    """
    Subdivides a bone into multiple segments.

    Args:
        armature (bpy.types.Object): The armature object.
        edit_bone (bpy.types.EditBone): The bone to subdivide.
        split_number (int, optional): The number of segments to create. Defaults to 2.
        keep_parent (bool, optional): Indicates whether to keep the original bone as the parent. Defaults to True.

    Returns:
        list: A list of the created bones.
    """

    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    # Vars
    edit_bone: bpy.types.EditBone = armature.data.edit_bones[bone_name]
    original_tail = edit_bone.tail + mathutils.Vector((0, 0, 0))

    # Duplication
    chain = [bone_name]
    for x in range(1, split_number):
        dup_bone_name = duplicate_bone(armature, edit_bone.name, subdivise_prefix_name + str(x).zfill(2) + "_" + edit_bone.name)
        chain.append(dup_bone_name)

    if not keep_parent:
        # Reparenting children bones to the tail of the chain
        for bone in armature.data.edit_bones:
            if bone.parent == edit_bone:
                bone.parent = armature.data.edit_bones[chain[-1]]

    # Replacing bones
    bone_root_pos = edit_bone.head
    vector_length = edit_bone.tail - edit_bone.head
    for x, bone_name in enumerate(chain):
        bone = armature.data.edit_bones[bone_name]
        if keep_parent:
            # bone.use_connect = False
            bone.head = bone_root_pos + (vector_length / split_number) * x
            bone.tail = bone_root_pos + (vector_length / split_number) * (x + 1)
            # bone.head = mathutils.Vector((0,0,0))
            bone.tail = original_tail
        else:
            bone.head = bone_root_pos + (vector_length / split_number) * x
            bone.tail = bone_root_pos + (vector_length / split_number) * (x + 1)

        if x > 0:
            bone.parent = armature.data.edit_bones[chain[x - 1]]
            if not keep_parent:
                bone.use_connect = True

    # Final reparenting
    return chain

def duplicate_bone(armature: bpy.types.Object, bone_name: str, new_name: Optional[str] = None):
    """
    Creates a duplicate bone in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        bone_name (str): The name of the bone to duplicate.
        new_name (str, optional): The name of the new bone. If None, a default name will be generated.

    Returns:
        str: The name of the created bone.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")

    edit_bone: bpy.types.EditBone = armature.data.edit_bones[bone_name]
    if new_name is None:
        new_name = edit_bone.name + "_dup"
    new_bone = armature.data.edit_bones.new(new_name)
    new_bone.head = edit_bone.head
    new_bone.tail = edit_bone.tail
    new_bone.roll = edit_bone.roll
    new_bone.inherit_scale = edit_bone.inherit_scale

    new_bone.parent = edit_bone.parent
    if bpy.app.version >= (4, 1, 0):
        for bone_col in edit_bone.collections:
            col = armature.data.collections_all[bone_col.name]
            col.assign(new_bone)
    elif bpy.app.version >= (4, 0, 0):
        for bone_col in edit_bone.collections:
            col = armature.data.collections[bone_col.name]
            col.assign(new_bone)
    else:
        new_bone.layers = edit_bone.layers # Deprecated in Blender 4.0

    return new_bone.name

def copy_constraint(armature: bpy.types.Object, copy_bone_name: str, paste_bone_name: str, clear: bool = True):
    """
    Copies constraints from one bone to another in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        copy_bone_name (str): The name of the bone from which to copy the constraints.
        paste_bone_name (str): The name of the bone to which the constraints are copied.
        clear (bool, optional): Indicates whether to clear existing constraints in the destination bone. Defaults to True.
    """
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("The provided object is not an armature.")
    
    if armature.pose is None:
        raise TypeError("The armature has no pose data.")

    copy_bone = armature.pose.bones[copy_bone_name]
    paste_bone = armature.pose.bones[paste_bone_name]

    if clear:
        for c in paste_bone.constraints:
            paste_bone.constraints.remove(c)

    for c in copy_bone.constraints:
        p = paste_bone.constraints.new(c.type)
        p.name = c.name
        p.target = c.target
        p.subtarget = c.subtarget
        # paste_bone.constraints[a.name] = c

    # armature.pose.bones[paste_bone].constraints = armature.pose.bones[copy_bone].constraints

def set_bones_lock(armature: bpy.types.Object, bone_names: List[str], lock: bool):
    for bone_name in bone_names:
        set_bone_lock(armature, bone_name, lock)

def set_bone_lock(armature: bpy.types.Object, bone_name: str, lock: bool):
    # Check if we are in Pose mode
    if not isinstance(armature.data, bpy.types.Armature):
        raise TypeError("Error: The provided object is not an armature.")

    if armature.pose is None:
        raise TypeError("Error: The armature has no pose data.")
    
    # Check if the bone exists in the armature
    if bone_name not in armature.pose.bones:
        raise TypeError(f"Error: Bone '{bone_name}' does not exist in the armature.")

    pose_bone = armature.pose.bones[bone_name]

    pose_bone.lock_rotation_w = lock
    pose_bone.lock_rotation[0] = lock
    pose_bone.lock_rotation[1] = lock
    pose_bone.lock_rotation[2] = lock
    pose_bone.lock_location[0] = lock
    pose_bone.lock_location[1] = lock
    pose_bone.lock_location[2] = lock
    pose_bone.lock_scale[0] = lock
    pose_bone.lock_scale[1] = lock
    pose_bone.lock_scale[2] = lock