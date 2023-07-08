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
import bmesh
from . import utils


class BoneVisualHelper:
    '''
    A class of functions to assist with bone visualization.
    '''

    def _get_shape_use_bone_size(self):
        return self.__shape_use_bone_size

    def _set_shape_use_bone_size(self, value):
        if not isinstance(value, bool):
            raise TypeError("shape_use_bone_size must be set to an Boolean")
        self.__shape_use_bone_size = value

    shape_use_bone_size = property(_get_shape_use_bone_size, _set_shape_use_bone_size)

    def __init__(self, armature, source_context):
        self.armature = armature
        self.shape_name: str = ""
        self.__shape_use_bone_size: bool = False
        self.shape_scale = (1.0, 1.0, 1.0)
        self.shape_translation = (0.0, 0.0, 0.0)
        self.shape_rotation = (0.0, 0.0, 0.0)
        self.shape_transform = ""
        self.group_name = "NoGroup"
        self.group_theme = "DEFAULT"
        self.bone_layer = 0
        self.source_context = source_context

    def delegate_layer(self, bones: str):
        '''
        Delegate the specified bones to the bone layer.
        '''
        if not isinstance(bones, list):
            bones = [bones]  # Convert to list

        for bone_name in bones:
            scene = bpy.context.scene
            delegate = scene.mar_layer_delegates.add()
            delegate.armature = self.armature
            delegate.bone_name = bone_name
            delegate.layer_index = self.bone_layer
            delegate.source_context = self.source_context

    def delegate_shape(self, bones: str):
        '''
        Delegate the specified bones to the custom shape.
        '''

        scene = bpy.context.scene

        if not isinstance(bones, list):
            bones = [bones]  # Convert to list

        for bone_name in bones:
            delegate = scene.mar_customshape_delegates.add()
            delegate.armature = self.armature
            delegate.bone_name = bone_name
            delegate.shape_name = self.shape_name
            delegate.shape_use_bone_size = self.shape_use_bone_size
            delegate.set_scale(self.shape_scale)
            delegate.shape_translation = self.shape_translation
            delegate.shape_rotation = self.shape_rotation
            delegate.shape_transform = self.shape_transform
            delegate.source_context = self.source_context

    def delegate_bone_group(self, bones: str):
        '''
        Add the specified bones to a bone group.
        '''

        if not isinstance(bones, list):
            bones = [bones]  # Convert to list

        for bone_name in bones:
            scene = bpy.context.scene
            delegate = scene.mar_bonegroup_delegates.add()
            delegate.armature = self.armature
            delegate.bone_name = bone_name
            delegate.group_name = self.group_name
            delegate.group_theme = self.group_theme
            delegate.source_context = self.source_context

    def apply_group(self, bone_name):
        '''
        Apply the bone group to the specified bone.
        '''

        if self.armature is not None:
            direct_add_to_bone_group(
                self.armature,
                bone_name,
                self.group_name
            )
        else:
            raise TypeError('Armature is None. Source: {0}'.format(self.source_context))


def get_theme_colors(theme="DEFAULT"):
    '''
    Retrieves the color values for the specified theme.
    '''

    if theme == "DEFAULT":
        return [
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ]
    elif theme == "RED":
        return [
            (0.603922, 0, 0),
            (0.741176, 0.0666667, 0.0666667),
            (0.968628, 0.0392157, 0.0392157),
        ]
    elif theme == "BLUE":
        return [
            (0.0392157, 0.211765, 0.580392),
            (0.211765, 0.403922, 0.87451),
            (0.368627, 0.756863, 0.937255),
        ]
    elif theme == "YELLOW":
        return [
            (0.956863, 0.788235, 0.0470588),
            (0.933333, 0.760784, 0.211765),
            (0.952941, 1, 0),
        ]
    elif theme == "PURPLE":
        return [
            (0.262745, 0.0470588, 0.470588),
            (0.329412, 0.227451, 0.639216),
            (0.529412, 0.392157, 0.835294),
        ]
    elif theme == "GREEN":
        return [
            (0.117647, 0.568627, 0.0352941),
            (0.34902, 0.717647, 0.0431373),
            (0.513726, 0.937255, 0.113725),
        ]
    else:
        raise ValueError("Unknown theme: " + theme)


def update_bone_shape(
    armature,
    bone_name,
    shape_obj,
    use_bone_size=True,
    shape_scale=(1.0, 1.0, 1.0),
    shape_translation=(0.0, 0.0, 0.0),
    shape_rotation=(0.0, 0.0, 0.0),
    override_transform_bone_name=""
):
    '''
    Updates the custom shape of a bone in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        bone_name (str): The name of the bone.
        shape_obj (bpy.types.Object): The custom shape object to assign to the bone.
        use_bone_size (bool): Indicates whether to use the bone size for the shape. Defaults to True.
        shape_scale (tuple): The scale of the custom shape. Defaults to (1.0, 1.0, 1.0).
        shape_translation (tuple): The translation of the custom shape. Defaults to (0.0, 0.0, 0.0).
        shape_rotation (tuple): The rotation of the custom shape in Euler angles. Defaults to (0.0, 0.0, 0.0).
        override_transform_bone_name (str): The name of the bone to override the shape's transform. Defaults to "".

    Returns:
        bool: True if the bone shape was successfully updated.

    Raises:
        KeyError: If the bone name or override transform bone name is not found in the armature.
    '''

    bone = armature.pose.bones.get(bone_name)
    if not bone:
        raise KeyError(f"Bone '{bone_name}' not found in the armature.")

    bone.custom_shape = shape_obj
    bone.use_custom_shape_bone_size = use_bone_size
    bone.custom_shape_scale_xyz = shape_scale
    bone.custom_shape_translation = shape_translation
    bone.custom_shape_rotation_euler = shape_rotation

    if override_transform_bone_name:
        override_transform_bone = armature.pose.bones.get(override_transform_bone_name)
        if not override_transform_bone:
            raise KeyError(f"Bone '{override_transform_bone_name}' not found in the armature.")
        bone.custom_shape_transform = override_transform_bone
    else:
        bone.custom_shape_transform = None

    return True


def generate_bone_shape_from_prop(
        armature,
        bone_name,
        object_use,
        shape_mirror_mode=False,
        shape_target_origin="BoneOrigin",
        construct_add_line=False
):
    '''
    Generates a custom bone shape object based on the provided object.

    Args:
        armature (bpy.types.Object): The armature object.
        bone_name (str): The name of the bone.
        object_use (bpy.types.Object): The object to use as the base shape.
        shape_mirror_mode (bool): Indicates whether to apply mirror mode to the shape. Defaults to False.
        shape_target_origin (str): The origin point for applying the shape transformation. Defaults to "BoneOrigin".
        construct_add_line (bool): Indicates whether to add a bone line to the shape. Defaults to False.

    Returns:
        bpy.types.Object: The generated custom shape object.

    Raises:
        KeyError: If the bone name is not found in the armature.
    '''
    def link_shape_obj(obj):
        col = utils.get_rig_collection(armature, "SHAPE")
        col.objects.link(obj)
        return col

    bone_length = armature.data.bones.get(bone_name).length
    new_shape_name = "Shape_CustomGeneratedShape_" + bone_name
    if new_shape_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[new_shape_name])  # Clean for recreate

    # Create the new shape
    new_shape = object_use.copy()
    new_shape.data = new_shape.data.copy()
    link_shape_obj(new_shape)
    new_shape.name = new_shape_name

    # Transform for apply mirror mode
    if shape_mirror_mode:
        for v in new_shape.data.vertices:
            v.co.x *= -1

    # Transform for apply shape mode
    if shape_target_origin == "BoneOrigin":
        pass

    elif shape_target_origin == "ArmatureOrigin":
        bone = armature.data.bones.get(bone_name)
        if not bone:
            raise KeyError(f"Bone '{bone_name}' not found in the armature.")
        bl = bone.matrix_local
        for v in new_shape.data.vertices:
            v.co -= bl.to_translation()
            v.co @= bl

    elif shape_target_origin == "SceneOrigin":
        bone = armature.data.bones.get(bone_name)
        if not bone:
            raise KeyError(f"Bone '{bone_name}' not found in the armature.")
        bl = bone.matrix_local
        for v in new_shape.data.vertices:
            v.co += object_use.location
            v.co -= bl.to_translation()
            v.co @= bl

    new_shape.select_set(True)
    bpy.context.view_layer.objects.active = new_shape
    utils.mode_set_on_target(new_shape, "EDIT")

    me = new_shape.data
    bm = bmesh.from_edit_mesh(me)

    if construct_add_line:
        # Add bone line
        v1 = bm.verts.new((0.0, 0.0, 0.0))
        if shape_target_origin == "BoneOrigin":
            v2 = bm.verts.new((0.0, 1.0, 0.0))
        else:
            v2 = bm.verts.new((0.0, bone_length, 0.0))
        bm.edges.new((v1, v2))

    bm.free()

    utils.mode_set_on_target(new_shape, "OBJECT")

    return new_shape

def update_bone_shape_by_name(
    armature,
    bone_name,
    shape_obj_name,
    use_bone_size=True,
    shape_scale=(1.0, 1.0, 1.0),
    shape_translation=(0.0, 0.0, 0.0),
    shape_rotation=(0.0, 0.0, 0.0),
    override_transform_bone_name=""
):
    """
    Deprecated function. Updates the shape of a bone in the armature based on the provided shape object name.

    Args:
        armature (bpy.types.Object): The armature object.
        bone_name (str): The name of the bone.
        shape_obj_name (str): The name of the shape object.
        use_bone_size (bool, optional): Indicates whether to use the bone's size. Defaults to True.
        shape_scale (tuple, optional): The scale of the shape object. Defaults to (1.0, 1.0, 1.0).
        shape_translation (tuple, optional): The translation offset of the shape object. Defaults to (0.0, 0.0, 0.0).
        shape_rotation (tuple, optional): The rotation angles of the shape object in radians. Defaults to (0.0, 0.0, 0.0).
        override_transform_bone_name (str, optional): The name of the bone used for transforming the shape object. Defaults to "".

    Returns:
        bool: True if the bone shape was updated successfully, False otherwise.
    """

    # Deprecated
    shape_obj = bpy.data.objects.get(shape_obj_name, None)
    if not shape_obj:
        print(f'Shape "{shape_obj_name}" not found.')
        return False

    return update_bone_shape(
        armature=armature,
        bone_name=bone_name,
        shape_obj=shape_obj,
        use_bone_size=use_bone_size,
        shape_scale=shape_scale,
        shape_translation=shape_translation,
        shape_rotation=shape_rotation,
        override_transform_bone_name=override_transform_bone_name
    )


def create_bone_group(armature, name, theme="DEFAULT"):
    """
    Creates a bone group in the armature with the specified name and color theme.

    Args:
        armature (bpy.types.Object): The armature object.
        name (str): The name of the bone group.
        theme (str, optional): The color theme of the bone group. Defaults to "DEFAULT".

    Returns:
        bpy.types.PoseBoneGroup: The created bone group.
    """
    if name in armature.pose.bone_groups:
        group = armature.pose.bone_groups[name]
    else:
        group = armature.pose.bone_groups.new(name=name)

    if theme == "DEFAULT":
        group.color_set = "DEFAULT"
    else:
        colors = get_theme_colors(theme)
        group.color_set = 'CUSTOM'
        group.colors.normal = colors[0]
        group.colors.select = colors[1]
        group.colors.active = colors[2]

    return group


def direct_add_to_bone_group(armature, bones, group_name):
    """
    Adds the specified bones to a bone group in the armature.

    Args:
        armature (bpy.types.Object): The armature object.
        bones (str or list): The name(s) of the bone(s) to add to the bone group.
        group_name (str): The name of the bone group.

    Returns:
        None
    """

    if isinstance(bones, list):
        for bone_name in bones:
            armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]
    else:
        bone_name = bones
        armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]
