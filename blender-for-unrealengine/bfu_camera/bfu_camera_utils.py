import bpy

def get_enum_cameras_list():
    camera_types = [
        ("REGULAR", "Regular", "Regular camera, for standard gameplay views."),
        ("CINEMATIC", "Cinematic", "The Cine Camera Actor is a specialized Camera Actor with additional settings that replicate real-world film camera behavior. You can use the Filmback, Lens, and Focus settings to create realistic scenes, while adhering to industry standards."),
        ("ARCHVIS", "ArchVis", "Support for ArchVis Tools Cameras."),
        ("CUSTOM", "Custom", "If you use an custom camera actor."),
    ]
    return camera_types



def get_enum_cameras_default():
    return "CINEMATIC"

