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

def convert_select_curves_to_bezier(curve_resolution=12):
    context = bpy.context
    for obj in context.selected_objects:
        if obj.type == 'CURVE':
            # Définir la résolution_u pour la courbe
            for spline in obj.data.splines:
                spline.resolution_u = curve_resolution
            
            # Sélectionner l'objet pour la conversion
            context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Convertir en Mesh
            bpy.ops.object.convert(target='MESH')
            
            # Convertir à nouveau en Curve
            bpy.ops.object.convert(target='CURVE')
            
            # Définir le type de spline en 'BEZIER'
            bpy.ops.object.select_all(action='DESELECT')  # Désélectionner tout pour éviter les conflits
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.curve.select_all(action='SELECT')
            bpy.ops.curve.spline_type_set(tygpe='BEZIER')
            bpy.ops.curve.handle_type_set(type='AUTOMATIC')
            bpy.ops.object.mode_set(mode='OBJECT')