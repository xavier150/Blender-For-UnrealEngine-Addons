# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy

def get_camera_unreal_actor(camera: bpy.types.Object) -> str:
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type  # type: ignore
    if camera_type == "REGULAR":
        return "/Script/Engine.CameraActor"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.CineCameraActor"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.ArchVisCineCameraActor"
    else:
        # Custom camera actor
        return camera.bfu_custom_camera_actor  # type: ignore

def get_camera_unreal_actor_default(camera: bpy.types.Object) -> str:
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type  # type: ignore
    if camera_type == "REGULAR":
        return "/Script/Engine.Default__CameraActor"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.Default__CineCameraActor"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.Default__ArchVisCineCameraActor"
    else:
        # Custom camera actor default
        return camera.bfu_custom_camera_default_actor  # type: ignore

def get_camera_unreal_component(camera: bpy.types.Object) -> str:
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type  # type: ignore
    if camera_type == "REGULAR":
        return "/Script/Engine.CameraComponent"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.CineCameraComponent"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.ArchVisCineCameraComponent"
    else:
        # Custom camera component
        return camera.bfu_custom_camera_component  # type: ignore

def get_camera_unreal_projection(camera: bpy.types.Object) -> str:
    # Engin ref:
    camera_type = camera.data.type  # type: ignore
    if camera_type == "PERSP":
        return "Perspective"
    elif camera_type == "ORTHO":
        return "Orthographic"
    elif camera_type == "PANO":
        # Panoramic is not yet supported native in Unreal Engine.
        return "Perspective"
    else:
        print(f"Warning: Unsupported camera type '{camera_type}' for Unreal Engine export.")
        return "Perspective"