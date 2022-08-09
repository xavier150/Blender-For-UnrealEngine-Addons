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
#  This addons allows to easily export several objects at the same time in .fbx
#  for use in unreal engine 4 by removing the usual constraints
#  while respecting UE4 naming conventions and a clean tree structure.
#  It also contains a small toolkit for collisions and sockets
#  xavierloux.com
# ----------------------------------------------

import bpy
import bmesh
from . import utils


class BoneVisualHelper():
    '''
    A class of function for help with bone visual
    '''

    def _get_shape_use_bone_size(self):
        return self.__shape_use_bone_size

    def _set_shape_use_bone_size(self, value):
        if not isinstance(value, bool):
            raise TypeError("shape_use_bone_size must be set to an Boolean")
        self.__shape_use_bone_size = value

    shape_use_bone_size = property(_get_shape_use_bone_size, _set_shape_use_bone_size)

    def __init__(self, armature, source_context):
        if armature:
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

    def DelegateLayer(self, bones: str):
        if not isinstance(bones, list):
            bones = [bones]  # Convert to list

        for bone_name in bones:
            scene = bpy.context.scene
            delegate = scene.mar_layer_delegates.add()
            delegate.armature = self.armature
            delegate.bone_name = bone_name
            delegate.layer_index = self.bone_layer
            delegate.source_context = self.source_context

    def DelegateShape(self, bones: str):

        scene = bpy.context.scene

        if not isinstance(bones, list):
            bones = [bones]  # Convert to list

        for bone_name in bones:
            delegate = scene.mar_customshape_delegates.add()
            delegate.armature = self.armature
            delegate.bone_name = bone_name
            delegate.shape_name = self.shape_name
            delegate.shape_use_bone_size = self.shape_use_bone_size
            delegate.SetScale(self.shape_scale)
            delegate.shape_translation = self.shape_translation
            delegate.shape_rotation = self.shape_rotation
            delegate.shape_transform = self.shape_transform
            delegate.source_context = self.source_context

    def DelegateBoneGroup(self, bones: str):
        '''
        Add a bone to a group.
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

    def ApplyGroup(self, bone_name):
        # self.DelegateBoneGroup(bone_name) # Force delegate
        # return

        if self.armature is not None:

            DirectAddToBonesGroup(
                self.armature,
                bone_name,
                self.group_name,
                self.group_theme,
                )
        else:
            raise TypeError('Armature is none. Source: {0}'.format(self.source_context))


def GetThemeColors(Theme="DEFAULT"):

    if Theme == "DEFAULT":
        return [
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ]
    elif Theme == "RED":
        return [
            (0.603922, 0, 0),
            (0.741176, 0.0666667, 0.0666667),
            (0.968628, 0.0392157, 0.0392157),
        ]
    elif Theme == "BLUE":
        return [
            (0.0392157, 0.211765, 0.580392),
            (0.211765, 0.403922, 0.87451),
            (0.368627, 0.756863, 0.937255),
        ]
    elif Theme == "YELLOW":
        return [
            (0.956863, 0.788235, 0.0470588),
            (0.933333, 0.760784, 0.211765),
            (0.952941, 1, 0),
        ]
    elif Theme == "PURPLE":
        return [
            (0.262745, 0.0470588, 0.470588),
            (0.329412, 0.227451, 0.639216),
            (0.529412, 0.392157, 0.835294),
        ]
    elif Theme == "GREEN":
        return [
            (0.117647, 0.568627, 0.0352941),
            (0.34902, 0.717647, 0.0431373),
            (0.513726, 0.937255, 0.113725),
        ]
    else:
        print("Error in GetThemeColors() "+Theme+" not found!")
        return [
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ]


def updateBoneShape(
    armature,
    boneName,
    shapeObj,
    useBoneSize=True,
    shapeScale=(1.0, 1.0, 1.0),
    shapeTranslation=(0.0, 0.0, 0.0),
    shapeRotation=(0.0, 0.0, 0.0),
    overrideTransformBoneName=""
        ):

    armature.pose.bones[boneName].custom_shape = shapeObj
    armature.pose.bones[boneName].use_custom_shape_bone_size = useBoneSize
    armature.pose.bones[boneName].custom_shape_scale_xyz = shapeScale
    armature.pose.bones[boneName].custom_shape_translation = shapeTranslation
    armature.pose.bones[boneName].custom_shape_rotation_euler = shapeRotation

    if not overrideTransformBoneName == "":
        armature.pose.bones[boneName].custom_shape_transform = armature.pose.bones[overrideTransformBoneName]
    else:
        armature.pose.bones[boneName].custom_shape_transform = None

    return True


def generateBoneShapeFromProp(
        armature,
        bone_name,
        object_use,
        shape_mirror_mode=False,
        shape_target_origin="BoneOrigin",  # GetShapeTargetOriginItems
        construct_add_line=False
        ):

    def LinkShapeObj(obj):
        col = utils.getRigCollection(armature, "SHAPE")
        col.objects.link(obj)
        return col

    bone_length = armature.data.bones[bone_name].length
    NewShapeName = "Shape_CustomGeneratedShape_"+bone_name
    if NewShapeName in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[NewShapeName])  # Clean for recreate

    # Create the new shape
    NewShape = object_use.copy()
    NewShape.data = NewShape.data.copy()
    LinkShapeObj(NewShape)
    NewShape.name = NewShapeName

    # Transform for apply mirror mode
    if shape_mirror_mode is True:
        for v in NewShape.data.vertices:
            v.co.x *= -1

    # Transform for apply shape mode
    if shape_target_origin == "BoneOrigin":
        pass

    elif shape_target_origin == "ArmatureOrigin":
        b = armature.data.bones[bone_name].matrix
        bl = armature.data.bones[bone_name].matrix_local
        for v in NewShape.data.vertices:
            pass
            v.co = v.co - bl.to_translation()
            v.co = v.co @ (bl)

    elif shape_target_origin == "SceneOrigin":
        b = armature.data.bones[bone_name].matrix
        bl = armature.data.bones[bone_name].matrix_local
        for v in NewShape.data.vertices:
            pass
            v.co = v.co + object_use.location
            v.co = v.co - bl.to_translation()
            v.co = v.co @ (bl)

    NewShape.select_set(True)
    bpy.context.view_layer.objects.active = NewShape
    utils.modeSetOnTarget(NewShape, "EDIT")

    me = NewShape.data
    bm = bmesh.from_edit_mesh(me)

    if construct_add_line:
        # Add bone line
        v1 = bm.verts.new((0.0, 0.0, 0.0))
        if shape_target_origin == "BoneOrigin":
            v2 = bm.verts.new((0.0, 1.0, 0.0))
        else:
            v2 = bm.verts.new((0.0, bone_length, 0.0))
        bm.edges.new((v1, v2))

    # bm.to_mesh(me)
    bm.free()

    utils.modeSetOnTarget(NewShape, "OBJECT")

    return NewShape


def updateBoneShapeByName(
        armature,
        boneName,
        shapeObjName,
        useBoneSize=True,
        shapeScale=(1.0, 1.0, 1.0),
        shapeTranslation=(0.0, 0.0, 0.0),
        shapeRotation=(0.0, 0.0, 0.0),
        overrideTransformBoneName=""
        ):
    # Deprectared
    shapeObj = None
    if shapeObjName in bpy.data.objects:
        shapeObj = bpy.data.objects[shapeObjName]
    else:
        print('Shape "{0}" not found.'.format(shapeObjName))
        return False

    return updateBoneShape(
        armature=armature,
        boneName=boneName,
        shapeObj=shapeObj,
        useBoneSize=useBoneSize,
        shapeScale=shapeScale,
        shapeTranslation=shapeTranslation,
        shapeRotation=shapeRotation,
        overrideTransformBoneName=overrideTransformBoneName
    )


def CreateBoneGroup(armature, name, Theme="DEFAULT"):
    if name in armature.pose.bone_groups:
        group = armature.pose.bone_groups[name]
    else:
        group = armature.pose.bone_groups.new(name=name)

    if Theme == "DEFAULT":
        group.color_set = "DEFAULT"
    else:
        colors = GetThemeColors(Theme)
        group.color_set = 'CUSTOM'
        group.colors.normal = colors[0]
        group.colors.select = colors[1]
        group.colors.active = colors[2]


def DirectAddToBonesGroup(armature, bones, groupName):

    if type(bones) is list:
        for bone_name in bones:
            armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[groupName]
    else:
        bone_name = bones
        armature.pose.bones[bone_name].bone_group = armature.pose.bone_groups[groupName]
