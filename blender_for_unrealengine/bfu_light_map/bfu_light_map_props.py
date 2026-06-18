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


class BFU_StaticMeshLightMapMode(str, Enum):
    DEFAULT = "Default"
    CUSTOM_MAP = "CustomMap"
    SURFACE_AREA = "SurfaceArea"

    @staticmethod
    def default() -> "BFU_StaticMeshLightMapMode":
        return BFU_StaticMeshLightMapMode.DEFAULT

    @classmethod
    def _missing_(cls, value: object) -> "BFU_StaticMeshLightMapMode":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_static_mesh_light_map_mode_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_StaticMeshLightMapMode.DEFAULT,
            "Default",
            "Has no effect on light maps"),
        (BFU_StaticMeshLightMapMode.CUSTOM_MAP,
            "Custom map",
            "Set the custom light map resolution"),
        (BFU_StaticMeshLightMapMode.SURFACE_AREA,
            "Surface Area",
            "Set light map resolution depending on the surface Area"),
    ]

def get_default_static_mesh_light_map_mode_enum() -> str:
    return BFU_StaticMeshLightMapMode.default().value

def get_preset_values() -> List[str]:
    preset_values = [
            'obj.bfu_static_mesh_light_map_mode',
            'obj.bfu_static_mesh_custom_light_map_res',
            'obj.bfu_static_mesh_light_map_surface_scale',
            'obj.bfu_static_mesh_light_map_round_power_of_two',
            'obj.bfu_use_static_mesh_light_map_world_scale',
            'obj.bfu_generate_light_map_uvs',
        ]
    return preset_values

def get_scene_light_map_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_object_light_map_properties_expanded.is_expanded()  # type: ignore

def get_tools_light_map_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_tools_light_map_properties_expanded.is_expanded()  # type: ignore

def get_object_static_mesh_light_map_mode(obj: bpy.types.Object) -> BFU_StaticMeshLightMapMode:
    return BFU_StaticMeshLightMapMode(obj.bfu_static_mesh_light_map_mode)  # type: ignore

def get_object_static_mesh_custom_light_map_res(obj: bpy.types.Object) -> int:
    return obj.bfu_static_mesh_custom_light_map_res  # type: ignore

def get_object_computed_static_mesh_light_map_res(obj: bpy.types.Object) -> float:
    return obj.bfu_computed_static_mesh_light_map_res  # type: ignore

def get_object_static_mesh_light_map_surface_scale(obj: bpy.types.Object) -> float:
    return obj.bfu_static_mesh_light_map_surface_scale  # type: ignore

def get_object_static_mesh_light_map_round_power_of_two(obj: bpy.types.Object) -> bool:
    return obj.bfu_static_mesh_light_map_round_power_of_two  # type: ignore

def get_object_use_static_mesh_light_map_world_scale(obj: bpy.types.Object) -> bool:
    return obj.bfu_use_static_mesh_light_map_world_scale  # type: ignore

def get_object_generate_light_map_uvs(obj: bpy.types.Object) -> bool:
    return obj.bfu_generate_light_map_uvs  # type: ignore


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_object_light_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Light map")  # type: ignore[attr-defined]
    bpy.types.Scene.bfu_tools_light_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Light Map")  # type: ignore[attr-defined]


    # StaticMeshImportData
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html


    bpy.types.Object.bfu_static_mesh_light_map_mode = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Light Map",
        description='Specify how the light map resolution will be generated',
        override={'LIBRARY_OVERRIDABLE'},
        items= get_static_mesh_light_map_mode_enum_list(),
        default= get_default_static_mesh_light_map_mode_enum()
        )

    bpy.types.Object.bfu_static_mesh_custom_light_map_res = bpy.props.IntProperty(  # type: ignore[attr-defined]
        name="Light Map Resolution",
        description="This is the resolution of the light map",
        override={'LIBRARY_OVERRIDABLE'},
        soft_max=2048,
        soft_min=16,
        max=4096,  # Max for unreal
        min=4,  # Min for unreal
        default=64
        )

    bpy.types.Object.bfu_computed_static_mesh_light_map_res = bpy.props.FloatProperty(  # type: ignore[attr-defined]
        name="Computed Light Map Resolution",
        description="This is the computed resolution of the light map",
        override={'LIBRARY_OVERRIDABLE'},
        default=64.0
        )

    bpy.types.Object.bfu_static_mesh_light_map_surface_scale = bpy.props.FloatProperty(  # type: ignore[attr-defined]
        name="Surface scale",
        description="This is for resacle the surface Area value",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.00001,  # Min for unreal
        default=64
        )

    bpy.types.Object.bfu_static_mesh_light_map_round_power_of_two = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Round power of 2",
        description=(
            "round Light Map resolution to nearest power of 2"
            ),
        default=True
        )

    bpy.types.Object.bfu_use_static_mesh_light_map_world_scale = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Use world scale",
        description=(
            "If not that will use the object scale."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_generate_light_map_uvs = bpy.props.BoolProperty(  # type: ignore[attr-defined]
        name="Generate LightmapUVs",
        description=(
            "If checked, UVs for Lightmap will automatically be generated."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_generate_light_map_uvs  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_use_static_mesh_light_map_world_scale  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_static_mesh_light_map_round_power_of_two  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_static_mesh_light_map_surface_scale  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_computed_static_mesh_light_map_res  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_static_mesh_custom_light_map_res  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_static_mesh_light_map_mode  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_tools_light_map_properties_expanded  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_object_light_map_properties_expanded  # type: ignore[attr-defined]