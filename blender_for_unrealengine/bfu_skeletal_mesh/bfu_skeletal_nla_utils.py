# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Tuple
from .. import bfu_anim_nla
from ..bfu_anim_nla.bfu_anim_nla_props import BFU_AnimNLAStartEndTimeEnum


def get_desired_nla_start_end_range(obj: bpy.types.Object) -> Tuple[float, float]:
    # Returns desired nla anim start/end time
    scene = bpy.context.scene
    if scene is None:
        raise Exception("No active scene found")

    if bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_start_end_time_enum(obj).value == BFU_AnimNLAStartEndTimeEnum.WITH_SCENEFRAMES.value:
        startTime = scene.frame_start + bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_start_frame_offset(obj)
        endTime = scene.frame_end + bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_end_frame_offset(obj)
        if endTime <= startTime:
            endTime = startTime

        return (startTime, endTime)

    elif bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_start_end_time_enum(obj).value == BFU_AnimNLAStartEndTimeEnum.WITH_CUSTOMFRAMES.value:
        startTime = bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_custom_start_frame(obj)
        endTime = bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_custom_end_frame(obj)
        if endTime <= startTime:
            endTime = startTime

        return (startTime, endTime)
    
    else:
        raise Exception("Unknown BFU_AnimNLAStartEndTimeEnum")
