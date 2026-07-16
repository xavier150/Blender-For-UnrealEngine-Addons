# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy

from .. import bfu_adv_object
from . import bfu_anim_nla_adv_props

def apply_nla_export_transform(obj: bpy.types.Object):
    move_to_center = bfu_anim_nla_adv_props.get_object_move_nla_to_center_for_export(obj)
    rotate_to_zero = bfu_anim_nla_adv_props.get_object_rotate_nla_to_zero_for_export(obj)
    bfu_adv_object.bfu_adv_obj_utils.apply_export_transform(obj, move_to_center, rotate_to_zero)