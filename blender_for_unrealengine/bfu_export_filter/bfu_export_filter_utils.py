# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from . import bfu_export_filter_props

def get_use_static_export() -> bool: 
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_static_export(scene) # type: ignore
    return False

def get_use_static_collection_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_static_collection_export(scene) # type: ignore
    return False

def get_use_skeletal_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_skeletal_export(scene) # type: ignore
    return False

def get_use_animation_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_animation_export(scene) # type: ignore
    return False

def get_use_alembic_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_alembic_export(scene) # type: ignore
    return False

def get_use_groom_simulation_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_groom_simulation_export(scene) # type: ignore
    return False

def get_use_camera_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_camera_export(scene) # type: ignore
    return False

def get_use_spline_export() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_spline_export(scene) # type: ignore
    return False

def get_use_text_export_log() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_text_export_log(scene) # type: ignore
    return False

def get_use_text_import_asset_script() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_text_import_asset_script(scene) # type: ignore
    return False

def get_use_text_import_sequence_script() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_text_import_sequence_script(scene) # type: ignore
    return False

def get_use_text_additional_data() -> bool:
    scene = bpy.context.scene
    if  scene:
        return bfu_export_filter_props.scene_use_text_additional_data(scene) # type: ignore
    return False
