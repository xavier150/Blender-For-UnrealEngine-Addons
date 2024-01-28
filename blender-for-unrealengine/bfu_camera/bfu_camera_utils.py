import bpy

from . import bfu_camera_write_text

def GetImportCameraScriptCommand(objs, CineCamera=True):
    # Return (success, command)

    success = False
    command = ""
    report = ""
    add_camera_num = 0

    def AddCameraToCommand(camera):
        if camera.type == "CAMERA":
            t = ""
            # Get Camera Data
            scene = bpy.context.scene
            frame_current = scene.frame_current

            # First I get the camera data.
            # This is a very bad way to do this. I need do a new python file specific to camera with class to get data.
            data = bfu_camera_write_text.WriteOneFrameCameraAnimationTracks(camera, frame_current)
            transform_track = data["Camera transform"][frame_current]
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
            if CineCamera:
                t += "      " + "Begin Actor Class=/Script/CinematicCamera.CineCameraActor Name="+CameraName+" Archetype=/Script/CinematicCamera.CineCameraActor'/Script/CinematicCamera.Default__CineCameraActor'" + "\n"
            else:
                t += "      " + "Begin Actor Class=/Script/Engine.CameraActor Name="+CameraName+" Archetype=/Script/Engine.CameraActor'/Script/Engine.Default__CameraActor'" + "\n"

            # Init SceneComponent
            if CineCamera:
                t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/CinematicCamera.Default__CineCameraActor:SceneComponent'" + "\n"
                t += "         " + "End Object" + "\n"
            else:
                t += "         " + "Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'/Script/Engine.Default__CameraActor:SceneComponent'" + "\n"
                t += "         " + "End Object" + "\n"

            # Init CameraComponent
            if CineCamera:
                t += "         " + "Begin Object Class=/Script/CinematicCamera.CineCameraComponent Name=\"CameraComponent\" Archetype=/Script/CinematicCamera.CineCameraComponent'/Script/CinematicCamera.Default__CineCameraActor:CameraComponent'" + "\n"
                t += "         " + "End Object" + "\n"
            else:
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

    cameras = []
    for obj in objs:
        if obj.type == "CAMERA":
            cameras.append(obj)

    if len(cameras) == 0:
        report = "Please select at least one camera."
        return (success, command, report)

    # And I apply the camrta data to the copy paste text.
    t = "Begin Map" + "\n"
    t += "   " + "Begin Level" + "\n"
    for camera in cameras:
        add_command = AddCameraToCommand(camera)
        if add_command:
            t += add_command
            add_camera_num += 1

    t += "   " + "End Level" + "\n"
    t += "Begin Surface" + "\n"
    t += "End Surface" + "\n"
    t += "End Object" + "\n"

    success = True
    command = t
    if CineCamera:
        report = str(add_camera_num)+" Cine camera(s) copied. Paste in Unreal Engine scene for import the camera. (Ctrl+V)"
    else:
        report = str(add_camera_num)+" Regular camera(s) copied. Paste in Unreal Engine scene for import the camera. (Ctrl+V)"

    return (success, command, report)