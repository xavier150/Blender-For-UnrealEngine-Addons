import bpy

from . import bfu_camera_data
from . import bfu_camera_unreal_utils
from . import bfu_camera_write_text



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
        transform_track = data["ue_camera_transform"][frame_current]
        location_x = transform_track["location_x"]
        location_y = transform_track["location_y"]
        location_z = transform_track["location_z"]
        rotation_x = transform_track["rotation_x"]
        rotation_y = transform_track["rotation_y"]
        rotation_z = transform_track["rotation_z"]
        scale_x = transform_track["scale_x"]
        scale_y = transform_track["scale_y"]
        scale_z = transform_track["scale_z"]
        NearClippingPlane = data["camera_near_clipping_plane"][frame_current]
        FarClippingPlane = data["camera_far_clipping_plane"][frame_current]
        FieldOfView = data["camera_field_of_view"][frame_current]
        FocalLength = data["camera_focal_length"][frame_current]
        SensorWidth = data["ue_camera_sensor_width"][frame_current]
        SensorHeight = data["ue_camera_sensor_height"][frame_current]
        MinFStop = data["ue_lens_minfstop"]
        MaxFStop = data["ue_lens_maxfstop"]
        FocusDistance = data["camera_focus_distance"][frame_current]
        Aperture = data["camera_aperture"][frame_current]
        AspectRatio = data["desired_screen_ratio"]
        ProjectionMode = data["ue_projection_mode"]
        OrthoWidth = data["ortho_scale"]
        CameraName = camera.name

        # Engin ref:
        target_camera_actor = bfu_camera_unreal_utils.get_camera_unreal_actor(camera)
        target_camera_actor_default = bfu_camera_unreal_utils.get_camera_unreal_actor_default(camera)
        target_camera_component = bfu_camera_unreal_utils.get_camera_unreal_component(camera)

        # Actor
        t += "      " + f"Begin Actor Class={target_camera_actor} Name={CameraName} Archetype={target_camera_actor}'{target_camera_actor_default}'" + "\n"

        # Init SceneComponent
        t += "         " + f"Begin Object Class=/Script/Engine.SceneComponent Name=\"SceneComponent\" Archetype=/Script/Engine.SceneComponent'{target_camera_actor_default}:SceneComponent'" + "\n"
        t += "         " + "End Object" + "\n"

        # Init CameraComponent
        t += "         " + f"Begin Object Class={target_camera_component} Name=\"CameraComponent\" Archetype={target_camera_component}'{target_camera_actor_default}:CameraComponent'" + "\n"
        t += "         " + "End Object" + "\n"

        # SceneComponent
        t += "         " + "Begin Object Name=\"SceneComponent\"" + "\n"
        t += "            " + "RelativeLocation=(X="+str(location_x)+",Y="+str(location_y)+",Z="+str(location_z)+")" + "\n"
        t += "            " + "RelativeRotation=(Pitch="+str(rotation_y)+",Yaw="+str(rotation_z)+",Roll="+str(rotation_x)+")" + "\n"
        t += "            " + "RelativeScale3D=(X="+str(scale_x)+",Y="+str(scale_y)+",Z="+str(scale_z)+")" + "\n"
        t += "         " + "End Object" + "\n"

        # CameraComponent
        t += "         " + "Begin Object Name=\"CameraComponent\"" + "\n"
        if camera_type == "ARCHVIS":
            arch_projection_shift = pre_bake_camera.arch_projection_shift[frame_current]
            shift_x = arch_projection_shift["x"]
            shift_y = arch_projection_shift["y"]
            t += "            " + f"ProjectionOffset=(X={shift_x}, Y={shift_y})" + "\n"
            t += "            " + f"FinalProjectionOffset=(X={shift_x}, Y={shift_y})" + "\n"
            t += "            " + "bCorrectPerspective=False" + "\n"
        t += "            " + "Filmback=(SensorWidth="+str(SensorWidth)+",SensorHeight="+str(SensorHeight)+", SensorAspectRatio="+str(AspectRatio)+")" + "\n"
        t += "            " + "LensSettings=(MinFStop="+str(MinFStop)+",MaxFStop="+str(MaxFStop)+")" + "\n"
        t += "            " + "FocusSettings=(ManualFocusDistance="+str(FocusDistance)+")" + "\n"
        t += "            " + "CurrentFocalLength="+str(FocalLength)+")" + "\n"
        t += "            " + "CurrentAperture="+str(Aperture)+")" + "\n"
        t += "            " + "CurrentFocusDistance="+str(FocusDistance)+")" + "\n"
        t += "            " + "CustomNearClippingPlane="+str(NearClippingPlane)+")" + "\n"
        t += "            " + "CustomFarClippingPlane="+str(FarClippingPlane)+")" + "\n"
        t += "            " + "FieldOfView="+str(FieldOfView)+")" + "\n"
        t += "            " + "AspectRatio="+str(AspectRatio)+")" + "\n"
        t += "            " + "ProjectionMode="+str(ProjectionMode)+")" + "\n"
        t += "            " + "OrthoWidth="+str(OrthoWidth)+")" + "\n"
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
        add_command = AddCameraToCommand(camera, pre_bake_camera.get_evaluate_camera_data(camera))
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