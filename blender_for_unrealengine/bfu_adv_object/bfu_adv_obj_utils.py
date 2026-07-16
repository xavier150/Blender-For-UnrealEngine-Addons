# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import mathutils

from . import bfu_adv_obj_props

def apply_export_transform(obj: bpy.types.Object, move_to_center: bool = False, rotate_to_zero: bool = False) -> None:

    new_matrix = obj.matrix_world @ mathutils.Matrix.Translation((0, 0, 0))
    saveScale = obj.scale * 1

    if move_to_center:
        mat_trans = mathutils.Matrix.Translation((0, 0, 0))
        mat_rot = new_matrix.to_quaternion().to_matrix()
        new_matrix = mat_trans @ mat_rot.to_4x4()

    obj.matrix_world = new_matrix
    # Turn object to the center of the scene for export
    if rotate_to_zero:
        mat_trans = mathutils.Matrix.Translation(new_matrix.to_translation()) # type: ignore
        mat_rot = mathutils.Matrix.Rotation(0, 4, 'X')
        new_matrix = mat_trans @ mat_rot

    eul = bfu_adv_obj_props.get_object_additional_rotation_for_export(obj)
    loc = bfu_adv_obj_props.get_object_additional_location_for_export(obj)

    mat_rot = eul.to_matrix()
    mat_loc = mathutils.Matrix.Translation(loc) # type: ignore
    add_mattrix_rot = mat_loc @ mat_rot.to_4x4()

    obj.matrix_world = new_matrix @ add_mattrix_rot
    obj.scale = saveScale

def apply_object_export_transform(obj: bpy.types.Object):
    move_to_center = bfu_adv_obj_props.get_object_move_to_center_for_export(obj)
    rotate_to_zero = bfu_adv_obj_props.get_object_rotate_to_zero_for_export(obj)
    apply_export_transform(obj, move_to_center, rotate_to_zero)