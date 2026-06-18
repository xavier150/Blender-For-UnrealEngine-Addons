# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List, Tuple
import bpy
from enum import Enum
from .. import bbpl

class BFU_AnimNLAStartEndTimeEnum(str, Enum):
    WITH_SCENEFRAMES = "with_sceneframes"
    WITH_CUSTOMFRAMES = "with_customframes"

    @staticmethod
    def default() -> "BFU_AnimNLAStartEndTimeEnum":
        return BFU_AnimNLAStartEndTimeEnum.WITH_SCENEFRAMES

    @classmethod
    def _missing_(cls, value: object) -> "BFU_AnimNLAStartEndTimeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_anim_nla_start_end_time_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_AnimNLAStartEndTimeEnum.WITH_SCENEFRAMES,
            "Scene time",
            "Time will be equal to the scene time"),
        (BFU_AnimNLAStartEndTimeEnum.WITH_CUSTOMFRAMES,
            "Custom time",
            'The time of all the animations of this object' +
            ' is defined by you.' +
            ' Use "bfu_anim_nla_custom_start_frame" and "bfu_anim_nla_custom_end_frame"'),
    ]

def get_default_anim_nla_start_end_time_enum() -> str:
    return BFU_AnimNLAStartEndTimeEnum.default().value

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_anim_nla_use',
        'obj.bfu_anim_nla_export_name',
        'obj.bfu_anim_nla_start_end_time_enum',
        'obj.bfu_anim_nla_start_frame_offset',
        'obj.bfu_anim_nla_end_frame_offset',
        'obj.bfu_anim_nla_custom_start_frame',
        'obj.bfu_anim_nla_custom_end_frame',
    ]
    return preset_values

def scene_get_animation_nla_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_animation_nla_properties_expanded.is_expanded()  # type: ignore

def get_object_anim_nla_use(obj: bpy.types.Object) -> bool:
    return obj.bfu_anim_nla_use  # type: ignore

def get_object_anim_nla_export_name(obj: bpy.types.Object) -> str:
    return obj.bfu_anim_nla_export_name  # type: ignore

def get_object_anim_nla_start_end_time_enum(obj: bpy.types.Object) -> BFU_AnimNLAStartEndTimeEnum:
    for item in BFU_AnimNLAStartEndTimeEnum:
        if item.value == obj.bfu_anim_nla_start_end_time_enum:  # type: ignore
            return item

    print(f"Warning: Object {obj.name} has unknown start/end time '{obj.bfu_anim_nla_start_end_time_enum}'. Falling back to default start/end time...")  # type: ignore
    return BFU_AnimNLAStartEndTimeEnum.default()

def get_object_anim_nla_start_frame_offset(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_nla_start_frame_offset  # type: ignore  

def get_object_anim_nla_end_frame_offset(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_nla_end_frame_offset  # type: ignore

def get_object_anim_nla_custom_start_frame(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_nla_custom_start_frame  # type: ignore

def get_object_anim_nla_custom_end_frame(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_nla_custom_end_frame  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_nla_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="NLA Properties")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_anim_nla_use = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Export NLA (Nonlinear Animation)",
        description=(
            "If checked, exports the all animation of the scene with the NLA " +
            "(Don't work with Auto-Rig Pro for the moment.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )
    
    bpy.types.Object.bfu_anim_nla_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="NLA export name",
        description="Export NLA name (Don't work with Auto-Rig Pro for the moment.)",
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="NLA_animation",
        subtype='FILE_NAME'
        )

    bpy.types.Object.bfu_anim_nla_start_end_time_enum = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="NLA Start/End Time",
        description="Set when animation starts and end",
        override={'LIBRARY_OVERRIDABLE'},
        items= get_anim_nla_start_end_time_enum_list(),
        default= get_default_anim_nla_start_end_time_enum()
        )
    
    bpy.types.Object.bfu_anim_nla_start_frame_offset = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Offset at start frame",
        description="Offset for the start frame.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_nla_end_frame_offset = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Offset at end frame",
        description=(
            "Offset for the end frame. +1" +
            " is recommended for the sequences | 0 is recommended" +
            " for UnrealEngine cycles | -1 is recommended for Sketchfab cycles"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_nla_custom_start_frame = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Custom start time",
        description="Set when animation start",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_anim_nla_custom_end_frame = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Custom end time",
        description="Set when animation end",
        override={'LIBRARY_OVERRIDABLE'},
        default=1
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_anim_nla_custom_end_frame  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_nla_custom_start_frame  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_nla_end_frame_offset  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_nla_start_frame_offset  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_nla_export_name  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_nla_use  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_animation_nla_properties_expanded  # type: ignore[attr-defined]