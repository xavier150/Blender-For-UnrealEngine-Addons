# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Tuple


from .. import bfu_anim_action
from ..bfu_anim_action.bfu_anim_action_props import BFU_AnimActionStartEndTimeEnum

def get_desired_action_start_end_range(obj: bpy.types.Object, action: bpy.types.Action)-> Tuple[float, float]:
    # Returns desired action or camera anim start/end time
    scene = bpy.context.scene
    if scene is None:
        raise Exception("No active scene found")

    if bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_end_time_enum(obj) == BFU_AnimActionStartEndTimeEnum.WITH_KEYFRAMES:
        # GetFirstActionFrame + Offset
        startTime = int(action.frame_range.x) + bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_frame_offset(obj)
        # GetLastActionFrame + Offset
        endTime = int(action.frame_range.y) + bfu_anim_action.bfu_anim_action_props.get_object_anim_action_end_frame_offset(obj)
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_end_time_enum(obj) == BFU_AnimActionStartEndTimeEnum.WITH_SCENEFRAMES:
        startTime = scene.frame_start + bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_frame_offset(obj)
        endTime = scene.frame_end + bfu_anim_action.bfu_anim_action_props.get_object_anim_action_end_frame_offset(obj)
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)

    elif bfu_anim_action.bfu_anim_action_props.get_object_anim_action_start_end_time_enum(obj) == BFU_AnimActionStartEndTimeEnum.WITH_CUSTOMFRAMES:
        startTime = bfu_anim_action.bfu_anim_action_props.get_object_anim_action_custom_start_frame(obj)
        endTime = bfu_anim_action.bfu_anim_action_props.get_object_anim_action_custom_end_frame(obj)
        if endTime <= startTime:
            endTime = startTime+1
        return (startTime, endTime)
    
    else:
        raise Exception("Unknown BFU_AnimActionStartEndTimeEnum")
    
def action_is_one_frame(action: bpy.types.Action) -> bool:
    # return True if action is one frame
    return action.frame_range.y - action.frame_range.x == 0