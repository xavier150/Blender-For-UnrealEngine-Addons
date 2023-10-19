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

import bpy
import mathutils
from . import utils


def create_safe_bone(armature, bone_name, layer=None):
    """
    Create a bone in the armature.
    """
    #if bone_name == "rp_c_Eye_L":
    #    k=k

    if bone_name in armature.data.edit_bones:
        print("Bone already exists! : " + bone_name)
        raise TypeError("Bone already exists! : " + bone_name)

    bone = armature.data.edit_bones.new(bone_name)
    bone.tail = bone.head + mathutils.Vector((0, 0, 1))

    if layer:
        change_current_layer(0, bpy.context.object.data)
        change_current_layer(layer, bone)

    return bone


def get_mirror_bone_name(original_bones):
    """
    Get the mirror bone name for the given bone(s).
    """
    bones = []
    new_bones = []

    if not isinstance(original_bones, list):
        bones = [original_bones]  # Convert to list
    else:
        bones = original_bones

    def try_to_invert_bones(bone):
        def invert(bone, old, new):
            if bone.endswith(old):
                new_bone_name = bone[:-len(old)]
                new_bone_name = new_bone_name + new
                return new_bone_name
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

    for bone in bones:
        new_bones.append(try_to_invert_bones(bone))

    # Can return same bone when don't found mirror
    if not isinstance(original_bones, list):
        return new_bones[0]
    else:
        return new_bones


def get_name_with_new_prefix(name, old_prefix, new_prefix):
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


def get_name_list_with_new_prefix(name_list, old_prefix, new_prefix):
    """
    Replace a prefix and add a new prefix to each name in a list.
    """

    new_list = []
    for name in name_list:
        new_list.append(get_name_with_new_prefix(name, old_prefix, new_prefix))
    return new_list


def no_num(name):
    """
    Remove the number index from a bone name.
    """
    suffix = name[-4:]
    if suffix == ".000" or suffix == ".001" or suffix == ".002" or suffix == ".003":
        return name[:-4]
    return name


def change_current_layer(layer, source):
    """
    Change the current active layer to the specified layer.
    """
    source.layers[layer] = True
    for i in range(0, 32):
        if i != layer:
            source.layers[i] = False


def change_select_layer(layer):
    """
    Change the active bone layer in the armature to the specified layer.
    """
    layer_values = [layer == i for i in range(32)]
    bpy.ops.armature.bone_layers(layers=layer_values)


def change_user_view_layer(layer):
    """
    Change the active layer in the user view to the specified layer.
    """
    change_current_layer(layer, bpy.context.object.data)


def duplicate_rig_layer(armature, original_layer, new_layer, old_prefix, new_prefix):
    """
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

    utils.safe_mode_set(armature, "EDIT")  # Set the armature to edit mode safely
    # Change the current active layer to the original layer
    change_current_layer(original_layer, bpy.context.object.data)
    bpy.ops.armature.select_all(action='SELECT')  # Select all bones
    bpy.ops.armature.duplicate()  # Duplicate the selected bones
    change_select_layer(new_layer)  # Move the duplicated bones to the new layer
    change_user_view_layer(new_layer)  # Set the user view to the new layer

    new_bone_names  = []
    for bone in bpy.context.selected_bones:
        new_bone_names .append(bone.name)

    armature.data.pose_position = 'REST'  # Set the pose position to rest
    utils.safe_mode_set(armature, "OBJECT")  # Set the armature to object mode safely
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

    def __init__(self, armature, child_bone):
        self.armature = armature
        self.name = child_bone.name
        self.old_parent_name = child_bone.parent.name
        self.new_parent_name = ""

    def apply_new_parent(self):
        """
        Apply the new parent bone to the child bone.
        """
        if self.new_parent_name != "":
            for bone in self.armature.data.edit_bones:
                if bone.name == self.name:
                    bone.parent = self.armature.data.edit_bones[self.new_parent_name]
                    # print(bone.name, " child for ", self.new_parent_name)  # Debug
        else:
            print("Error: new_parent not set in Orig_prefixhanBone for " + self.name)


def set_bone_orientation(armature, bone_name, vector, roll):
    """
    Définit l'orientation d'un os dans l'armature.
    """
    bone = armature.data.edit_bones[bone_name]
    length = bone.length
    bone.tail = bone.head + vector * length
    bone.roll = roll


def set_bone_length(armature, bone_name, new_length, apply_tail=True):
    """
    Définit la longueur d'un os dans l'armature.
    """
    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head
    vector.normalize()

    new_tail = bone.head + (vector * new_length)
    if apply_tail:
        bone.tail = new_tail
    return new_tail


def get_bone_vector(armature, bone_name):
    """
    Récupère le vecteur (direction) d'un os dans l'armature.
    """
    head = armature.data.edit_bones[bone_name].head
    tail = armature.data.edit_bones[bone_name].tail
    return head - tail


def set_bone_scale(armature, bone_name, new_scale, apply_tail=True):
    """
    Définit l'échelle d'un os dans l'armature.
    """
    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head

    new_tail = bone.head + (vector * new_scale)
    if apply_tail:
        bone.tail = new_tail
    return new_tail

'''
def create_head_control_point(armature, bone_name, add_controller=False, prefix="TailControlPoint_"):
    """
    Crée un point de contrôle de la tête d'un os dans l'armature.
    """
    #TO DO: Move this to Modular Auto Rig Addon
    rig_prefix = armature.mar_rig_prefix
    rig_joint_prefix = armature.mar_rig_joint_prefix

    bone = armature.data.edit_bones[bone_name]
    rig_prefix_bone = armature.data.edit_bones[rig_prefix + bone_name]

    # Créer l'os RP pour le parent et l'enfant
    rig_prefix_point_bone_name = rig_joint_prefix + "HeadControlPoint_" + bone_name
    rig_prefix_point_bone = create_safe_bone(armature, rig_prefix_point_bone_name, layer=armature.mar_rig_joint_layer)
    rig_prefix_point_bone.parent = rig_prefix_bone

    # Définir leur position
    bone_length = 0.02 * armature.mar_rig_bone_scale
    target_head = bone.head
    target_tail = set_bone_length(armature, bone_name, bone_length, apply_tail=False)
    target_roll = bone.roll

    rig_prefix_point_bone.head = target_head
    rig_prefix_point_bone.tail = target_tail
    rig_prefix_point_bone.roll = target_roll

    if add_controller:
        controller_bone_name = rig_prefix + prefix + bone_name
        controller_bone = create_safe_bone(armature, controller_bone_name, layer=get_layer_by_name(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rig_prefix_point_bone
        return controller_bone_name


def create_tail_control_point(armature, bone_name, add_controller=False, prefix="TailControlPoint_"):
    """
    Crée un point de contrôle de la queue d'un os dans l'armature.
    """
    #TO DO: Move this to Modular Auto Rig Addon
    rig_prefix = armature.mar_rig_prefix
    rig_joint_prefix = armature.mar_rig_joint_prefix

    bone = armature.data.edit_bones[bone_name]
    rig_prefix_bone = armature.data.edit_bones[rig_prefix + bone_name]

    # Créer l'os RP pour le parent et l'enfant
    rig_prefix_point_bone_name = rig_joint_prefix + "TailControlPoint_" + bone_name
    rig_prefix_point_bone = create_safe_bone(armature, rig_prefix_point_bone_name, layer=armature.mar_rig_joint_layer)
    rig_prefix_point_bone.parent = rig_prefix_bone

    # Définir leur position
    bone_length = 0.02 * armature.mar_rig_bone_scale
    target_head = bone.tail
    target_tail = set_bone_length(armature, bone_name, bone_length, apply_tail=False) - bone.head + bone.tail
    target_roll = bone.roll

    rig_prefix_point_bone.head = target_head
    rig_prefix_point_bone.tail = target_tail
    rig_prefix_point_bone.roll = target_roll

    if add_controller:
        controller_bone_name = rig_prefix + prefix + bone_name
        controller_bone = create_safe_bone(armature, controller_bone_name, layer=get_layer_by_name(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rig_prefix_point_bone
        return controller_bone_name


def create_bone_interpolation(
        armature, 
        parent_bone_name, 
        child_bone_name, 
        position_mode="PARENT",
        desired_head=None, 
        desired_tail=None, 
        desired_roll=None,
        add_controller=False, 
        mode="ROTATION",
        stretch_by_difference=False, 
        stretch_axis=0, 
        prefix="interp_"
        ):
    

    """
    Crée une interpolation entre deux os dans l'armature.
    """
    #TO DO: Move this to Modular Auto Rig Addon
    #TO DO: Move this to Modular Auto Rig Addon
    #TO DO: Move this to Modular Auto Rig Addon
    rig_prefix = armature.mar_rig_prefix
    rig_joint_prefix = armature.mar_rig_joint_prefix

    parent_bone = armature.data.edit_bones[rig_prefix + parent_bone_name]
    child_bone = armature.data.edit_bones[rig_prefix + child_bone_name]

    # Créer deux os RP pour le parent et l'enfant
    rig_prefix_parent_bone_name = rig_joint_prefix + "interp_prefixParent_" + parent_bone_name
    rig_prefix_parent_bone = create_safe_bone(armature, rig_prefix_parent_bone_name, layer=armature.mar_rig_joint_layer)
    rig_prefix_parent_bone.parent = parent_bone

    rig_prefix_child_bone_name = rig_joint_prefix + "interp_prefixChild_" + parent_bone_name
    rig_prefix_child_bone = create_safe_bone(armature, rig_prefix_child_bone_name, layer=armature.mar_rig_joint_layer)
    rig_prefix_child_bone.parent = child_bone

    # Définir leur position
    bone_length = 0.02 * armature.mar_rig_bone_scale

    if position_mode == "PARENT":
        target_head = child_bone.head
        target_tail = set_bone_length(armature, rig_prefix + parent_bone_name, bone_length, apply_tail=False) - parent_bone.head + child_bone.head
        target_roll = parent_bone.roll

    elif position_mode == "CHILD":
        target_head = child_bone.head
        target_tail = set_bone_length(armature, rig_prefix + child_bone_name, bone_length, apply_tail=False)
        target_roll = child_bone.roll

    elif position_mode == "MIX":
        target_head = child_bone.head
        vector_parent = (parent_bone.tail - parent_bone.head)
        vector_child = (child_bone.tail - child_bone.head)
        vector_parent.normalize()
        vector_child.normalize()
        vector_target = ((vector_parent + vector_child) / 2) * bone_length
        target_tail = child_bone.head + vector_target
        target_roll = (child_bone.roll + child_bone.roll) / 2

    elif position_mode == "UP":
        target_head = child_bone.head
        target_tail = target_head + mathutils.Vector((0, 0, bone_length))
        target_roll = 0

    else:
        raise TypeError('Position mode not found! ' + position_mode)

    if desired_head:
        target_head = desired_head

    if desired_tail:
        target_tail = desired_tail

    if desired_roll:
        target_roll = desired_roll

    rig_prefix_parent_bone.head = target_head
    rig_prefix_parent_bone.tail = target_tail
    rig_prefix_parent_bone.roll = target_roll

    rig_prefix_child_bone.head = target_head
    rig_prefix_child_bone.tail = target_tail
    rig_prefix_child_bone.roll = target_roll

    if stretch_by_difference:
        rig_prefix_parent_stretch_bone = armature.data.edit_bones[duplicate_bone(armature, rig_prefix_parent_bone_name)]
        rig_prefix_parent_stretch_bone_name = rig_prefix_parent_stretch_bone.name
        rig_prefix_child_stretch_bone = armature.data.edit_bones[duplicate_bone(armature, rig_prefix_child_bone_name)]
        rig_prefix_child_stretch_bone_name = rig_prefix_child_stretch_bone.name

    # Créer un troisième os qui effectue l'interpolation entre les deux premiers
    rig_prefix_interp_bone_name = rig_joint_prefix + "interp_" + parent_bone_name
    rig_prefix_interp_bone = create_safe_bone(armature, rig_prefix_interp_bone_name, layer=armature.mar_rig_joint_layer)

    rig_prefix_interp_bone.head = target_head
    rig_prefix_interp_bone.tail = target_tail
    rig_prefix_interp_bone.roll = target_roll
    if stretch_by_difference:
        rig_prefix_interp_bone.parent = rig_prefix_parent_stretch_bone
    else:
        rig_prefix_interp_bone.parent = rig_prefix_parent_bone

    if add_controller:
        controller_bone_name = rig_prefix + prefix + parent_bone_name
        controller_bone = create_safe_bone(armature, controller_bone_name, layer=get_layer_by_name(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rig_prefix_interp_bone

    bpy.ops.object.mode_set(mode='POSE')
    if mode == "ROTATION":
        cons_name = "COPY_ROTATION"
    elif mode == "LOCATION":
        cons_name = "COPY_LOCATION"
    elif mode == "TRANSFORM":
        cons_name = "COPY_TRANSFORMS"
    else:
        raise TypeError("Error in create_bone_interpolation() cons_name " + cons_name + " not valid.")


    constraint = armature.pose.bones[rig_prefix_interp_bone_name].constraints.new(cons_name)
    constraint.target = armature
    if stretch_by_difference:
        constraint.subtarget = rig_prefix_child_stretch_bone_name
    else:
        constraint.subtarget = rig_prefix_child_bone_name
    constraint.name = "interpolation follow rotation"
    constraint.influence = 0.5

    if stretch_by_difference:
        # Créer un driver pour modifier l'échelle en fonction de l'interp_prefix
        def create_stretch_driver(bone_name, value="min_x", axis_index=0):
            driver_stretch_name = 'pose.bones["' + bone_name + '"].scale'

            driver_stretch = armature.driver_add(driver_stretch_name, axis_index).driver
            utils.clear_driver_var(driver_stretch)
            value = driver_stretch.variables.new()
            value.name = "interp_stretch_by_difference"
            value.type = 'ROTATION_DIFF'
            value.targets[0].id = armature
            value.targets[1].id = armature
            value.targets[0].bone_target = rig_prefix_parent_bone_name
            value.targets[1].bone_target = rig_prefix_child_bone_name
            driver_stretch.expression = "1+"+value.name
            return driver_stretch

        stretch_drivers = []
        stretch_drivers.append(create_stretch_driver(rig_prefix_parent_stretch_bone_name, "min_z", stretch_axis))
        stretch_drivers.append(create_stretch_driver(rig_prefix_child_stretch_bone_name, "max_z", stretch_axis))

    if add_controller:
        # Gestion des drivers
        my_property = DriverPropertyHelper(armature, rig_prefix_interp_bone_name, constraint.name, name="Follow_Child")
        my_property.default = 0.5
        my_property.description = "Follow child factor."
        my_property.apply_driver(controller_bone_name)

    bpy.ops.object.mode_set(mode='EDIT')

    class interp_prefixBone():
        def __init__(self):
            self.parent = rig_prefix_parent_bone_name
            self.child = rig_prefix_child_bone_name
            self.interp_prefix = rig_prefix_interp_bone_name

            if stretch_by_difference:
                self.parent_stretch = rig_prefix_parent_stretch_bone_name
                self.child_stretch = rig_prefix_child_stretch_bone_name
                self.stretch_drivers = stretch_drivers
            else:
                self.parent_stretch = None
                self.child_stretch = None
                self.stretch_drivers = None
            if add_controller:
                self.controller = controller_bone_name

    interp_prefix = interp_prefixBone()
    return interp_prefix



'''

class BoneDataSave:
    """
    Définit le mode d'orientation de l'os dans l'armature.
    """
    def __init__(self, armature, saved_bone):
        self.name = saved_bone.name
        self.parent = saved_bone.parent.name
        self.childs = [bone for bone in armature if bone.parent == saved_bone]

'''

'''


def get_first_parent(bone):
    """
    Recursively retrieves the first parent bone of the given bone.
    """
    if bone.parent:
        return get_first_parent(bone.parent)
    else:
        return bone


def create_simple_stretch(armature, bone, target_bone_name, name):
    """
    Create a simple stretch constraint for a bone in an armature.
    """
    bpy.ops.object.mode_set(mode='POSE')
    constraint = armature.pose.bones[bone].constraints.new('STRETCH_TO')
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

    def __init__(self, armature, bone_const_name, constraint_name, name="NoPropertyName"):

        self.armature = armature
        self.bone_const_name = bone_const_name
        self.constraint_name = constraint_name
        self.description = ""
        self.property_name = name
        self.default = 0.0
        self.min = 0.0
        self.max = 1.0

    def apply_driver(self, bone_name):
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

        bone_const = self.bone_const_name
        constraints = self.constraint_name
        driver_value = 'pose.bones["' + bone_const + '"].constraints["' + constraints + '"].influence'
        driver = self.armature.driver_add(driver_value).driver
        set_driver(self.armature, driver, bone_name, self.property_name)


def create_bone_custom_property(armature, property_bone_name, property_name, default=0.0, value_min=0.0, value_max=1.0, description='..', overridable=True):
    """
    Creates a custom property for the specified bone in the armature.
    """
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
    property_bone.property_overridable_library_set('["' + property_name + '"]', overridable)

    return 'pose.bones["' + property_bone_name + '"]["' + property_name + '"]'


def set_driver(armature, driver, bone_name, driver_name, clean_previous=True):
    """
    Sets up a driver for the specified bone and property in the armature.
    """
    if clean_previous:
        utils.clear_driver_var(driver)
    v = driver.variables.new()
    v.name = driver_name.replace(" ", "_")
    v.targets[0].id = armature
    v.targets[0].data_path = 'pose.bones["' + bone_name + '"]["' + driver_name + '"]'
    driver.expression = driver_name.replace(" ", "_")
    return v


def subdivise_one_bone(armature, bone_name, subdivise_prefix_name="Subdivise_", split_number=2, keep_parent=True, ):
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

    # Vars
    edit_bone = armature.data.edit_bones[bone_name]
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


def duplicate_bone(armature, bone_name, new_name=None):
    """
    Creates a duplicate bone in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        bone_name (str): The name of the bone to duplicate.
        new_name (str, optional): The name of the new bone. If None, a default name will be generated.

    Returns:
        str: The name of the created bone.
    """
    edit_bone = armature.data.edit_bones[bone_name]
    if new_name is None:
        new_name = edit_bone.name + "_dup"
    new_bone = armature.data.edit_bones.new(new_name)
    new_bone.head = edit_bone.head
    new_bone.tail = edit_bone.tail
    new_bone.roll = edit_bone.roll
    new_bone.inherit_scale = edit_bone.inherit_scale

    new_bone.parent = edit_bone.parent
    new_bone.layers = edit_bone.layers

    return new_bone.name


def copy_constraint(armature, copy_bone_name, paste_bone_name, clear=True):
    """
    Copies constraints from one bone to another in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        copy_bone_name (str): The name of the bone from which to copy the constraints.
        paste_bone_name (str): The name of the bone to which the constraints are copied.
        clear (bool, optional): Indicates whether to clear existing constraints in the destination bone. Defaults to True.
    """
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



def set_bones_lock(armature, bone_names, lock):
    for bone_name in bone_names:
        set_bone_lock(armature, bone_name, lock)


def set_bone_lock(armature, bone_name, lock):
    # Check if we are in Pose mode
    if armature.mode != 'POSE':
        print("Error: You must be in Pose mode to modify bone locks.")
        return
    
    # Check if the bone exists in the armature
    if bone_name not in armature.pose.bones:
        print(f"Error: Bone '{bone_name}' does not exist in the armature.")
        return

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