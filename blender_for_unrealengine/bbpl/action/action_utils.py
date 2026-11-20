# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from typing import Iterable, List, Optional, cast

import bpy
from bpy_extras import anim_utils


def get_used_actions(obj: bpy.types.Object) -> List[bpy.types.Action]:
    """Return the active action and all actions referenced by the object's NLA strips."""
    animation_data = obj.animation_data
    if animation_data is None:
        return []
    actions: List[bpy.types.Action] = []
    if animation_data.action is not None:
        actions.append(animation_data.action)

    def collect_strips(strips: Iterable[bpy.types.NlaStrip]) -> None:
        for strip in strips:
            if strip.action is not None and strip.action not in actions:
                actions.append(strip.action)
            if strip.type == 'META':
                collect_strips(strip.strips)

    for track in animation_data.nla_tracks:
        collect_strips(track.strips)
    return actions


def _fcurves_match_armature(
    obj: bpy.types.Object,
    fcurves: List[bpy.types.FCurve],
) -> bool:
    if not isinstance(obj.data, bpy.types.Armature):
        return False

    for fcurve in fcurves:
        data_path = fcurve.data_path
        start = data_path.find('["')
        end = data_path.rfind('"]')
        if start > 0 and end > 0:
            bone_name = data_path[start + 2:end]
            if bone_name in obj.data.bones:
                return True

    return False


def get_relevant_actions(objs: List[bpy.types.Object]) -> List[bpy.types.Action]:
    """Return local actions that animate bones on at least one supplied armature."""
    relevant_actions: List[bpy.types.Action] = []

    for obj in objs:
        if not isinstance(obj.data, bpy.types.Armature):
            continue

        for action in bpy.data.actions:
            if action.library:
                continue

            if bpy.app.version >= (4, 4, 0):
                if obj.animation_data is None:
                    continue

                slot_identifier = obj.animation_data.last_slot_identifier
                if slot_identifier not in action.slots:
                    continue

                slot = action.slots[slot_identifier]
                channel_bag = cast(
                    Optional[bpy.types.ActionChannelbag],
                    anim_utils.action_get_channelbag_for_slot(action, slot),  # type: ignore
                )
                if channel_bag is None:
                    continue
                fcurves = channel_bag.fcurves
            else:
                fcurves = action.fcurves

            if _fcurves_match_armature(obj, fcurves) and action not in relevant_actions:
                relevant_actions.append(action)

    return relevant_actions
