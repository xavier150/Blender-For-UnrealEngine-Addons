# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from enum import Enum
from typing import List, Tuple
import bpy
import math
from .. import bbpl

class BFU_CameraTypeEnum(Enum):
    REGULAR = "REGULAR"
    CINEMATIC = "CINEMATIC"
    ARCHVIS = "ARCHVIS"
    CUSTOM = "CUSTOM"

    @staticmethod
    def default() -> "BFU_CameraTypeEnum":
        return BFU_CameraTypeEnum.CINEMATIC

def get_cameras_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_CameraTypeEnum.REGULAR.value, 
            "Regular", 
            "Regular camera, for standard gameplay views."),
        (BFU_CameraTypeEnum.CINEMATIC.value, 
            "Cinematic", 
            "The Cine Camera Actor is a specialized Camera Actor with additional settings that replicate real-world film camera behavior. You can use the Filmback, Lens, and Focus settings to create realistic scenes, while adhering to industry standards."),
        (BFU_CameraTypeEnum.ARCHVIS.value, 
            "ArchVis", 
            "Support for ArchVis Tools Cameras."),
        (BFU_CameraTypeEnum.CUSTOM.value, 
            "Custom", 
            "If you use an custom camera actor."),
    ]

def get_default_cameras_enum() -> str:
    return BFU_CameraTypeEnum.default().value

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_fix_axis_flippings',
        'obj.bfu_desired_camera_type',
        'obj.bfu_custom_camera_actor',
        'obj.bfu_custom_camera_default_actor',
        'obj.bfu_custom_camera_component'
        ]
    return preset_values

def get_object_desired_camera_type(obj: bpy.types.Object) -> BFU_CameraTypeEnum:
    return BFU_CameraTypeEnum(obj.bfu_desired_camera_type)  # type: ignore

def get_object_fix_axis_flippings(obj: bpy.types.Object) -> bool:
    return obj.bfu_fix_axis_flippings  # type: ignore

def get_object_fix_axis_flippings_warp_target(obj: bpy.types.Object) -> Tuple[float, float, float]:
    return obj.bfu_fix_axis_flippings_warp_target  # type: ignore





# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bfu_camera_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Camera Properties")  # type: ignore[attr-defined]
    bpy.types.Scene.bfu_camera_tools_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Camera")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_fix_axis_flippings = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Fix Camera Axis",
        description=('Enable this option to fix axis flipping caused by rotation wrapping. '
                    'Disable only if you use extreme camera animations in a single frame.'),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )
    bpy.types.Object.bfu_fix_axis_flippings_warp_target = bpy.props.FloatVectorProperty(  # type: ignore[attr-defined]
        name="Fix Camera Axis Warp Target",
        description=('Target rotation values (in degrees) used to fix camera axis wrapping issues.'),
        override={'LIBRARY_OVERRIDABLE'},
        default=(math.radians(360.0), math.radians(360.0), math.radians(360.0)),  # Convert to radians
        subtype='EULER'
        )
    bpy.types.Object.bfu_desired_camera_type = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Camera Type",
        description="Choose the type of camera",
        items=get_cameras_enum_list(),
        default=get_default_cameras_enum()
    )
    bpy.types.Object.bfu_custom_camera_actor = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Custom Camera Actor",
        description=('Ref adress for an custom camera actor'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.MyCameraActor",
        )
    bpy.types.Object.bfu_custom_camera_default_actor = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Custom Camera Actor(default)",
        description=('Ref adress for an custom camera actor (default)'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.Default__MyCameraActor",
        )
    bpy.types.Object.bfu_custom_camera_component = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Custom Camera Component",
        description=('Ref adress for an custom camera component'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/MyModule.MyCameraComponent",
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_custom_camera_component  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_custom_camera_default_actor  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_custom_camera_actor  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_desired_camera_type  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_fix_axis_flippings  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_camera_tools_expanded  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_camera_properties_expanded  # type: ignore[attr-defined]



