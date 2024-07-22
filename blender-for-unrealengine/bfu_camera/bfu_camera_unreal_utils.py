import bpy

def get_camera_unreal_actor(camera: bpy.types.Object):
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type
    if camera_type == "REGULAR":
        return "/Script/Engine.CameraActor"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.CineCameraActor"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.ArchVisCineCameraActor"
    elif camera_type == "CUSTOM":
        return camera.bfu_custom_camera_actor

def get_camera_unreal_actor_default(camera: bpy.types.Object):
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type
    if camera_type == "REGULAR":
        return "/Script/Engine.Default__CameraActor"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.Default__CineCameraActor"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.Default__ArchVisCineCameraActor"
    elif camera_type == "CUSTOM":
        return camera.bfu_custom_camera_default_actor

def get_camera_unreal_component(camera: bpy.types.Object):
    # Engin ref:
    camera_type = camera.bfu_desired_camera_type
    if camera_type == "REGULAR":
        return "/Script/Engine.CameraComponent"
    elif camera_type == "CINEMATIC":
        return "/Script/CinematicCamera.CineCameraComponent"
    elif camera_type == "ARCHVIS":
        return "/Script/ArchVisTools.ArchVisCineCameraComponent"
    elif camera_type == "CUSTOM":
        return camera.bfu_custom_camera_component
    
def get_camera_unreal_projection(camera: bpy.types.Object):
    # Engin ref:
    camera_type = camera.data.type
    if camera_type == "PERSP":
        return "Perspective"
    elif camera_type == "ORTHO":
        return "Orthographic"
    elif camera_type == "PANO":
        # Panoramic is not yet supported native in Unreal Engine.
        return "Perspective"