# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List
import bpy
from enum import Enum
from typing import Tuple
from .. import bbpl

''' Example of usage:
class BFU_AlembicExportProcedure(str, Enum):
    STANDARD_ALEMBIC = "standard_alembic"

    @staticmethod
    def default() -> "BFU_AlembicExportProcedure":
        return BFU_AlembicExportProcedure.STANDARD_ALEMBIC

def get_alembic_export_procedure_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_AlembicExportProcedure.STANDARD_ALEMBIC.value,
            "Blender Standard",
            "Standard ALEMBIC.",
            "OUTLINER_OB_FONT",
            1),
        ]

def get_default_alembic_export_procedure() -> str:
    return BFU_AlembicExportProcedure.default().value
'''

class BFU_EngineRefSkeletonSearchModeEnum(str, Enum):
    AUTO = "auto"
    CUSTOM_NAME = "custom_name"
    CUSTOM_PATH_NAME = "custom_path_name"
    CUSTOM_REFERENCE = "custom_reference"

    @staticmethod
    def default() -> "BFU_EngineRefSkeletonSearchModeEnum":
        return BFU_EngineRefSkeletonSearchModeEnum.AUTO

    @classmethod
    def _missing_(cls, value: object) -> "BFU_EngineRefSkeletonSearchModeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_engine_ref_skeleton_search_mode_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_EngineRefSkeletonSearchModeEnum.AUTO.value,
            "Auto",
            "...",
            "OUTLINER_OB_FONT",
            1),
        (BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_NAME.value,
            "Custom name",
            "Default location with custom name",
            "OUTLINER_OB_FONT",
            2),
        (BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_PATH_NAME.value,
            "Custom path and name",
            "Set the custom light map resolution",
            "OUTLINER_OB_FONT",
            3),
        (BFU_EngineRefSkeletonSearchModeEnum.CUSTOM_REFERENCE.value,
            "custom reference",
            "Reference from Unreal.",
            "OUTLINER_OB_FONT",
            4)
        ]

def get_default_engine_ref_skeleton_search_mode() -> str:
    return BFU_EngineRefSkeletonSearchModeEnum.default().value

class BFU_EngineRefSkeletalMeshSearchModeEnum(str, Enum):
    AUTO = "auto"
    CUSTOM_NAME = "custom_name"
    CUSTOM_PATH_NAME = "custom_path_name"
    CUSTOM_REFERENCE = "custom_reference"

    @staticmethod
    def default() -> "BFU_EngineRefSkeletalMeshSearchModeEnum":
        return BFU_EngineRefSkeletalMeshSearchModeEnum.AUTO

    @classmethod
    def _missing_(cls, value: object) -> "BFU_EngineRefSkeletalMeshSearchModeEnum":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()
    
def get_engine_ref_skeletal_mesh_search_mode_enum_property_list() -> List[Tuple[str, str, str, str, int]]:
    return [
        (BFU_EngineRefSkeletalMeshSearchModeEnum.AUTO.value,
            "Auto",
            "...",
            "OUTLINER_OB_FONT",
            1),
        (BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_NAME.value,
            "Custom name",
            "Default location with custom name",
            "OUTLINER_OB_FONT",
            2),
        (BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_PATH_NAME.value,
            "Custom path and name",
            "Set the custom light map resolution",
            "OUTLINER_OB_FONT",
            3),
        (BFU_EngineRefSkeletalMeshSearchModeEnum.CUSTOM_REFERENCE.value,
            "custom reference",
            "Reference from Unreal.",
            "OUTLINER_OB_FONT",
            4)
        ]

def get_default_engine_ref_skeletal_mesh_search_mode() -> str:
    return BFU_EngineRefSkeletalMeshSearchModeEnum.default().value

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_engine_ref_skeleton_search_mode',
        'obj.bfu_engine_ref_skeleton_custom_path',
        'obj.bfu_engine_ref_skeleton_custom_name',
        'obj.bfu_engine_ref_skeleton_custom_ref',

        'obj.bfu_engine_ref_skeletal_mesh_search_mode',
        'obj.bfu_engine_ref_skeletal_mesh_custom_path',
        'obj.bfu_engine_ref_skeletal_mesh_custom_name',
        'obj.bfu_engine_ref_skeletal_mesh_custom_ref'
        ]
    return preset_values

def get_scene_engine_ref_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_engine_ref_properties_expanded.is_expanded()  # type: ignore

def get_object_engine_ref_skeleton_search_mode(obj: bpy.types.Object) -> BFU_EngineRefSkeletonSearchModeEnum:
    for mode in BFU_EngineRefSkeletonSearchModeEnum:
        if obj.bfu_engine_ref_skeleton_search_mode == mode.value: # type: ignore
            return mode
        
    print(f"Warning: Object '{obj.name}' has an invalid skeleton search mode '{obj.bfu_engine_ref_skeleton_search_mode}'. Using default search mode.") # type: ignore
    return BFU_EngineRefSkeletonSearchModeEnum.default()
    

def get_object_engine_ref_skeleton_custom_path(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeleton_custom_path  # type: ignore

def get_object_engine_ref_skeleton_custom_name(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeleton_custom_name  # type: ignore

def get_object_engine_ref_skeleton_custom_ref(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeleton_custom_ref  # type: ignore

def get_object_engine_ref_skeletal_mesh_search_mode(obj: bpy.types.Object) -> BFU_EngineRefSkeletalMeshSearchModeEnum:
    for mode in BFU_EngineRefSkeletalMeshSearchModeEnum:
        if obj.bfu_engine_ref_skeletal_mesh_search_mode == mode.value: # type: ignore
            return mode
        
    print(f"Warning: Object '{obj.name}' has an invalid skeletal mesh search mode '{obj.bfu_engine_ref_skeletal_mesh_search_mode}'. Using default search mode.") # type: ignore
    return BFU_EngineRefSkeletalMeshSearchModeEnum.default()

def get_object_engine_ref_skeletal_mesh_custom_path(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeletal_mesh_custom_path  # type: ignore

def get_object_engine_ref_skeletal_mesh_custom_name(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeletal_mesh_custom_name  # type: ignore

def get_object_engine_ref_skeletal_mesh_custom_ref(obj: bpy.types.Object) -> str:
    return obj.bfu_engine_ref_skeletal_mesh_custom_ref  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_engine_ref_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Engine Refs")  # type: ignore[attr-defined]

    bpy.types.Object.bfu_engine_ref_skeleton_search_mode = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Skeleton Ref",
        description='Specify the skeleton location in Unreal',
        override={'LIBRARY_OVERRIDABLE'},
        items=get_engine_ref_skeleton_search_mode_enum_property_list(),
        default=get_default_engine_ref_skeleton_search_mode()
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description="The path of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="ImportedBlenderAssets"
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description="The name of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="SK_MySketon_Skeleton"
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_ref = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description=(
            "The full reference of the Skeleton in Unreal. " +
            "(Use right clic on asset and copy reference.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="SkeletalMesh'/Game/ImportedBlenderAssets/SK_MySketon_Skeleton.SK_MySketon_Skeleton'"
        )


    bpy.types.Object.bfu_engine_ref_skeletal_mesh_search_mode = bpy.props.EnumProperty(  # type: ignore[attr-defined]
        name="Skeletal Mesh Ref",
        description='Specify the Skeletal Mesh location in Unreal',
        override={'LIBRARY_OVERRIDABLE'},
        items=get_engine_ref_skeletal_mesh_search_mode_enum_property_list(),
        default=get_default_engine_ref_skeletal_mesh_search_mode()
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description="The path of the Skeletal Mesh in Unreal. Skeletal Mesh not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="ImportedBlenderAssets"
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description="The name of the Skeletal Mesh in Unreal. Skeletal Mesh not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="SKM_MySkeletalMesh"
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_ref = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="",
        description=(
            "The full reference of the Skeletal Mesh in Unreal. " +
            "(Use right clic on asset and copy reference.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="SkeletalMesh'/Game/ImportedBlenderAssets/SKM_MySkeletalMesh.SKM_MySkeletalMesh'"
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_engine_ref_skeleton_custom_ref  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeleton_custom_name  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeleton_custom_path  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeleton_search_mode  # type: ignore[attr-defined]

    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_ref  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_name  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_path  # type: ignore[attr-defined]
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_search_mode  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_engine_ref_properties_expanded  # type: ignore[attr-defined]