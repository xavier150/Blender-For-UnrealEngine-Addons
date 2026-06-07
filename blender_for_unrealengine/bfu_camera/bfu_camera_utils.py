# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Tuple, List, Any
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType

def is_camera(obj: bpy.types.Object) -> bool:
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type(obj) == AssetType.CAMERA:
            return True
    return False

def get_desired_camera_start_end_range(obj: bpy.types.Object)-> Tuple[float, float]:
    # Returns desired action or camera anim start/end time
    
    if not isinstance(obj.data, bpy.types.Camera):
        return (0.0, 1.0)

    scene = bpy.context.scene
    if scene is None:
        raise Exception("No active scene found")
    
    startTime = scene.frame_start
    endTime = scene.frame_end
    if endTime <= startTime:
        endTime = startTime+1
    return (startTime, endTime)


def _get_one_keys_by_action_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame: int, is_data: bool = True) -> Any:  
    # Old method, Blender 4.4 now use layers and action slots.
    if is_data and obj.data is not None:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                f = obj.data.animation_data.action.fcurves.find(data_path)  # type: ignore
                if f:
                    return f.evaluate(frame)  # type: ignore
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                f = obj.animation_data.action.fcurves.find(data_path)  # type: ignore
                if f:
                    return f.evaluate(frame)  # type: ignore
    return data_value

def _get_one_keys_by_action_slots_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame: int, is_data: bool = True) -> Any:
    # Note: I don't understand the logic with layers and stips. 
    # It alway use the index 0 for the both but that may wrong so I loop through all of them and return the first correct value.
    # It that related to NLA? For the moment I keep like this but if you have info and better way to do that don't hesitate to contact me.

    if is_data and obj.data is not None:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                slot_identifier: str = obj.data.animation_data.last_slot_identifier
                if slot_identifier in obj.data.animation_data.action.slots:
                    slot = obj.data.animation_data.action.slots[slot_identifier]
                    for layer in obj.data.animation_data.action.layers:
                        for strip in layer.strips:
                            channelbag = strip.channelbag(slot)
                            f = channelbag.fcurves.find(data_path)
                            if f:
                                return f.evaluate(frame)
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                slot_identifier: str = obj.animation_data.last_slot_identifier
                if slot_identifier in obj.animation_data.action.slots:
                    slot = obj.animation_data.action.slots[slot_identifier]
                    for layer in obj.animation_data.action.layers:
                        for strip in layer.strips:
                            channelbag = strip.channelbag(slot)
                            f = channelbag.fcurves.find(data_path)
                            if f:
                                return f.evaluate(frame)
    return data_value

def _get_all_keys_by_action_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame_start: int, frame_end: int, is_data: bool = True) -> List[Tuple[int, Any]]:
    # Old method, Blender 4.4 now use layers and action slots.
    keys: List[Tuple[int, Any]] = []
    if is_data and obj.data is not None:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                f = obj.data.animation_data.action.fcurves.find(data_path)  # type: ignore
                if f is not None:
                    for frame in range(frame_start, frame_end):
                        v = f.evaluate(frame)  # type: ignore
                        keys.append((frame, v))  # type: ignore
                    return keys
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                f = obj.animation_data.action.fcurves.find(data_path)  # type: ignore
                if f is not None:
                    for frame in range(frame_start, frame_end):
                        v = f.evaluate(frame)  # type: ignore
                        keys.append((frame, v))  # type: ignore
                    return keys
    return[(frame_start, data_value)]

def _get_all_keys_by_action_slots_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame_start: int, frame_end: int, is_data: bool = True) -> List[Tuple[int, Any]]:
    keys: List[Tuple[int, Any]] = []
    if is_data and obj.data is not None:
        if obj.data.animation_data is not None:
            if obj.data.animation_data.action is not None:
                slot_identifier: str = obj.data.animation_data.last_slot_identifier
                if slot_identifier in obj.data.animation_data.action.slots:
                    slot = obj.data.animation_data.action.slots[slot_identifier]
                    for layer in obj.data.animation_data.action.layers:
                        for strip in layer.strips:
                            channelbag = strip.channelbag(slot)
                            f = channelbag.fcurves.find(data_path)
                            if f is not None:
                                for frame in range(frame_start, frame_end):
                                    v = f.evaluate(frame)
                                    keys.append((frame, v))
                                return keys
    else:
        if obj.animation_data is not None:
            if obj.animation_data.action is not None:
                slot_identifier: str = obj.animation_data.last_slot_identifier
                if slot_identifier in obj.animation_data.action.slots:
                    slot = obj.animation_data.action.slots[slot_identifier]
                    for layer in obj.animation_data.action.layers:
                        for strip in layer.strips:
                            channelbag = strip.channelbag(slot)
                            f = channelbag.fcurves.find(data_path)
                            if f is not None:
                                for frame in range(frame_start, frame_end):
                                    v = f.evaluate(frame)
                                    keys.append((frame, v))
                                return keys
    return[(frame_start, data_value)]

def get_one_keys_by_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame: int, is_data: bool = True) -> Any:    
    # The list of slots in this Action was added in Blender 4.4
    if bpy.app.version >= (4, 4, 0):
        return _get_one_keys_by_action_slots_fcurves(obj, data_path, data_value, frame, is_data)
    
    else:
        return _get_one_keys_by_action_fcurves(obj, data_path, data_value, frame, is_data)

def get_all_keys_by_fcurves(obj: bpy.types.Object, data_path: str, data_value: Any, frame_start: int, frame_end: int, is_data: bool = True) -> List[Tuple[int, Any]]:
    # The list of slots in this Action was added in Blender 4.4
    if bpy.app.version >= (4, 4, 0):
        return _get_all_keys_by_action_slots_fcurves(obj, data_path, data_value, frame_start, frame_end, is_data)

    else:
        return _get_all_keys_by_action_fcurves(obj, data_path, data_value, frame_start, frame_end, is_data)