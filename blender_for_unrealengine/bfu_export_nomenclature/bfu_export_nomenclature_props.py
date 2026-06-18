# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List, Set, Any
import os
from pathlib import Path
import bpy
from .. import bbpl


def get_preset_values() -> List[str]:
    preset_values = [
        # Prefix
        'scene.bfu_static_mesh_prefix_export_name',
        'scene.bfu_skeletal_mesh_prefix_export_name',
        'scene.bfu_skeleton_prefix_export_name',
        'scene.bfu_alembic_animation_prefix_export_name',
        'scene.bfu_groom_simulation_prefix_export_name',
        'scene.bfu_anim_prefix_export_name',
        'scene.bfu_pose_prefix_export_name',
        'scene.bfu_camera_prefix_export_name',
        'scene.bfu_spline_prefix_export_name',
        
        # Sub folder
        'scene.bfu_anim_subfolder_name',

        # Import location
        'scene.bfu_unreal_import_module',
        'scene.bfu_unreal_import_location',

        # File path
        'scene.bfu_export_static_mesh_file_path',
        'scene.bfu_export_skeletal_mesh_file_path',
        'scene.bfu_export_skeletal_animation_file_path',
        'scene.bfu_export_alembic_file_path',
        'scene.bfu_export_groom_file_path',
        'scene.bfu_export_camera_file_path',
        'scene.bfu_export_spline_file_path',
        'scene.bfu_export_other_file_path',

        # File name
        'scene.bfu_file_export_log_name',
        'scene.bfu_file_import_asset_script_name',
        'scene.bfu_file_import_sequencer_script_name',
    ]
    return preset_values

def get_scene_nomenclature_properties_expanded(scene: bpy.types.Scene) -> bool:
    return scene.bfu_nomenclature_properties_expanded.is_expanded()  # type: ignore

def get_static_mesh_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_static_mesh_prefix_export_name  # type: ignore

def get_skeletal_mesh_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_skeletal_mesh_prefix_export_name  # type: ignore

def get_skeleton_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_skeleton_prefix_export_name  # type: ignore

def get_alembic_animation_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_alembic_animation_prefix_export_name  # type: ignore

def get_groom_simulation_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_groom_simulation_prefix_export_name  # type: ignore

def get_anim_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_anim_prefix_export_name  # type: ignore

def get_pose_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_pose_prefix_export_name  # type: ignore

def get_camera_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_camera_prefix_export_name  # type: ignore

def get_spline_prefix_export_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_spline_prefix_export_name  # type: ignore

def get_anim_subfolder_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_anim_subfolder_name  # type: ignore

def get_unreal_import_module(scene: bpy.types.Scene) -> str:
    return scene.bfu_unreal_import_module  # type: ignore

def get_unreal_import_location(scene: bpy.types.Scene) -> str:
    return scene.bfu_unreal_import_location  # type: ignore

def get_export_static_mesh_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_static_mesh_file_path  # type: ignore

def get_export_skeletal_mesh_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_skeletal_mesh_file_path  # type: ignore

def get_export_skeletal_animation_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_skeletal_animation_file_path  # type: ignore

def get_export_alembic_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_alembic_file_path  # type: ignore

def get_export_groom_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_groom_file_path  # type: ignore

def get_export_camera_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_camera_file_path  # type: ignore

def get_export_spline_file_path(scene: bpy.types.Scene) -> str: 
    return scene.bfu_export_spline_file_path  # type: ignore

def get_export_other_file_path(scene: bpy.types.Scene) -> str:
    return scene.bfu_export_other_file_path  # type: ignore

def get_file_export_log_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_file_export_log_name  # type: ignore

def get_file_import_asset_script_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_file_import_asset_script_name  # type: ignore

def get_file_import_sequencer_script_name(scene: bpy.types.Scene) -> str:
    return scene.bfu_file_import_sequencer_script_name  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_nomenclature_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Nomenclature")  # type: ignore[attr-defined]

    # Prefix
    bpy.types.Scene.bfu_static_mesh_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="StaticMesh Prefix",
        description="Prefix of staticMesh",
        maxlen=32,
        default="SM_")

    bpy.types.Scene.bfu_skeletal_mesh_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="SkeletalMesh Prefix ",
        description="Prefix of SkeletalMesh",
        maxlen=32,
        default="SKM_")

    bpy.types.Scene.bfu_skeleton_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Skeleton Prefix ",
        description="Prefix of skeleton",
        maxlen=32,
        default="SK_")

    bpy.types.Scene.bfu_alembic_animation_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Alembic Prefix ",
        description="Prefix of Alembic (SkeletalMesh in unreal)",
        maxlen=32,
        default="SKM_")
    
    bpy.types.Scene.bfu_groom_simulation_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Groom Prefix ",
        description="Prefix of Groom Simulation",
        maxlen=32,
        default="GS_")
    
    bpy.types.Scene.bfu_anim_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="AnimationSequence Prefix",
        description="Prefix of AnimationSequence",
        maxlen=32,
        default="Anim_")

    bpy.types.Scene.bfu_pose_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="AnimationSequence(Pose) Prefix",
        description="Prefix of AnimationSequence with only one frame",
        maxlen=32,
        default="Pose_")

    bpy.types.Scene.bfu_camera_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Camera anim Prefix",
        description="Prefix of camera animations",
        maxlen=32,
        default="Cam_")
    
    bpy.types.Scene.bfu_spline_prefix_export_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Spline anim Prefix",
        description="Prefix of spline animations",
        maxlen=32,
        default="Spline_")

    # Sub folder
    bpy.types.Scene.bfu_anim_subfolder_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Animations sub folder name",
        description=(
            "The name of sub folder for animations New." +
            " You can now use ../ for up one directory."),
        maxlen=512,
        default="Anim")
    
    # Import location
    bpy.types.Scene.bfu_unreal_import_module = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Unreal import module",
        description="Which module (plugin name) to import to. Default is 'Game', meaning it will be put into your project's /Content/ folder. If you wish to import to a plugin (for example a plugin called 'myPlugin'), just write its name here",
        maxlen=512,
        default='Game')

    bpy.types.Scene.bfu_unreal_import_location = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Unreal import location",
        description="Unreal assets import location inside the module",
        maxlen=512,
        default='ImportedBlenderAssets')

    def blender_relpath(*parts: str) -> str:
        # Relative blender path. 
        # Need use pathlib join to support different OS.
        # os.sep at end because it a folder path.
        return "//" + str(Path("").joinpath(*parts)) + os.sep

    def export_property_options() -> Set[Any]:
        if bpy.app.version >= (4, 5, 0): # Added in Blender 4.5
            return {'PATH_SUPPORTS_BLEND_RELATIVE'}
        else:
            return set()

    # File path
    bpy.types.Scene.bfu_export_static_mesh_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Static Mesh Export Path",
        description="Choose a directory to export Static Mesh(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "StaticMesh"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_skeletal_mesh_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Skeletal Mesh Export Path",
        description="Choose a directory to export Skeletal Mesh(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "SkeletalMesh"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_skeletal_animation_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Skeletal Animation Export Path",
        description="Choose a directory to export Skeletal Animation(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "SkeletalAnimation"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_alembic_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Alembic Export Path",
        description="Choose a directory to export Alembic animation(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "Alembic"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_groom_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Groom Export Path",
        description="Choose a directory to export Groom simulation(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "Groom"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_camera_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Camera Export Path",
        description="Choose a directory to export Camera(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "Sequencer"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_spline_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Spline Export Path",
        description="Choose a directory to export Spline(s)",
        maxlen=512,
        default=blender_relpath("ExportedAssets", "Spline"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    bpy.types.Scene.bfu_export_other_file_path = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Other Export Path",
        description="Choose a directory to export text file and other",
        maxlen=512,
        default=blender_relpath("ExportedAssets"),
        subtype='DIR_PATH',
        options=export_property_options()
    )

    # File name
    bpy.types.Scene.bfu_file_export_log_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Export log name",
        description="Export log name",
        maxlen=64,
        default="ExportLog.txt")

    bpy.types.Scene.bfu_file_import_asset_script_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Import asset script Name",
        description="Import asset script name",
        maxlen=64,
        default="ImportAssetScript.py")

    bpy.types.Scene.bfu_file_import_sequencer_script_name = bpy.props.StringProperty(  # type: ignore[attr-defined]
        name="Import sequencer script Name",
        description="Import sequencer script name",
        maxlen=64,
        default="ImportSequencerScript.py")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_file_import_sequencer_script_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_file_import_asset_script_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_file_export_log_name  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_export_other_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_spline_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_camera_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_groom_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_alembic_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_skeletal_animation_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_skeletal_mesh_file_path  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_export_static_mesh_file_path  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_unreal_import_location  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_unreal_import_module  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_anim_subfolder_name  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_spline_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_camera_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_pose_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_anim_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_groom_simulation_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_alembic_animation_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_skeleton_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_skeletal_mesh_prefix_export_name  # type: ignore[attr-defined]
    del bpy.types.Scene.bfu_static_mesh_prefix_export_name  # type: ignore[attr-defined]

    del bpy.types.Scene.bfu_nomenclature_properties_expanded  # type: ignore[attr-defined]