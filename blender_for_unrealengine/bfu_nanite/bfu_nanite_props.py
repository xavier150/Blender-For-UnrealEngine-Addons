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

class BFU_BuildNaniteMode(str, Enum):
    AUTO = "auto"
    BUILD_NANITE_TRUE = "build_nanite_true"
    BUILD_NANITE_FALSE = "build_nanite_false"

    @staticmethod
    def default() -> "BFU_BuildNaniteMode":
        return BFU_BuildNaniteMode.AUTO

    @classmethod
    def _missing_(cls, value: object) -> "BFU_BuildNaniteMode":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_build_nanite_mode_enum_list() -> List[Tuple[str, str, str]]:
    return [
        (BFU_BuildNaniteMode.AUTO,
            "Auto",
            "Use project settings."),
        (BFU_BuildNaniteMode.BUILD_NANITE_TRUE,
            "Build Nanite",
            "Build nanite at import."),
        (BFU_BuildNaniteMode.BUILD_NANITE_FALSE,
            "Don't Build Nanite",
            "Don't build and set object as non Nanite.")
    ]

def get_default_build_nanite_mode_enum() -> str:
    return BFU_BuildNaniteMode.default().value

def get_preset_values() -> List[str]:
    preset_values = [
            'obj.bfu_build_nanite_mode'
        ]
    return preset_values

def get_object_build_nanite_mode(obj: bpy.types.Object) -> BFU_BuildNaniteMode:
    return BFU_BuildNaniteMode(obj.bfu_build_nanite_mode)  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # StaticMeshImportData
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html


    bpy.types.Scene.bfu_object_nanite_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Nanite")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_build_nanite_mode = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Build Nanite",
        description='If enabled, imported meshes will be rendered by Nanite at runtime.',
        override={'LIBRARY_OVERRIDABLE'},
        items= get_build_nanite_mode_enum_list(),
        default=get_default_build_nanite_mode_enum()
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_build_nanite_mode  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_object_nanite_properties_expanded  # type: ignore[attr-defined]