# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import List, Set, TYPE_CHECKING, Tuple
from enum import Enum
import bpy
from .. import bbpl
from . import bfu_spline_utils
from . import bfu_spline_write_paste_commands


class BFU_SplineDesiredComponent(str, Enum):
    SPLINE = "Spline"
    CUSTOM = "Custom"

    @staticmethod
    def default() -> "BFU_SplineDesiredComponent":
        return BFU_SplineDesiredComponent.SPLINE

    @classmethod
    def _missing_(cls, value: object) -> "BFU_SplineDesiredComponent":
        # Fallback for old scenes/transient states with empty or invalid value.
        return cls.default()

def get_spline_desired_component_enum_property_list() -> List[Tuple[str, str, str, int]]:
    return [
        (BFU_SplineDesiredComponent.SPLINE.value,
            "Spline",
            "Regular Spline component.",
            1),
        (BFU_SplineDesiredComponent.CUSTOM.value,
            "Custom",
            "Use a custom spline component.",
            2),
        ]

def get_default_spline_desired_component() -> str:
    return BFU_SplineDesiredComponent.default().value

def get_preset_values() -> List[str]:
    preset_values = [
        'obj.bfu_desired_spline_type',
        'obj.bfu_custom_spline_component',
        'obj.bfu_export_spline_as_static_mesh'
        ]
    return preset_values
   

# Object button
class BFU_OT_CopyActivesplineOperator(bpy.types.Operator):
    bl_label = "Copy active spline for Unreal"
    bl_idname = "object.bfu_copy_active_spline_data"
    bl_description = "Copy active spline data. (Use CTRL+V in Unreal viewport)"


    def execute(self, context: bpy.types.Context) -> Set[str]:  # type: ignore
        obj = context.object
        if obj:
            result = bfu_spline_write_paste_commands.get_spline_unreal_clipboard([obj])
            if result[0]:
                bbpl.basics.set_windows_clipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
        else:
            self.report({'WARNING'}, "No active object found. Please select a spline (Curve) object.")
        return {'FINISHED'}

# Scene button
class BFU_OT_CopySelectedsplinesOperator(bpy.types.Operator):
    bl_label = "Copy selected spline(s) for Unreal"
    bl_idname = "object.copy_selected_splines_data"
    bl_description = "Copy selected spline(s) data. (Use CTRL+V in Unreal viewport)"

    def execute(self, context: bpy.types.Context) -> Set[str]:  # type: ignore
        objs = context.selected_objects
        result = bfu_spline_write_paste_commands.get_spline_unreal_clipboard(objs)
        if result[0]:
            bbpl.basics.set_windows_clipboard(result[1])
            self.report({'INFO'}, result[2])
        else:
            self.report({'WARNING'}, result[2])
        return {'FINISHED'}

class BFU_OT_ConvertAnyCurveToBezier(bpy.types.Operator):
    """Convert selected curves to Bezier for Unreal Engine export."""
    bl_label = "Convert selected curves to Bezier for Unreal"
    bl_idname = "object.bfu_convert_any_curve_to_bezier"
    bl_description = "Convert selected curves to Bezier for Unreal Engine export."
    bl_options = {'REGISTER', 'UNDO'}
    
    resolution: bpy.props.IntProperty(  # type: ignore
        name="Resolution",
        description="Number of computed points in the U direction between every pair of control points.",
        default=12,
        min=1,
        max=64
    )

    if TYPE_CHECKING:
        resolution: int

    def execute(self, context: bpy.types.Context) -> Set[str]:  # type: ignore
        print(f"Resolution set to: {self.resolution}")
        # Votre logique de conversion ici
        bfu_spline_utils.convert_select_curves_to_bezier(self.resolution)
        return {'FINISHED'}
    

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> Set[str]:  # type: ignore
        # This calls the dialog allowing the user to modify properties before execution
        return context.window_manager.invoke_props_dialog(self)  # type: ignore

        return {'FINISHED'}

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CopyActivesplineOperator,
    BFU_OT_CopySelectedsplinesOperator,
    BFU_OT_ConvertAnyCurveToBezier
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bfu_spline_properties_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Spline Properties")  # type: ignore
    bpy.types.Scene.bfu_spline_tools_expanded = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Spline")  # type: ignore

    bpy.types.Object.bfu_desired_spline_type = bpy.props.EnumProperty(  # type: ignore
        name="Spline Type",
        description="Choose the type of spline",
        items=get_spline_desired_component_enum_property_list(),
        default=get_default_spline_desired_component()
    )

    bpy.types.Object.bfu_spline_resample_resolution = bpy.props.IntProperty(  # type: ignore
        name="Resample resolution",
        description="NURBS curves must be resampled. You can choose the resampling resolution. 12 It's nice to keep the same quality but consume a lot of performance in Unreal Engine.",
        max=64,
        min=0,
        default=12,
    )

    bpy.types.Object.bfu_custom_spline_component = bpy.props.StringProperty(  # type: ignore
        name="Custom spline Component",
        description=('Ref adress for an custom spline component'),
        override={'LIBRARY_OVERRIDABLE'},
        default="/Script/Engine.MySplineComponent",
        )
    
    bpy.types.Object.bfu_export_spline_as_static_mesh = bpy.props.BoolProperty(  # type: ignore
        name="Export as Static Mesh",
        description="If true this mesh will be exported as a Static Mesh",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )
    
    bpy.types.Scene.bfu_spline_vector_scale = bpy.props.FloatVectorProperty(  # type: ignore
        name="Spline Vector Scale (Apply on all splines)",
        description="Spline export scale for Unreal Engine.\n" \
         "- If you use glTF with unit scale at 1.0 keep 100.0.\n" \
         "- If you work with FBX and unit scale 0.01 use 1.0.",
        size=3,
        default=(100.0, 100.0, 100.0),
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bfu_spline_vector_scale  # type: ignore
    del bpy.types.Object.bfu_export_spline_as_static_mesh  # type: ignore
    del bpy.types.Object.bfu_custom_spline_component  # type: ignore
    del bpy.types.Object.bfu_spline_resample_resolution  # type: ignore
    del bpy.types.Object.bfu_desired_spline_type  # type: ignore
    del bpy.types.Scene.bfu_spline_tools_expanded  # type: ignore
    del bpy.types.Scene.bfu_spline_properties_expanded  # type: ignore


