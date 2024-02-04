import bpy
import json
from .. import bbpl

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
        convert_curve_to_bezier(obj, curve_resolution)

def convert_curve_to_bezier(obj: bpy.types.Object, curve_resolution=12):
    context = bpy.context
    if obj.type == 'CURVE':
        # Définir la résolution_u pour la courbe
        for spline in obj.data.splines:
            spline.resolution_u = curve_resolution
        
        # Sélectionner l'objet pour la conversion
        bbpl.utils.select_specific_object(obj)
        
        # Convertir en Mesh
        bpy.ops.object.convert(target='MESH')

        # Convertir à nouveau en Curve
        bpy.ops.object.convert(target='CURVE')
        
        # Définir le type de spline en 'BEZIER'
        bbpl.utils.select_specific_object(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='BEZIER')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.object.mode_set(mode='OBJECT')

def create_resampled_spline(spline_data: bpy.types.Spline, curve_resolution=12):
    # Créer un nouveau bloc de données courbe
    new_curve_data = bpy.data.curves.new(name="ResampledCurve", type='CURVE')
    new_curve_data.dimensions = '3D'
    
    # Ajouter une nouvelle spline au bloc de données courbe en fonction du type de la spline source
    if spline_data.type == 'BEZIER':
        new_spline = new_curve_data.splines.new(type='BEZIER')
        new_spline.bezier_points.add(len(spline_data.bezier_points) - 1)  # Ajuster le nombre de points
        
        # Copier les points de la spline Bézier source
        for i, bp in enumerate(spline_data.bezier_points):
            new_bp = new_spline.bezier_points[i]
            new_bp.co = bp.co
            new_bp.handle_left = bp.handle_left
            new_bp.handle_left_type = bp.handle_left_type
            new_bp.handle_right = bp.handle_right
            new_bp.handle_right_type = bp.handle_right_type

        new_spline.use_cyclic_u = spline_data.use_cyclic_u
        new_spline.resolution_u = spline_data.resolution_u
        new_spline.tilt_interpolation = spline_data.tilt_interpolation
        new_spline.radius_interpolation = spline_data.radius_interpolation
        new_spline.use_smooth = spline_data.use_smooth

    elif spline_data.type == 'NURBS':
        new_spline = new_curve_data.splines.new(type='NURBS')
        new_spline.points.add(len(spline_data.points) - 1)  # Ajuster le nombre de points
        
        # Copier les points de la spline NURBS source
        for i, point in enumerate(spline_data.points):
            new_point = new_spline.points[i]
            new_point.co = point.co  # copie les coordonnées et le poids (w)
            new_point.weight = point.weight
            
        new_spline.use_cyclic_u = spline_data.use_cyclic_u
        new_spline.use_bezier_u = spline_data.use_bezier_u
        new_spline.use_endpoint_u = spline_data.use_endpoint_u
        new_spline.order_u = spline_data.order_u
        new_spline.resolution_u = spline_data.resolution_u
        new_spline.use_smooth = spline_data.use_smooth
            
    else:
        # Ajouter une gestion pour d'autres types si nécessaire
        print(f"Le type de spline {spline_data.type} n'est pas supporté.")
        return
    
    # Créer un nouvel objet courbe avec ce bloc de données courbe
    new_curve_obj = bpy.data.objects.new("ResampledCurveObject", new_curve_data)
    
    # Ajouter l'objet à la scène active
    bpy.context.collection.objects.link(new_curve_obj)
    convert_curve_to_bezier(new_curve_obj, curve_resolution)
    return new_curve_obj