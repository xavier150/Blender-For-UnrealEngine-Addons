import bpy

def get_spline_unreal_component(spline: bpy.types.Object):
    # Engin ref:
    spline_type = spline.bfu_desired_spline_type
    if spline_type == "SPLINE":
        return "/Script/Engine.SplineComponent"
    elif spline_type == "CUSTOM":
        return spline.bfu_custom_spline_component
    