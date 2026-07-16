# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List
import bpy
from .. import bbpl


def get_preset_values() -> List[str]:
    preset_values: List[str] = [
        'obj.bfu_disable_free_scale_animation',
        'obj.bfu_export_animation_without_mesh',
        'obj.bfu_export_animation_without_materials',
        'obj.bfu_export_animation_without_textures',
        'obj.bfu_sample_anim_for_export',
        'obj.bfu_simplify_anim_for_export',
    ]
    return preset_values

def get_object_sample_anim_for_export(obj: bpy.types.Object) -> float:
    return obj.bfu_sample_anim_for_export  # type: ignore

def get_object_simplify_anim_for_export(obj: bpy.types.Object) -> float:
    return obj.bfu_simplify_anim_for_export  # type: ignore

def get_object_disable_free_scale_animation(obj: bpy.types.Object) -> bool:
    return obj.bfu_disable_free_scale_animation  # type: ignore

def get_object_export_animation_without_mesh(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_animation_without_mesh  # type: ignore

def get_object_export_animation_without_materials(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_animation_without_materials  # type: ignore

def get_object_export_animation_without_textures(obj: bpy.types.Object) -> bool:
    return obj.bfu_export_animation_without_textures  # type: ignore

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_animation_advanced_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Animation Advanced Properties")  # type: ignore

    bpy.types.Object.bfu_sample_anim_for_export = bpy.props.FloatProperty(  # type: ignore
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.01, max=100.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        )

    bpy.types.Object.bfu_simplify_anim_for_export = bpy.props.FloatProperty(  # type: ignore
        name="Simplify animations",
        description=(
            "How much to simplify baked values" +
            " (0.0 to disable, the higher the more simplified)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # No simplification to up to 10% of current magnitude tolerance.
        min=0.0, max=100.0,
        soft_min=0.0, soft_max=10.0,
        default=0.0,
        )
    
    bpy.types.Object.bfu_disable_free_scale_animation = bpy.props.BoolProperty(  # type: ignore
        name="Disable non-uniform scale animation.",
        description=(
            "If checked, scale animation track's elements always have same value. " + 
            "This applies basic bones only."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )

    bpy.types.Object.bfu_export_animation_without_mesh = bpy.props.BoolProperty(  # type: ignore
        name="Export animation without mesh",
        description="If checked, When exporting animation, do not include mesh data in the animation exported files. \n"
        "(False by default because don't work with shape keys animation.)",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )
    
    bpy.types.Object.bfu_export_animation_without_materials = bpy.props.BoolProperty(  # type: ignore
        name="Export animation without materials",
        description="If checked, When exporting animation, do not include materials in the animation exported files.",
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )
    
    bpy.types.Object.bfu_export_animation_without_textures = bpy.props.BoolProperty(  # type: ignore
        name="Export animation without textures",
        description="If checked, When exporting animation, do not include textures in the animation exported files.",
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_export_animation_without_textures  # type: ignore
    del bpy.types.Object.bfu_export_animation_without_materials  # type: ignore
    del bpy.types.Object.bfu_export_animation_without_mesh  # type: ignore
    del bpy.types.Object.bfu_disable_free_scale_animation  # type: ignore
    del bpy.types.Object.bfu_simplify_anim_for_export  # type: ignore
    del bpy.types.Object.bfu_sample_anim_for_export  # type: ignore
    del bpy.types.Scene.bfu_animation_advanced_properties_expanded  # type: ignore