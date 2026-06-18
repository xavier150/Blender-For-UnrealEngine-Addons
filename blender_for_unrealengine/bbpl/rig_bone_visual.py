# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import List, Tuple, Union


def get_theme_colors(theme: str = "DEFAULT") -> List[Tuple[float, float, float]]:
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
    armature: bpy.types.Object,
    bone_name: str,
    shape_obj: bpy.types.Object,
    use_bone_size: bool = True,
    shape_scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    shape_translation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    shape_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    override_transform_bone_name: str = ""
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
    if armature.pose is None:
        return False

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


if bpy.app.version <= (3, 6, 0):
    def create_bone_group(armature: bpy.types.Object, name: str, theme: str = "DEFAULT"):   # type: ignore
        """
        Deprecated in Blender 4.0
        Creates a bone group in the armature with the specified name and color theme.

        Args:
            armature (bpy.types.Object): The armature object.
            name (str): The name of the bone group.
            theme (str, optional): The color theme of the bone group. Defaults to "DEFAULT".

        Returns:
            bpy.types.PoseBoneGroup: The created bone group.
        """
        if name in armature.pose.bone_groups:  # type: ignore
            group = armature.pose.bone_groups[name]  # type: ignore
        else:
            group = armature.pose.bone_groups.new(name=name)  # type: ignore

        if theme == "DEFAULT":
            group.color_set = "DEFAULT"
        else:
            colors = get_theme_colors(theme)
            group.color_set = 'CUSTOM'
            group.colors.normal = colors[0]  # type: ignore
            group.colors.select = colors[1]  # type: ignore
            group.colors.active = colors[2]  # type: ignore

        return group  # type: ignore


    def direct_add_to_bone_group(armature: bpy.types.Object, bones: Union[str, List[str]], group_name: str):
        """
        Deprecated in Blender 4.0
        Adds the specified bones to a bone group in the armature.

        Args:
            armature (bpy.types.Object): The armature object.
            bones (str or list): The name(s) of the bone(s) to add to the bone group.
            group_name (str): The name of the bone group.

        Returns:
            None
        """

        if isinstance(bones, list):
            for bone_name in bones:  # type: ignore
                armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]  # type: ignore
        else:
            bone_name = bones  # type: ignore
            armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]  # type: ignore
