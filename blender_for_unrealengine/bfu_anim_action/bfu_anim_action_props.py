# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from enum import Enum
from typing import List, Tuple
import bpy
from .. import bbpl
from .bfu_anim_action_operator_action_group import BFU_OT_ObjExportAction

class BFU_AnimActionExportEnum(str, Enum):
    EXPORT_AUTO = "export_auto"
    EXPORT_SPECIFIC_LIST = "export_specific_list"
    EXPORT_SPECIFIC_PREFIX = "export_specific_prefix"
    EXPORT_CURRENT = "export_current"
    DONT_EXPORT = "dont_export"

    @staticmethod
    def default() -> "BFU_AnimActionExportEnum":
        return BFU_AnimActionExportEnum.EXPORT_AUTO

    @classmethod
    def _missing_(cls, value: object) -> "BFU_AnimActionExportEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()

def get_anim_action_export_enum_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_AnimActionExportEnum.EXPORT_AUTO.value,
            "Export auto",
            "Export all actions connected to the bones names.",
            "FILE_SCRIPT",
            1),
        (BFU_AnimActionExportEnum.EXPORT_SPECIFIC_LIST.value,
            "Export specific list",
            "Export only actions that are checked in the list.",
            "LINENUMBERS_ON",
            3),
        (BFU_AnimActionExportEnum.EXPORT_SPECIFIC_PREFIX.value,
            "Export specific prefix",
            "Export only actions with a specific prefix" +
            " or the beginning of the actions names.",
            "SYNTAX_ON",
            4),
        (BFU_AnimActionExportEnum.DONT_EXPORT.value,
            "Not exported",
            "No action will be exported.",
            "MATPLANE",
            5),
        (BFU_AnimActionExportEnum.EXPORT_CURRENT.value,
            "Export Current",
            "Export only the current actions.",
            "FILE_SCRIPT",
            6),
    ]

def get_default_anim_action_export_enum() -> str:
    return BFU_AnimActionExportEnum.default().value

class BFU_AnimNamingTypeEnum(str, Enum):
    ACTION_NAME = "action_name"
    INCLUDE_ARMATURE_NAME = "include_armature_name"
    INCLUDE_CUSTOM_NAME = "include_custom_name"

    @staticmethod
    def default() -> "BFU_AnimNamingTypeEnum":
        return BFU_AnimNamingTypeEnum.ACTION_NAME

    @classmethod
    def _missing_(cls, value: object) -> "BFU_AnimNamingTypeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_anim_naming_type_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_AnimNamingTypeEnum.ACTION_NAME.value,
            "Action name",
            'Exemple: "Anim_MyAction"'),
        (BFU_AnimNamingTypeEnum.INCLUDE_ARMATURE_NAME.value,
            "Include Armature Name",
            'Include armature name in animation export file name.' +
            ' Exemple: "Anim_MyArmature_MyAction"'),
        (BFU_AnimNamingTypeEnum.INCLUDE_CUSTOM_NAME.value,
            "Include custom name",
            'Include custom name in animation export file name.' +
            ' Exemple: "Anim_MyCustomName_MyAction"'),
    ]

def get_default_anim_naming_type_enum() -> str:
    return BFU_AnimNamingTypeEnum.default().value

class BFU_AnimActionStartEndTimeEnum(str, Enum):
    WITH_KEYFRAMES = "with_keyframes"
    WITH_SCENEFRAMES = "with_sceneframes"
    WITH_CUSTOMFRAMES = "with_customframes"

    @staticmethod
    def default() -> "BFU_AnimActionStartEndTimeEnum":
        return BFU_AnimActionStartEndTimeEnum.WITH_KEYFRAMES

    @classmethod
    def _missing_(cls, value: object) -> "BFU_AnimActionStartEndTimeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_anim_action_start_end_time_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_AnimActionStartEndTimeEnum.WITH_KEYFRAMES.value,
            "Auto",
            "The time will be defined according" +
            " to the first and the last frame"),
        (BFU_AnimActionStartEndTimeEnum.WITH_SCENEFRAMES.value,
            "Scene time",
            "Time will be equal to the scene time"),
        (BFU_AnimActionStartEndTimeEnum.WITH_CUSTOMFRAMES.value,
            "Custom time",
            'The time of all the animations of this object' +
            ' is defined by you.' +
            ' Use "bfu_anim_action_custom_start_frame" and "bfu_anim_action_custom_end_frame"'),
    ]

def get_default_anim_action_start_end_time_enum() -> str:
    return BFU_AnimActionStartEndTimeEnum.default().value


def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        'obj.bfu_anim_action_export_enum',
        'obj.bfu_prefix_name_to_export',
        'obj.bfu_anim_action_start_end_time_enum',
        'obj.bfu_anim_action_start_frame_offset',
        'obj.bfu_anim_action_end_frame_offset',
        'obj.bfu_anim_action_custom_start_frame',
        'obj.bfu_anim_action_custom_end_frame',
        'obj.bfu_anim_naming_type',
        'obj.bfu_anim_naming_custom',
    ]
    return preset_values

def object_action_asset_list(obj: bpy.types.Object) -> List[BFU_OT_ObjExportAction]:
    return obj.bfu_action_asset_list #  type: ignore

def object_prefix_name_to_export(obj: bpy.types.Object) -> str:
    return obj.bfu_prefix_name_to_export #  type: ignore

def object_clear_action_asset_list(obj: bpy.types.Object) -> None:
    obj.bfu_action_asset_list.clear()  # type: ignore

def object_add_action_asset_list_item(obj: bpy.types.Object) -> BFU_OT_ObjExportAction:
    return obj.bfu_action_asset_list.add()  # type: ignore

def get_object_active_action_asset_list(obj: bpy.types.Object) -> int:
    return obj.bfu_active_action_asset_list  # type: ignore

def get_object_anim_action_export_enum(obj: bpy.types.Object) -> BFU_AnimActionExportEnum:
    return BFU_AnimActionExportEnum(obj.bfu_anim_action_export_enum)  # type: ignore

def get_object_prefix_name_to_export(obj: bpy.types.Object) -> str:
    return obj.bfu_prefix_name_to_export  # type: ignore

def has_object_with_export_enum(objects: List[bpy.types.Object], export_enum: BFU_AnimActionExportEnum) -> bool:
    for obj in objects:
        if get_object_anim_action_export_enum(obj) == export_enum:
            return True
    return False

def get_object_anim_action_start_end_time_enum(obj: bpy.types.Object) -> BFU_AnimActionStartEndTimeEnum:
    for enum in BFU_AnimActionStartEndTimeEnum:
        if obj.bfu_anim_action_start_end_time_enum == enum.value:  # type: ignore
            return enum

    print(f"Warning: Object {obj.name} has unknown start/end time '{obj.bfu_anim_action_start_end_time_enum}'. Falling back to default start/end time...")  # type: ignore
    return BFU_AnimActionStartEndTimeEnum.default()

def get_object_anim_action_start_frame_offset(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_action_start_frame_offset  # type: ignore

def get_object_anim_action_end_frame_offset(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_action_end_frame_offset  # type: ignore

def get_object_anim_action_custom_start_frame(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_action_custom_start_frame  # type: ignore

def get_object_anim_action_custom_end_frame(obj: bpy.types.Object) -> int:
    return obj.bfu_anim_action_custom_end_frame  # type: ignore

def get_object_anim_naming_type_enum(obj: bpy.types.Object) -> BFU_AnimNamingTypeEnum:
    for enum in BFU_AnimNamingTypeEnum:
        if obj.bfu_anim_naming_type == enum.value:  # type: ignore
            return enum

    print(f"Warning: Object {obj.name} has unknown naming type '{obj.bfu_anim_naming_type}'. Falling back to default naming type...")  # type: ignore
    return BFU_AnimNamingTypeEnum.default()

def get_object_anim_naming_custom(obj: bpy.types.Object) -> str:
    return obj.bfu_anim_naming_custom  # type: ignore

def get_window_manager_debug_show_action_list() -> bool:
    wm = bpy.context.window_manager
    return wm.bfu_debug_show_action_list  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_action_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions Properties")   # type: ignore[attr-defined]

    bpy.types.Object.bfu_action_asset_list = bpy.props.CollectionProperty(   # type: ignore[attr-defined]
        type=BFU_OT_ObjExportAction,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )

    bpy.types.Object.bfu_active_action_asset_list = bpy.props.IntProperty(   # type: ignore[attr-defined]
        name="Active Scene Action",
        description="Index of the currently active object action",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )
    
    bpy.types.Object.bfu_anim_action_export_enum = bpy.props.EnumProperty(   # type: ignore[attr-defined]
        name="Action to export",
        description="Export procedure for actions (Animations and poses)",
        override={'LIBRARY_OVERRIDABLE'},
        items=get_anim_action_export_enum_list(),
        default=get_default_anim_action_export_enum()
    )

    bpy.types.Object.bfu_prefix_name_to_export = bpy.props.StringProperty(   # type: ignore[attr-defined]
        # properties used with ""export_specific_prefix" on bfu_anim_action_export_enum
        name="Prefix name",
        description="Indicate the prefix of the actions that must be exported",
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=32,
        default="Example_",
        )

    bpy.types.Object.bfu_anim_action_start_end_time_enum = bpy.props.EnumProperty(   # type: ignore[attr-defined]
        name="Action Start/End Time",
        description="Set when animation starts and end",
        override={'LIBRARY_OVERRIDABLE'},
        items=get_anim_action_start_end_time_enum_list(),
        default=get_default_anim_action_start_end_time_enum()
        )

    bpy.types.Object.bfu_anim_action_start_frame_offset = bpy.props.IntProperty(   # type: ignore[attr-defined]
        name="Offset at start frame",
        description="Offset for the start frame.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_action_end_frame_offset = bpy.props.IntProperty(   # type: ignore[attr-defined]
        name="Offset at end frame",
        description=(
            "Offset for the end frame. +1" +
            " is recommended for the sequences | 0 is recommended" +
            " for UnrealEngine cycles | -1 is recommended for Sketchfab cycles"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )


    bpy.types.Object.bfu_anim_action_custom_start_frame = bpy.props.IntProperty(   # type: ignore[attr-defined]
        name="Custom start time",
        description="Set when animation start",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_anim_action_custom_end_frame = bpy.props.IntProperty(   # type: ignore[attr-defined]
        name="Custom end time",
        description="Set when animation end",
        override={'LIBRARY_OVERRIDABLE'},
        default=1
        )
    

    bpy.types.Object.bfu_anim_naming_type = bpy.props.EnumProperty(   # type: ignore[attr-defined]
        name="Naming type",
        override={'LIBRARY_OVERRIDABLE'},
        items=get_anim_naming_type_enum_list(),
        default=get_default_anim_naming_type_enum()
        )

    bpy.types.Object.bfu_anim_naming_custom = bpy.props.StringProperty(   # type: ignore[attr-defined]
        name="Export name",
        override={'LIBRARY_OVERRIDABLE'},
        default='MyCustomName'
        )
    
    bpy.types.WindowManager.bfu_debug_show_action_list = bpy.props.BoolProperty(   # type: ignore[attr-defined]
        name="Show Debug Info",
        description="Show debug information about the action list overrides",
        default=False
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.bfu_debug_show_action_list   # type: ignore[attr-defined]

    del bpy.types.Object.bfu_anim_naming_custom   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_naming_type   # type: ignore[attr-defined]

    del bpy.types.Object.bfu_anim_action_custom_end_frame   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_action_custom_start_frame   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_action_end_frame_offset   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_action_start_frame_offset   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_action_start_end_time_enum   # type: ignore[attr-defined]

    del bpy.types.Object.bfu_prefix_name_to_export   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_anim_action_export_enum   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_active_action_asset_list   # type: ignore[attr-defined]
    del bpy.types.Object.bfu_action_asset_list   # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_animation_action_properties_expanded   # type: ignore[attr-defined]