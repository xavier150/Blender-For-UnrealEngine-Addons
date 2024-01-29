import bpy

from . import bfu_camera_write_text
from . import bfu_camera_data
from .. import languages

def get_enum_cameras_list():
    camera_types = [
        ("REGULAR", "Regular", "Regular camera, for standard gameplay views."),
        ("CINEMATIC", "Cinematic", "The Cine Camera Actor is a specialized Camera Actor with additional settings that replicate real-world film camera behavior. You can use the Filmback, Lens, and Focus settings to create realistic scenes, while adhering to industry standards."),
    ]
    return camera_types

def get_enum_cameras_default():
    return "CINEMATIC"

def AddCameraToCommand(camera: bpy.types.Object, pre_bake_camera: bfu_camera_data.BFU_CameraTracks = None):
    if camera.type == "CAMERA":
        camera_type = camera.bfu_desired_camera_type

        t = ""
        # Get Camera Data
        scene = bpy.context.scene
        frame_current = scene.frame_current

        # First I get the camera data.
        # This is a very bad way to do this. I need do a new python file specific to camera with class to get data.
        data = bfu_camera_write_text.WriteOneFrameCameraAnimationTracks(camera, frame_current, pre_bake_camera)
        transform_track = data["Camera Transform"][frame_current]
        location_x = transform_track["location_x"]
        location_y = transform_track["location_y"]
        location_z = transform_track["location_z"]
        rotation_x = transform_track["rotation_x"]
        rotation_y = transform_track["rotation_y"]
        rotation_z = transform_track["rotation_z"]
        scale_x = transform_track["scale_x"]
        scale_y = transform_track["scale_y"]
        scale_z = transform_track["scale_z"]
        NearClippingPlane = data["Camera NearClippingPlane"][frame_current]
        FarClippingPlane = data["Camera FarClippingPlane"][frame_current]
        FieldOfView = data["Camera FieldOfView"][frame_current]
        FocalLength = data["Camera FocalLength"][frame_current]
        SensorWidth = data["Camera SensorWidth"][frame_current]
        SensorHeight = data["Camera SensorHeight"][frame_current]
        FocusDistance = data["Camera FocusDistance"][frame_current]
        Aperture = data["Camera Aperture"][frame_current]
        AspectRatio = data["desired_screen_ratio"]
        CameraName = camera.name

        # Actor
        if camera_type == "CINEMATIC":
            t += "      " + "Begin Actor Class=/Script/CinematicCamera.CineCameraActor Name="+CameraName+" Archetype=/Script/CinematicCamera.CineCameraActor'/Script/CinematicCamera.Default__CineCameraActor'" + "\n"
        elif camera_type == "REGULAR":
            t += "      " + "Begin Actor Class=/Script/Engine.CameraActor Name="+CameraName+" Archetype=/Script/Engine.CameraActor'/Script/Engine.Default__CameraActor'" + "\n"

        # Init SceneComponent
        if camera_type == "CINEMATIC":
            t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/CinematicCamera.Default__CineCameraActor:SceneComponent'" + "\n"
            t += "         " + "End Object" + "\n"
        elif camera_type == "REGULAR":
            t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/Engine.Default__CameraActor:SceneComponent'" + "\n"
            t += "         " + "End Object" + "\n"

        # Init CameraComponent
        if camera_type == "CINEMATIC":
            t += "         " + "Begin Object Class=/Script/CinematicCamera.CineCameraComponent Name=\"CameraComponent\" Archetype=/Script/CinematicCamera.CineCameraComponent'/Script/CinematicCamera.Default__CineCameraActor:CameraComponent'" + "\n"
            t += "         " + "End Object" + "\n"
        elif camera_type == "REGULAR":
            t += "         " + "Begin Object Class=/Script/Engine.CameraComponent Name=\"CameraComponent\" Archetype=/Script/Engine.CameraComponent'/Script/Engine.Default__CameraActor:CameraComponent'" + "\n"
            t += "         " + "End Object" + "\n"

        # SceneComponent
        t += "         " + "Begin Object Name=\"SceneComponent\"" + "\n"
        t += "            " + "RelativeLocation=(X="+str(location_x)+",Y="+str(location_y)+",Z="+str(location_z)+")" + "\n"
        t += "            " + "RelativeRotation=(Pitch="+str(rotation_y)+",Yaw="+str(rotation_z)+",Roll="+str(rotation_x)+")" + "\n"
        t += "            " + "RelativeScale3D=(X="+str(scale_x)+",Y="+str(scale_y)+",Z="+str(scale_z)+")" + "\n"
        t += "         " + "End Object" + "\n"

        # CameraComponent
        t += "         " + "Begin Object Name=\"CameraComponent\"" + "\n"
        t += "            " + "Filmback=(SensorWidth="+str(SensorWidth)+",SensorHeight="+str(SensorHeight)+", SensorAspectRatio="+str(AspectRatio)+")" + "\n"
        t += "            " + "FocusSettings=(ManualFocusDistance="+str(FocusDistance)+")" + "\n"
        t += "            " + "CurrentFocalLength="+str(FocalLength)+")" + "\n"
        t += "            " + "CurrentAperture="+str(Aperture)+")" + "\n"
        t += "            " + "CurrentFocusDistance="+str(FocusDistance)+")" + "\n"
        t += "            " + "CustomNearClippingPlane="+str(NearClippingPlane)+")" + "\n"
        t += "            " + "CustomFarClippingPlane="+str(FarClippingPlane)+")" + "\n"
        t += "            " + "FieldOfView="+str(FieldOfView)+")" + "\n"
        t += "            " + "AspectRatio="+str(AspectRatio)+")" + "\n"
        t += "         " + "End Object" + "\n"

        # Attach
        t += "         " + "CameraComponent=\"CameraComponent\"" + "\n"
        t += "         " + "SceneComponent=\"SceneComponent\"" + "\n"
        t += "         " + "RootComponent=\"SceneComponent\"" + "\n"
        t += "         " + "ActorLabel=\""+CameraName+"\"" + "\n"

        # Close
        t += "      " + "End Actor" + "\n"
        return t
    return None

def GetImportCameraScriptCommand(objs):
    # Return (success, command)
    scene = bpy.context.scene
    frame_current = scene.frame_current

    success = False
    command = ""
    report = ""
    add_camera_num = 0

    cameras = []
    for obj in objs:
        if obj.type == "CAMERA":
            cameras.append(obj)

    if len(cameras) == 0:
        report = "Please select at least one camera."
        return (success, command, report)

    pre_bake_camera = bfu_camera_data.BFU_MultiCameraTracks()
    pre_bake_camera.set_start_end_frames(frame_current, frame_current+1)
    for camera in cameras:
        pre_bake_camera.add_camera_to_evaluate(camera)
    pre_bake_camera.evaluate_all_cameras(True)

    # And I apply the camrta data to the copy paste text.
    t = "Begin Map" + "\n"
    t += "   " + "Begin Level" + "\n"


    for camera in cameras:
        add_command = AddCameraToCommand(camera, pre_bake_camera.get_evaluate_camera_data(obj))
        if add_command:
            t += add_command
            add_camera_num += 1

    t += "   " + "End Level" + "\n"
    t += "Begin Surface" + "\n"
    t += "End Surface" + "\n"
    t += "End Object" + "\n"

    success = True
    command = t
    report = str(add_camera_num) + " Camera(s) copied. Paste in Unreal Engine scene for import the camera. (Use CTRL+V in Unreal viewport)"

    return (success, command, report)