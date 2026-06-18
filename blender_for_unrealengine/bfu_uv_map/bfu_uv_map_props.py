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
    preset_values = [
        'obj.bfu_convert_geometry_node_attribute_to_uv',
        'obj.bfu_convert_geometry_node_attribute_to_uv_name',
        'obj.bfu_use_correct_extrem_uv_scale',
        'obj.bfu_correct_extrem_uv_scale_step_scale',
        'obj.bfu_correct_extrem_uv_scale_use_absolute',
    ]
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bfu_object_uv_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="UV map")
    bpy.types.Scene.bfu_tools_uv_map_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="UV Map")

    bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv = bpy.props.BoolProperty(
        name="Convert Attribute To Uv",
        description=(
            "convert target geometry node attribute to UV when found."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv_name = bpy.props.StringProperty(
        name="Attribute name",
        description=(
            "Name of the Attribute to convert"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="UVMap",
        )

    bpy.types.Object.bfu_use_correct_extrem_uv_scale = bpy.props.BoolProperty(
        name=bpy.app.translations.pgettext("Correct Extrem UV Scale For Unreal", "interface.correct_use_extrem_uv_scale_name"),
        description=bpy.app.translations.pgettext("Correct Extrem UV Scale for better UV quality in Unreal Engine (Export will take more time).", "tooltips.correct_use_extrem_uv_scale_desc"),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )
    
    bpy.types.Object.bfu_correct_extrem_uv_scale_step_scale = bpy.props.IntProperty(
        name=bpy.app.translations.pgettext("Step Scale", "interface.correct_extrem_uv_scale_step_scale_name"),
        description=bpy.app.translations.pgettext("Scale of the snap grid.", "tooltips.correct_extrem_uv_scale_step_scale_desc"),
        override={'LIBRARY_OVERRIDABLE'},
        default=2,
        min=1,
        max=100,
        )
    
    bpy.types.Object.bfu_correct_extrem_uv_scale_use_absolute = bpy.props.BoolProperty(
        name=bpy.app.translations.pgettext("Use Positive Pos", "interface.correct_extrem_uv_scale_use_absolute_name"),
        description=bpy.app.translations.pgettext("Keep uv islands to positive positions.", "tooltips.correct_extrem_uv_scale_use_absolute_desc"),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_correct_extrem_uv_scale_use_absolute
    del bpy.types.Object.bfu_correct_extrem_uv_scale_step_scale
    del bpy.types.Object.bfu_use_correct_extrem_uv_scale
    del bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv_name
    del bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv

    del bpy.types.Scene.bfu_tools_uv_map_properties_expanded
    del bpy.types.Scene.bfu_object_uv_map_properties_expanded
