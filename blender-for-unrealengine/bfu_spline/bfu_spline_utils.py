import bpy
import json

def get_enum_splines_list():
    spline_types = [
        ("SPLINE", "Spline", "Regular Spline component."),
        ("CUSTOM", "Custom", "If you use an custom spline component."),
    ]
    return spline_types

def get_enum_splines_default():
    return "SPLINE"

def transform_point_data(points):
    transformed_points = []
    for point in points:
        point_parts = []
        for key, val in point.items():
            if isinstance(val, dict):  # Pour OutVal, ArriveTangent, LeaveTangent
                val_str = ",".join([f"{k}={v}" for k, v in val.items()])
                point_parts.append(f"{key}=({val_str})")
            else:  # Pour InVal, InterpMode
                point_parts.append(f"{key}={val}")
        transformed_points.append(f"({','.join(point_parts)})")
    return f"({','.join(transformed_points)})"

def json_to_ue_format(json_data):
    result_parts = []
    for spline, data in json_data.items():  # SplineCurves, ReparamTable, etc.
        if spline == "SplineCurves":
            spline_parts = []
            for key, value in data.items():  # Position, Rotation, Scale
                points = transform_point_data(value["Points"])
                spline_parts.append(f"{key}=(Points={points})")
            result_parts.append(f"SplineCurves=({', '.join(spline_parts)})")
        else:  # Pour ReparamTable ou autres éléments similaires
            points = transform_point_data(data["Points"])
            result_parts.append(f"{spline}=(Points={points})")
    return ", ".join(result_parts)