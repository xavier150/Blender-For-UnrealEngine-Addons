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

from .. import bbpl
from .. import bps

import mathutils


def saveDefomsBones(armature):
    SavedBones = []
    for bone in armature.data.bones:
        SavedBones.append([bone.name, bone.use_deform])
    return SavedBones


def resetDeformBones(armature, SavedBones):
    for bones in SavedBones:
        armature.data.bones[bones[0]].use_deform = bones[1]


def setAllBonesDeforms(armature, use_deform):
    for bone in armature.data.bones:
        bone.use_deform = use_deform


def setBonesDeforms(armature, bone_name_list, use_deform):
    bone_list = []

    for bone_name in bone_name_list:
        bone_list.append(armature.data.bones[bone_name])

    for bone in bone_list:
        bone.use_deform = use_deform


def removeVertexGroups(obj):
    for VertexGroup in obj.vertex_groups:
        obj.vertex_groups.remove(VertexGroup)
    return


def copyRigGroup(obj, source):

    # Select
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(state=True)
    bpy.context.view_layer.objects.active = obj

    # Vars
    mod_name = "MAR_RigWeightTransfer"

    # Clean
    for old_mod in obj.modifiers:
        if old_mod.name == mod_name:
            obj.modifiers.remove(old_mod)
    removeVertexGroups(obj)

    mod = obj.modifiers.new(name=mod_name, type='DATA_TRANSFER')

    while obj.modifiers[0].name != mod_name:
        bpy.ops.object.modifier_move_up(modifier=mod_name)

    mod.object = source
    mod.use_vert_data = True
    mod.data_types_verts = {'VGROUP_WEIGHTS'}
    bpy.ops.object.datalayout_transfer(modifier=mod_name, data_type="VGROUP_WEIGHTS")
    return bpy.ops.object.modifier_apply(modifier=mod_name)


def applyAutoRigParent(armature, target, parent_type='ARMATURE_AUTO', use_only_bone_white_list=False, white_list_bones=[], black_list_bones=[]):

    # Select
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(state=True)
    target.select_set(state=True)
    bpy.context.view_layer.objects.active = armature

    if len(white_list_bones) > 0 or len(black_list_bones) > 0:
        save_defom = saveDefomsBones(armature)

        if use_only_bone_white_list:
            setAllBonesDeforms(armature, False)

        # Apply white list
        setBonesDeforms(armature, white_list_bones, True)

        # Apply white list
        setBonesDeforms(armature, black_list_bones, False)

    # Clean
    for modifier in target.modifiers:
        if modifier.type == "ARMATURE":
            target.modifiers.remove(modifier)

    removeVertexGroups(target)
    bpy.ops.object.parent_set(type=parent_type)

    if len(white_list_bones) > 0 or len(black_list_bones) > 0:
        resetDeformBones(armature, save_defom)
