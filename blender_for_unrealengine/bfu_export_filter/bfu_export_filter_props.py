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

class BFU_ExportSelectionFilterEnum(str, Enum):
    DEFAULT = "default"
    ONLY_OBJECT = "only_object"
    ONLY_OBJECT_AND_ACTIVE = "only_object_and_active"

    @staticmethod
    def default() -> "BFU_ExportSelectionFilterEnum":
        return BFU_ExportSelectionFilterEnum.DEFAULT

    @classmethod
    def _missing_(cls, value: object) -> "BFU_ExportSelectionFilterEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_export_selection_filter_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_ExportSelectionFilterEnum.DEFAULT,
            "No Filter",
            "Export as normal all objects with the recursive export option."),
        (BFU_ExportSelectionFilterEnum.ONLY_OBJECT,
            "Only selected",
            "Export only the selected and visible object(s)"),
        (BFU_ExportSelectionFilterEnum.ONLY_OBJECT_AND_ACTIVE,
            "Only selected, active action / part",
            "Export only the selected and visible object(s) and active action on this object or part for modular skeletal mesh"),
    ]

def get_default_export_selection_filter_enum() -> str:
    return BFU_ExportSelectionFilterEnum.default().value

def get_preset_values() -> List[str]:
    preset_values = [
        # Filter Categories
        'scene.bfu_use_static_export',
        'scene.bfu_use_static_collection_export',
        'scene.bfu_use_skeletal_export',
        'scene.bfu_use_animation_export',
        'scene.bfu_use_alembic_export',
        'scene.bfu_use_groom_simulation_export',
        'scene.bfu_use_camera_export',
        'scene.bfu_use_spline_export',

        # Additional Files
        'scene.bfu_use_text_export_log',
        'scene.bfu_use_text_import_asset_script',
        'scene.bfu_use_text_import_sequence_script',
        'scene.bfu_use_text_additional_data',

        # Export Filter
        'scene.bfu_export_selection_filter',
        ]
    return preset_values


def scene_use_static_export(scene: bpy.types.Scene) -> bool: 
    return scene.bfu_use_static_export # type: ignore

def scene_use_static_collection_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_static_collection_export # type: ignore

def scene_use_skeletal_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_skeletal_export # type: ignore

def scene_use_animation_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_animation_export # type: ignore

def scene_use_alembic_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_alembic_export # type: ignore

def scene_use_groom_simulation_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_groom_simulation_export # type: ignore

def scene_use_camera_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_camera_export # type: ignore

def scene_use_spline_export(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_spline_export # type: ignore

def scene_use_text_export_log(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_text_export_log # type: ignore

def scene_use_text_import_asset_script(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_text_import_asset_script # type: ignore

def scene_use_text_import_sequence_script(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_text_import_sequence_script # type: ignore

def scene_use_text_additional_data(scene: bpy.types.Scene) -> bool:
    return scene.bfu_use_text_additional_data # type: ignore

def scene_export_selection_filter(scene: bpy.types.Scene) -> BFU_ExportSelectionFilterEnum:
    for item in BFU_ExportSelectionFilterEnum:
        if item.value == scene.bfu_export_selection_filter:  # type: ignore
            return item
        
    print(f"Warning: Scene has unknown export selection filter '{scene.bfu_export_selection_filter}'. Falling back to default export selection filter...")  # type: ignore
    return BFU_ExportSelectionFilterEnum.default()

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_export_filter_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Export filters") #  type: ignore

    # Filter Categories
    bpy.types.Scene.bfu_use_static_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="StaticMesh(s)",
        description="Check mark to export StaticMesh(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_static_collection_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Collection(s) ",
        description="Check mark to export Collection(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_skeletal_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="SkeletalMesh(s)",
        description="Check mark to export SkeletalMesh(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_animation_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Animation(s)",
        description="Check mark to export Animation(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_alembic_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Alembic Animation(s)",
        description="Check mark to export Alembic animation(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_groom_simulation_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Groom Simulation(s)",
        description="Check mark to export Groom Simulation(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_camera_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Camera(s)",
        description="Check mark to export Camera(s)",
        default=True
        )

    bpy.types.Scene.bfu_use_spline_export = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Spline(s)",
        description="Check mark to export Spline(s)",
        default=True
        )
    
    # Additional Files
    bpy.types.Scene.bfu_use_text_export_log = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Export Log",
        description="Check mark to write export log file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_import_asset_script = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Import assets script",
        description="Check mark to write import asset script file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_import_sequence_script = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Import sequence script",
        description="Check mark to write import sequencer script file",
        default=True
        )

    bpy.types.Scene.bfu_use_text_additional_data = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Additional data",
        description=(
            "Check mark to write additional data" +
            " like parameter or anim tracks"),
        default=True
        )
    
    # Export Filter
    bpy.types.Scene.bfu_export_selection_filter = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Selection filter",
        items=get_export_selection_filter_enum_list(),
        description=(
            "Choose what need be export from asset list."),
        default=get_default_export_selection_filter_enum()
        )

def unregister():
    del bpy.types.Scene.bfu_export_selection_filter  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_use_text_additional_data  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_text_import_sequence_script  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_text_import_asset_script  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_text_export_log  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_use_spline_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_camera_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_groom_simulation_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_alembic_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_animation_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_skeletal_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_static_collection_export  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_use_static_export  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_export_filter_properties_expanded  # type: ignore[attr-defined]

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)