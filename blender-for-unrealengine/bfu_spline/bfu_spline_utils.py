import bpy

def get_enum_splines_list():
    spline_types = [
        ("SPLINE", "Spline", "Regular Spline component."),
        ("CUSTOM", "Custom", "If you use an custom spline component."),
    ]
    return spline_types

def get_enum_splines_default():
    return "SPLINE"

