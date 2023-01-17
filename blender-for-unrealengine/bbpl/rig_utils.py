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


from typing import Type
import bpy


from .. import bbpl
from .. import bps

import mathutils


def createSafeBone(armature, bone_name, layer=None):
    if bone_name in armature.data.edit_bones:
        print("Bone alredy exit! : "+bone_name)
        raise TypeError("Bone alredy exit! : "+bone_name)
        return

    bone = armature.data.edit_bones.new(bone_name)
    bone.tail = bone.head + mathutils.Vector((0, 0, 1))

    if layer:
        changeCurrentLayer(0, bpy.context.object.data)
        changeCurrentLayer(layer, bone)

    return bone

# Naming


def getMirrorBoneName(original_bones: str, debug=False):

    bones = []
    new_bones = []

    if not isinstance(original_bones, list):
        bones = [original_bones]  # Convert to list
    else:
        bones = original_bones

    def TryToInvertBones(bone):
        def Invert(bone, old, new):
            if bone.endswith(old):
                new_bone_name = bone[:-len(old)]
                new_bone_name = new_bone_name+new
                return new_bone_name
            return None

        change = [
                ["_l", "_r"],
                ["_L", "_R"]
            ]
        for c in change:
            a = Invert(bone, c[0], c[1])
            if a:
                return a
            b = Invert(bone, c[1], c[0])
            if b:
                return b

        # Return original If no invert found.
        return bone

    for bone in bones:
        new_bones.append(TryToInvertBones(bone))

    # Can return same bone when don't found mirror
    if not isinstance(original_bones, list):
        return new_bones[0]
    else:
        return new_bones


def getNameWithNewPrefix(Name, old_prefix, new_prefix):
    '''
    Remplace an prefix and add a new prefix.
    '''

    new_bone_name = Name
    if new_bone_name.startswith(old_prefix):
        new_bone_name = new_bone_name[len(old_prefix):]
        new_bone_name = new_prefix+new_bone_name
    else:
        raise TypeError('"' + old_prefix + '" not found as prefix in "' + Name + '".')
    return new_bone_name


def getNameListWithNewPrefix(NameList, old_prefix, new_prefix):
    '''
    Remplace an prefix and add a new prefix to a list.
    '''

    new_list = []
    for name in NameList:
        new_list.append(getNameWithNewPrefix(name, old_prefix, new_prefix))
    return new_list


def noNum(name):
    # get bnone name without number index
    u = name[-4:]
    if u == ".000" or u == ".001" or u == ".002" or u == ".003":
        return name[:-4]
    return name

# Layer type


def inConstructLayer(armature, source):
    if source.layers[armature.mar_construct_layer] is True:
        return True
    return False


def inDeformLayer(armature, source):
    if source.layers[armature.mar_deform_layer] is True:
        return True
    return False


def inRigLayer(armature, source):
    if source.layers[armature.mar_rig_layer] is True:
        return True
    return False


def inRigJointLayer(armature, source):
    if source.layers[armature.mar_rig_joint_layer] is True:
        return True
    return False

# Bone type


def isConstructBone(armature, source):
    if source.name.startswith(armature.mar_construct_prefix) is True:
        return True
    return False


def isDeformBone(armature, source):
    if source.name.startswith(armature.mar_deform_prefix) is True:
        return True
    return False


def isRigBone(armature, source):
    if source.name.startswith(armature.mar_rig_prefix) is True:
        return True
    return False


def isRigJointBone(armature, source):
    if source.name.startswith(armature.mar_rig_joint_prefix) is True:
        return True
    return False


def changeCurrentLayer(layer, source):
    source.layers[layer] = True
    for i in range(0, 32):
        if i != layer:
            source.layers[i] = False


def changeSelectLayer(layer):
    bpy.ops.armature.bone_layers(layers=(
        layer == 0,
        layer == 1,
        layer == 2,
        layer == 3,
        layer == 4,
        layer == 5,
        layer == 6,
        layer == 7,
        layer == 8,
        layer == 9,
        layer == 10,
        layer == 11,
        layer == 12,
        layer == 13,
        layer == 14,
        layer == 15,
        layer == 16,
        layer == 17,
        layer == 18,
        layer == 19,
        layer == 20,
        layer == 21,
        layer == 22,
        layer == 23,
        layer == 24,
        layer == 25,
        layer == 26,
        layer == 27,
        layer == 28,
        layer == 29,
        layer == 30,
        layer == 31
    ))


def changeUserViewLayer(layer):
    changeCurrentLayer(layer, bpy.context.object.data)


def duplicateRigLayer(armature, original_layer, new_layer, old_prefix, new_prefix, process_title="Duplicate Rig Layer"):

    bbpl.utils.safeModeSet(armature, "EDIT")
    changeCurrentLayer(original_layer, bpy.context.object.data)
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.duplicate()
    changeSelectLayer(new_layer)  # Move bone to layer
    changeUserViewLayer(new_layer)  # Move self to layer

    NewBonesNames = []
    for bone in bpy.context.selected_bones:
        NewBonesNames.append(bone.name)

    pbc = bps.advprint.ProgressionBarClass()
    pbc.name = process_title
    pbc.total_step = len(NewBonesNames)

    armature.data.pose_position = 'REST'
    bbpl.utils.safeModeSet(armature, "OBJECT")
    for x, bone_name in enumerate(NewBonesNames):
        new_bone_name = getNameWithNewPrefix(bone_name, old_prefix, new_prefix)
        new_bone_name = noNum(new_bone_name)
        armature.data.bones[bone_name].name = new_bone_name  # Why this take so many time ?
        pbc.update_progress(x+1)

    armature.data.pose_position = 'POSE'
    return NewBonesNames


def createRigCollectionSubFolder(armature, col_type="RIG"):
    def newRigCollection(collection_name):
        myCol = bbpl.utils.getSafeCollection(collection_name)
        myCol.color_tag = "COLOR_01"
        myCol.hide_render = True
        # Add custom property to found witch collection should be removed when regenerate.
        myCol["Info"] = "GenerateFromModularAutoRig"
        return myCol

    main_collection_name = armature.users_collection[0].name
    rig_col = bpy.data.collections[main_collection_name]

    if col_type == "SHAPE":
        shapes_Col = newRigCollection(armature.name+armature.mar_shapes_collection_prefix)
        if shapes_Col.name not in rig_col.children:
            rig_col.children.link(shapes_Col)
        return shapes_Col
    elif col_type == "CURVE":
        curves_Col = newRigCollection(armature.name+armature.mar_curves_collection_prefix)
        if curves_Col.name not in rig_col.children:
            rig_col.children.link(curves_Col)
        return curves_Col
    elif col_type == "CAMERA":
        cameras_Col = newRigCollection(armature.name+armature.mar_cameras_collection_prefix)
        if cameras_Col.name not in rig_col.children:
            rig_col.children.link(cameras_Col)
        return cameras_Col
    else:
        print("In getRigCollection() "+col_type+" not found!")
        raise TypeError("In getRigCollection() "+col_type+" not found!")


def getRigCollectionSubFolder(armature, col_type="RIG"):

    main_collection_name = armature.users_collection[0].name
    rig_col = bpy.data.collections[main_collection_name]

    if col_type == "SHAPE":
        return bbpl.utils.getSafeCollection(armature.name+armature.mar_shapes_collection_prefix)

    elif col_type == "CURVE":
        return bbpl.utils.getSafeCollection(armature.name+armature.mar_curves_collection_prefix)

    elif col_type == "CAMERA":
        return bbpl.utils.getSafeCollection(armature.name+armature.mar_cameras_collection_prefix)

    else:
        print("In getRigCollection() "+col_type+" not found!")
        raise TypeError("In getRigCollection() "+col_type+" not found!")


class OrphanBone():
    def __init__(self, armature, child_bone):
        self.armature = armature
        self.name = child_bone.name
        self.old_parent_name = child_bone.parent.name
        self.new_parent_name = ""

    def ApplyNewParent(self):
        if self.new_parent_name != "":
            for bone in self.armature.data.edit_bones:
                if bone.name == self.name:
                    bone.parent = self.armature.data.edit_bones[self.new_parent_name]
                    # print(bone.name, " child for ", self.new_parent_name)  # Debug
        else:
            print("Error new_parent not set in orphan_bone() for " + self.name)


def setBoneOrientation(armature, bone_name, vector, roll):
    bone = armature.data.edit_bones[bone_name]
    length = bone.length
    bone.tail = bone.head + vector*length
    bone.roll = roll


def setBoneLength(armature, bone_name, new_length, apply_tail=True):
    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head
    vector.normalize()

    new_tail = bone.head+(vector*new_length)
    if apply_tail:
        bone.tail = new_tail
    return new_tail


def getBoneVector(armature, bone_name):
    head = armature.data.edit_bones[bone_name].head
    tail = armature.data.edit_bones[bone_name].tail
    return head - tail


def setBoneScale(armature, bone_name, new_scale, apply_tail=True):
    bone = armature.data.edit_bones[bone_name]
    vector = bone.tail - bone.head

    new_tail = bone.head+(vector*new_scale)
    if apply_tail:
        bone.tail = new_tail
    return new_tail


def createHeadControlPoint(armature, bone_name, add_controller=False, prefix="TailControlPoint_"):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    bone = armature.data.edit_bones[bone_name]
    rp_bone = armature.data.edit_bones[rp+bone_name]

    '''
    Cree bone RP pour le parent et l'enfant.
    '''

    rp_point_bone_name = rjp+"HeadControlPoint_"+bone_name
    rp_point_bone = bbpl.rig_utils.createSafeBone(armature, rp_point_bone_name, layer=armature.mar_rig_joint_layer)
    rp_point_bone.parent = rp_bone

    '''
    Defini leur position.
    '''

    bone_length = 0.02*armature.mar_rig_bone_scale
    target_head = bone.head
    target_tail = setBoneLength(armature, bone_name, bone_length, apply_tail=False)
    target_roll = bone.roll

    rp_point_bone.head = target_head
    rp_point_bone.tail = target_tail
    rp_point_bone.roll = target_roll

    if add_controller:
        controller_bone_name = rp+prefix+bone_name
        controller_bone = createSafeBone(armature, controller_bone_name, layer=getLayerByName(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rp_point_bone
        return controller_bone_name


def createTailControlPoint(armature, bone_name, add_controller=False, prefix="TailControlPoint_"):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    bone = armature.data.edit_bones[bone_name]
    rp_bone = armature.data.edit_bones[rp+bone_name]

    '''
    Cree bone RP pour le parent et l'enfant.
    '''

    rp_point_bone_name = rjp+"TailControlPoint_"+bone_name
    rp_point_bone = bbpl.rig_utils.createSafeBone(armature, rp_point_bone_name, layer=armature.mar_rig_joint_layer)
    rp_point_bone.parent = rp_bone

    '''
    Defini leur position.
    '''

    bone_length = 0.02*armature.mar_rig_bone_scale
    target_head = bone.tail
    target_tail = setBoneLength(armature, bone_name, bone_length, apply_tail=False) - bone.head + bone.tail
    target_roll = bone.roll

    rp_point_bone.head = target_head
    rp_point_bone.tail = target_tail
    rp_point_bone.roll = target_roll

    if add_controller:
        controller_bone_name = rp+prefix+bone_name
        controller_bone = createSafeBone(armature, controller_bone_name, layer=getLayerByName(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rp_point_bone
        return controller_bone_name


def createBoneInterpolation(armature, parent_bone_name, child_bone_name, position_Mode="PARENT",
                            desired_head=None, desired_tail=None, desired_roll=None,
                            add_controller=False, mode="ROTATION",
                            strech_by_diference=False, strech_axe=0, prefix="Interp_"
                            ):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    parent_bone = armature.data.edit_bones[rp+parent_bone_name]
    child_bone = armature.data.edit_bones[rp+child_bone_name]

    '''
    Je cree deux bone RP pour le parent et l'enfant.
    '''

    rp_parent_bone_name = rjp+"InterpParent_"+parent_bone_name
    rp_parent_bone = createSafeBone(armature, rp_parent_bone_name, layer=armature.mar_rig_joint_layer)
    rp_parent_bone.parent = parent_bone

    rp_child_bone_name = rjp+"InterpChild_"+parent_bone_name
    rp_child_bone = createSafeBone(armature, rp_child_bone_name, layer=armature.mar_rig_joint_layer)
    rp_child_bone.parent = child_bone

    '''
    Defini leur position cree deux bone RP pour le parent et l'enfant.
    (Ils aurons tout les deux bone la meme position.)
    '''

    bone_length = 0.02*armature.mar_rig_bone_scale

    if position_Mode == "PARENT":
        target_head = child_bone.head
        target_tail = setBoneLength(armature, rp+parent_bone_name, bone_length, apply_tail=False) - parent_bone.head + child_bone.head
        target_roll = parent_bone.roll

    elif position_Mode == "CHILD":
        target_head = child_bone.head
        target_tail = setBoneLength(armature, rp+child_bone_name, bone_length, apply_tail=False)
        target_roll = child_bone.roll

    elif position_Mode == "MIX":
        target_head = child_bone.head
        vector_parent = (parent_bone.tail - parent_bone.head)
        vector_child = (child_bone.tail - child_bone.head)
        vector_parent.normalize()
        vector_child.normalize()
        vector_target = ((vector_parent + vector_child) / 2) * bone_length
        target_tail = child_bone.head + vector_target
        target_roll = (child_bone.roll + child_bone.roll) / 2

    elif position_Mode == "UP":
        target_head = child_bone.head
        target_tail = target_head+mathutils.Vector((0, 0, bone_length))
        target_roll = 0

    else:
        raise TypeError('Position mode not found!' + position_Mode)

    if desired_head:
        target_head = desired_head

    if desired_tail:
        target_tail = desired_tail

    if desired_roll:
        target_roll = desired_roll

    rp_parent_bone.head = target_head
    rp_parent_bone.tail = target_tail
    rp_parent_bone.roll = target_roll

    rp_child_bone.head = target_head
    rp_child_bone.tail = target_tail
    rp_child_bone.roll = target_roll

    if strech_by_diference:
        rp_parent_strech_bone = armature.data.edit_bones[duplicateBone(armature, rp_parent_bone_name)]
        rp_parent_strech_bone_name = rp_parent_strech_bone.name
        rp_child_strech_bone = armature.data.edit_bones[duplicateBone(armature, rp_child_bone_name)]
        rp_child_strech_bone_name = rp_child_strech_bone.name

    '''
    Je cree un 3eme os qui ferra l'interpolation entre les deux premier
    '''

    rp_interp_bone_name = rjp+"Interp_"+parent_bone_name
    rp_interp_bone = createSafeBone(armature, rp_interp_bone_name, layer=armature.mar_rig_joint_layer)

    rp_interp_bone.head = target_head
    rp_interp_bone.tail = target_tail
    rp_interp_bone.roll = target_roll
    if strech_by_diference:
        rp_interp_bone.parent = rp_parent_strech_bone
    else:
        rp_interp_bone.parent = rp_parent_bone

    if add_controller:
        controller_bone_name = rp+prefix+parent_bone_name
        controller_bone = createSafeBone(armature, controller_bone_name, layer=getLayerByName(armature, "Default"))
        controller_bone.head = target_head
        controller_bone.tail = target_tail
        controller_bone.roll = target_roll
        controller_bone.parent = rp_interp_bone

    bpy.ops.object.mode_set(mode='POSE')
    if mode == "ROTATION":
        consName = "COPY_ROTATION"
    elif mode == "LOCATION":
        consName = "COPY_LOCATION"
    elif mode == "TRANSFROM":
        consName = "COPY_TRANSFORMS"
    else:
        raise TypeError("Error in createBoneInterpolation() consName "+consName+" not valid.")

    constraint = armature.pose.bones[rp_interp_bone_name].constraints.new(consName)
    constraint.target = armature
    if strech_by_diference:
        constraint.subtarget = rp_child_strech_bone_name
    else:
        constraint.subtarget = rp_child_bone_name
    constraint.name = "Interpolation follow rotation"
    constraint.influence = 0.5

    if strech_by_diference:
        '''
        Ici je cree un driver pour modifier le scale en fonction de l'interp
        '''

        def CreateStrechDriver(bone_name, value="min_x", axe_index=0):
            driver_strech_name = 'pose.bones["'+bone_name+'"].scale'

            driver_strech = armature.driver_add(driver_strech_name, axe_index).driver
            bbpl.utils.clearDriverVar(driver_strech)
            v = driver_strech.variables.new()
            v.name = "Interp_strech_by_diference"
            v.type = 'ROTATION_DIFF'
            v.targets[0].id = armature
            v.targets[1].id = armature
            v.targets[0].bone_target = rp_parent_bone_name
            v.targets[1].bone_target = rp_child_bone_name
            driver_strech.expression = "1+"+v.name
            return driver_strech

        strech_drivers = []
        strech_drivers.append(CreateStrechDriver(rp_parent_strech_bone_name, "min_z", strech_axe))
        strech_drivers.append(CreateStrechDriver(rp_child_strech_bone_name, "max_z", strech_axe))

    if add_controller:
        # Gestion des driver
        MyProperty = DriverPropertyHelpper(armature, rp_interp_bone_name, constraint.name, name="Follow_Child")
        MyProperty.default = 0.5
        MyProperty.description = "Follow child factor."
        MyProperty.ApplyDriver(controller_bone_name, constraint)

    bpy.ops.object.mode_set(mode='EDIT')

    class InterpBone():
        def __init__(self):
            self.parent = rp_parent_bone_name
            self.child = rp_child_bone_name
            self.interp = rp_interp_bone_name

            if strech_by_diference:
                self.parent_strech = rp_parent_strech_bone_name
                self.child_strech = rp_child_strech_bone_name
                self.strech_drivers = strech_drivers
            else:
                self.parent_strech = None
                self.child_strech = None
                self.strech_drivers = None
            if add_controller:
                self.controller = controller_bone_name

    interp = InterpBone()
    return interp


def createRpBone(armature, BoneName, make_it_parent=True, custom_rjp_parent="", new_bone_name=""):

    # CreationOs
    rjp = armature.mar_rig_joint_prefix
    desired_bone_name = rjp+BoneName
    if new_bone_name != "":
        desired_bone_name = rjp+new_bone_name
    NewRpBone = armature.data.edit_bones.new(desired_bone_name)
    changeCurrentLayer(armature.mar_rig_joint_layer, NewRpBone)
    NewRpBone.head = armature.data.edit_bones[BoneName].head
    NewRpBone.tail = armature.data.edit_bones[BoneName].tail
    NewRpBone.roll = armature.data.edit_bones[BoneName].roll
    if custom_rjp_parent != "":
        NewRpBone.parent = armature.data.edit_bones[custom_rjp_parent]
    else:
        NewRpBone.parent = armature.data.edit_bones[BoneName].parent

    if make_it_parent:
        armature.data.edit_bones[BoneName].use_connect = False
        armature.data.edit_bones[BoneName].parent = NewRpBone

    return NewRpBone.name


def setBoneOrentationMode(armature, bone_name, orentation="DEFAULT"):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    if orentation == "DEFAULT":
        pass
    elif orentation == "UP":
        rjp_bone = bbpl.rig_utils.createRpBone(armature, bone_name, make_it_parent=False, custom_rjp_parent=bone_name)

        edit_bone_dup = armature.data.edit_bones[bone_name]
        length = edit_bone_dup.length
        edit_bone_dup.tail = edit_bone_dup.head + mathutils.Vector((0.0, 0.0, 1.0))
        edit_bone_dup.roll = 0
        setBoneLength(armature, bone_name, length)

        bpy.ops.object.mode_set(mode='POSE')

        armature.pose.bones[bone_name].custom_shape_transform = armature.pose.bones[rjp_bone]
        # Remap deform bone
        for bone in armature.pose.bones:
            if armature.data.bones[bone.name].layers[armature.mar_deform_layer]:
                for con in bone.constraints:
                    if con.name == "DeformRetargeting":
                        if con.subtarget == bone_name:
                            con.subtarget = rjp_bone

        bpy.ops.object.mode_set(mode='EDIT')

        return rjp_bone
    else:
        print("Error in setBoneOrentationMode() "+orentation+" not found!")


class BoneDataSave():
    def __init__(self, armature, saved_bone):
        self.name = saved_bone.name
        self.parent = saved_bone.parent.name
        self.childs = []
        for bone in armature:
            if bone.parent is not None:
                if bone.parent == saved_bone:
                    self.childs.append(bone)


def generateFollowList(
        armature, follow_List, follow_Default,
        BoneName,
        BoneWithConst,
        BoneWithProperty,
        UseRotOnly=False
        ):

    follow_Default_found = False
    for Follow in follow_List:
        value = 0.0
        if Follow == follow_Default:
            follow_Default_found = True
            value = 1.0
        addBoneFollow(
            armature=armature,
            bone_name=BoneName,
            bone_with_const=BoneWithConst,
            bone_with_property=BoneWithProperty,
            target_bone=Follow,
            default_property=value,
            property_name="Follow_"+Follow,
            use_rot_only=UseRotOnly
            )

    if not follow_Default_found:
        if follow_Default:
            print("Follow Default not found! "+follow_Default)
            raise TypeError("Follow Default not found! "+follow_Default)
        else:
            print("Follow Default is None!")
            raise TypeError("Follow Default is None!")


def generateFollowListWithValues(
        armature,
        follow_List,
        follow_Default_List,
        BoneName,
        BoneWithConst,
        BoneWithProperty,
        UseRotOnly=False
        ):

    follow_Default_found = False
    for x, Follow in enumerate(follow_List):
        value = follow_Default_List[x]
        addBoneFollow(
            armature=armature,
            bone_name=BoneName,
            bone_with_const=BoneWithConst,
            bone_with_property=BoneWithProperty,
            target_bone=Follow,
            default_property=value,
            property_name="Follow_"+Follow,
            use_rot_only=UseRotOnly
            )


def addBoneFollow(
        armature,
        bone_name,
        bone_with_const,
        bone_with_property,
        target_bone,
        default_property=0.0,
        property_name="Follow",
        use_rot_only=False
        ):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    # CreationOs
    FollowBone = armature.data.edit_bones.new(rjp+"follow_"+target_bone+"_"+bone_name)
    changeCurrentLayer(armature.mar_rig_joint_layer, FollowBone)
    FollowBone.head = armature.data.edit_bones[bone_name].head
    FollowBone.tail = armature.data.edit_bones[bone_name].tail
    FollowBone.roll = armature.data.edit_bones[bone_name].roll
    FollowBone.parent = armature.data.edit_bones[target_bone]
    FollowBoneName = FollowBone.name

    # Creation des contraintes copy transform

    bpy.ops.object.mode_set(mode='POSE')
    if use_rot_only:
        constraint = armature.pose.bones[bone_with_const].constraints.new("COPY_ROTATION")
        constraint.target = armature
        constraint.subtarget = FollowBoneName
        constraint.name = property_name+"_"+target_bone+"_Transfom"
    else:
        constraint = armature.pose.bones[bone_with_const].constraints.new('COPY_TRANSFORMS')
        constraint.target = armature
        constraint.subtarget = FollowBoneName
        constraint.name = property_name+"_"+target_bone+"_Transfom"

    # Gestion des driver
    createCustomProperty(
        armature=armature,
        property_bone_name=bone_with_property,
        property_name=property_name,
        default=default_property,
        min=0.0,
        max=1.0,
        description='..',
        overridable=True)

    d = armature.driver_add('pose.bones["'+bone_with_const+'"].constraints["'+constraint.name+'"].influence').driver
    setDriver(armature, d, bone_with_property, property_name)

    bpy.ops.object.mode_set(mode='EDIT')
    return FollowBoneName


def getRigModifiers(armature, class_name, use_only=True):
    modifiers = []
    for mod in armature.MAR_ConstructModifiers:
        if mod.rigClassType == class_name:
            if mod.use or not use_only:
                if mod.isValid():
                    modifiers.append(mod)
                else:
                    print(mod.name + "not valid")
    return modifiers


def getFirstParent(bone):
    if bone.parent:
        return getFirstParent(bone.parent)
    else:
        return bone


def createSimpleStretch(armature, Bone, TargetBoneName, Name):

    bpy.ops.object.mode_set(mode='POSE')
    constraint = armature.pose.bones[Bone].constraints.new('STRETCH_TO')
    constraint.target = armature
    constraint.subtarget = TargetBoneName
    constraint.name = Name
    bpy.ops.object.mode_set(mode='EDIT')
    constraint.rest_length = (
        armature.data.edit_bones[TargetBoneName].head - armature.data.edit_bones[Bone].tail
        ).length


class DriverPropertyHelpper():
    def __init__(self, armature, bone_const_name, constraint_name, name="NoPropertyName"):
        self.armature = armature
        self.bone_const_name = bone_const_name
        self.constraint_name = constraint_name
        self.description = ""
        self.property_name = name
        self.default = 0.0
        self.min = 0.0
        self.max = 1.0

    def ApplyDriver(self, bone_name, constraint):
        if not (self.bone_const_name or self.constraint_name):
            print("bone_const_name or constraint_name not set!")
            return

        createCustomProperty(
            armature=self.armature,
            property_bone_name=bone_name,
            property_name=self.property_name,
            default=self.default,
            min=self.min,
            max=self.max,
            description=self.description,
            overridable=True)

        driver_value = 'pose.bones["'+self.bone_const_name+'"].constraints["'+self.constraint_name+'"].influence'
        d = self.armature.driver_add(driver_value).driver
        setDriver(self.armature, d, bone_name, self.property_name)


def createCustomProperty(
    # return data_path
        armature, property_bone_name, property_name,
        default=0.0, min=0.0, max=1.0, description='..', overridable=True
        ):
    property_bone = armature.pose.bones[property_bone_name]
    property_bone[property_name] = default
    ui_data = property_bone.id_properties_ui(property_name)
    ui_data.update(
        default=default,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        description=description
        )
    property_bone.property_overridable_library_set('["'+property_name+'"]', True)

    return 'pose.bones["'+property_bone_name+'"]["'+property_name+'"]'


def setDriver(armature, driver, boneName, driverName, cleanPrevious=True):
    if cleanPrevious:
        bbpl.utils.clearDriverVar(driver)
    v = driver.variables.new()
    v.name = driverName.replace(" ", "_")
    v.targets[0].id = armature
    v.targets[0].data_path = 'pose.bones["'+boneName+'"]["'+driverName+'"]'
    driver.expression = driverName.replace(" ", "_")
    return v


def getMainRootChain(armature):
    for rootChain in getRigModifiers(armature, "RootChain"):
        return rootChain


def getFirstRootBone(armature):
    rp = armature.mar_rig_prefix
    # Exemple le World
    if getMainRootChain(armature) is not None:
        prop = getMainRootChain(armature)
        rig_bone_list = prop.bone_list.getBoneList_AsRig()
        return rig_bone_list[0]
    else:
        for bone in armature.data.bones:
            if bone.parent is None:
                if bone.name.startswith(rp):
                    return bone.name


def getLastRootBone(armature):
    # Exemple le Fly
    if getMainRootChain(armature) is not None:
        prop = getMainRootChain(armature)
        rig_bone_list = prop.bone_list.getBoneList_AsRig()
        return rig_bone_list[-1]
    else:
        for bone in armature.data.bones:
            if bone.parent is None:
                if bone.name.startswith(rp):
                    return bone.name


def createParentRigPointBone(armature, SourceBone, WillBeTheParent=True, bone_name=None):

    consp = armature.mar_construct_prefix
    dp = armature.mar_deform_prefix
    rp = armature.mar_rig_prefix
    rjp = armature.mar_rig_joint_prefix

    if bone_name:
        RtBone = armature.data.edit_bones.new(bone_name)
    else:
        RtBone = armature.data.edit_bones.new(rjp+"parent_"+SourceBone)

    changeCurrentLayer(armature.mar_rig_joint_layer, RtBone)
    RtBone.head = armature.data.edit_bones[SourceBone].head
    RtBone.tail = armature.data.edit_bones[SourceBone].tail
    RtBone.roll = armature.data.edit_bones[SourceBone].roll
    if WillBeTheParent:
        RtBone.parent = armature.data.edit_bones[SourceBone].parent
        armature.data.edit_bones[SourceBone].parent = RtBone
    else:
        RtBone.parent = armature.data.edit_bones[SourceBone]

    return RtBone.name


def subdiviseOneBone(armature, EditBone, SplitNumber=2, KeepParent=True):
    dp = armature.mar_deform_prefix

    # Vars
    OriginalHead = EditBone.head + mathutils.Vector((0, 0, 0))
    OriginalTail = EditBone.tail + mathutils.Vector((0, 0, 0))

    # Duplication
    Chain = []
    Chain.append(EditBone)
    for x in range(1, SplitNumber):
        dup_bone_name = duplicateBone(armature, EditBone.name, dp+"Twist"+str(x).zfill(2)+"_"+EditBone.name)
        Chain.append(armature.data.edit_bones[dup_bone_name])

    if not KeepParent:
        # Reparentage des enfant au la queue de la chaine
        for bone in armature.data.edit_bones:
            if bone.parent == EditBone:
                bone.parent = Chain[-1]

    # Replacement des os
    BoneRootPos = EditBone.head
    vectorLength = EditBone.tail - EditBone.head
    for x, bone in enumerate(Chain):
        if KeepParent:
            # bone.use_connect = False
            bone.head = BoneRootPos + (vectorLength/SplitNumber)*x
            bone.tail = BoneRootPos + (vectorLength/(SplitNumber))*(x+1)
            # bone.head = mathutils.Vector((0,0,0))
            bone.tail = OriginalTail
        else:
            bone.head = BoneRootPos + (vectorLength/SplitNumber)*x
            bone.tail = BoneRootPos + (vectorLength/(SplitNumber))*(x+1)

        if x > 0:
            bone.parent = Chain[x-1]
            if not KeepParent:
                bone.use_connect = True

    # Reparentage final
    return Chain


def duplicateBone(armature, bone_name, new_name=None):
    editBone = armature.data.edit_bones[bone_name]
    if new_name is None:
        new_name = editBone.name+"_dup"
    newBone = armature.data.edit_bones.new(new_name)
    newBone.head = editBone.head
    newBone.tail = editBone.tail
    newBone.roll = editBone.roll
    newBone.inherit_scale = editBone.inherit_scale

    newBone.parent = editBone.parent
    newBone.layers = editBone.layers

    return newBone.name


def copyContraint(armature, copy_bone_name, paste_bone_name, clear=True):
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


def getLayerByName(armature, name: str):
    if name == armature.mar_rig_layer_label_a:
        return armature.mar_rig_layer_a
    elif name == armature.mar_rig_layer_label_b:
        return armature.mar_rig_layer_b
    elif name == armature.mar_rig_layer_label_c:
        return armature.mar_rig_layer_c
    elif name == armature.mar_rig_layer_label_d:
        return armature.mar_rig_layer_d
    elif name == armature.mar_rig_layer_label_e:
        return armature.mar_rig_layer_e
    elif name == armature.mar_rig_layer_label_f:
        return armature.mar_rig_layer_f
    elif name == armature.mar_rig_layer_label_g:
        return armature.mar_rig_layer_g
    elif name == armature.mar_rig_layer_label_h:
        return armature.mar_rig_layer_h
    else:
        return 0


def getBoneInRigLayer(armature, bone_name):
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_a]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_b]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_c]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_d]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_e]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_f]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_g]:
        return True
    if armature.data.bones[bone_name].layers[armature.mar_rig_layer_h]:
        return True
    return False


def getRigLayers(armature):
    layers = []
    layers.append(armature.mar_rig_layer_a)
    layers.append(armature.mar_rig_layer_b)
    layers.append(armature.mar_rig_layer_c)
    layers.append(armature.mar_rig_layer_d)
    layers.append(armature.mar_rig_layer_e)
    layers.append(armature.mar_rig_layer_f)
    layers.append(armature.mar_rig_layer_g)
    layers.append(armature.mar_rig_layer_h)
    return layers
