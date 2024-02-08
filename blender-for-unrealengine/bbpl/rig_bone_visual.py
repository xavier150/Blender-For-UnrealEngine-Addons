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

import bpy
import bmesh
from . import utils


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
        object_to_use: bpy.types.Object,
        shape_mirror_mode=False,
        shape_target_origin="BoneOrigin",
        construct_add_line=False,
        apply_modifiers=False
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

    
    scene = bpy.context.scene
    bone = armature.data.bones.get(bone_name)
    new_shape_name = "Shape_CustomGeneratedShape_" + bone_name

    # Vérifier si la forme existe et la supprimer le cas échéant
    if new_shape_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[new_shape_name], do_unlink=True)

    def link_shape_object(obj):
        shape_collection = utils.get_rig_collection(armature, "SHAPE")
        shape_collection.objects.link(obj)

    def apply_shape_modifiers(obj):
        scene.render.use_simplify = False

        # Exit current mode
        #if bpy.context.object.mode != 'OBJECT':
        #    if bpy.ops.object.mode_set.poll():
        #        bpy.ops.object.mode_set(mode='OBJECT')
        
        if bpy.app.version >= (4, 0, 0):
            with bpy.context.temp_override(active_object=obj, object=obj):
                for mod in obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        else:
            override_context = bpy.context.copy()
            override_context['active_object'] = obj
            override_context['object'] = obj
            for mod in obj.modifiers:
                bpy.ops.object.modifier_apply(override_context, modifier=mod.name)

    # Créer la nouvelle forme
    new_shape = object_to_use.copy()
    #new_shape.name = new_shape_name #Why this take so many time??? Around 4000% more time!
    new_shape.data = new_shape.data.copy()
    link_shape_object(new_shape)
    

    if apply_modifiers:
        apply_shape_modifiers(new_shape)  # Appliquer les modificateurs


    if shape_target_origin != "BoneOrigin" or shape_mirror_mode or construct_add_line:
        # ...
        def mirror_bmesh(verts):
            for v in verts:
                v.co.x *= -1

        # Transformations en fonction de l'origine cible
        def transform_bmesh(verts):
            if shape_target_origin == "ArmatureOrigin":
                bl = bone.matrix_local
                for v in verts:
                    v.co = v.co - bl.to_translation()
                    v.co = v.co @ (bl)

            elif shape_target_origin == "SceneOrigin":
                bl = bone.matrix_local
                for v in verts:
                    if shape_mirror_mode:
                        v.co.x *= -1
                    v.co = v.co + object_to_use.location
                    v.co = v.co - bl.to_translation()
                    v.co = v.co @ (bl)

        # ...
        def add_bmesh_line(bm):
            v1 = bm.verts.new((0.0, 0.0, 0.0))
            if shape_target_origin == "BoneOrigin":
                v2 = bm.verts.new((0.0, 1.0, 0.0))
            else:
                bone_length = armature.data.bones.get(bone_name).length
                v2 = bm.verts.new((0.0, bone_length, 0.0))
            bm.edges.new((v1, v2))

        me = new_shape.data
        bm = bmesh.new()
        bm.from_mesh(me)

        if shape_mirror_mode:
            mirror_bmesh(bm.verts)

        if shape_target_origin != "BoneOrigin":
            transform_bmesh(bm.verts)

        if construct_add_line:
            add_bmesh_line(bm)

        bm.to_mesh(me)
        bm.free()

    return new_shape

if bpy.app.version <= (3, 6, 0):
    def create_bone_group(armature, name, theme="DEFAULT"):
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
            for bone_name in bones:
                armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]
        else:
            bone_name = bones
            armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[group_name]
