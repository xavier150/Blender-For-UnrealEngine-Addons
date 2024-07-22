# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

import bpy
import json
from . import bfu_spline_config
from .. import bbpl
from .. import bfu_assets_manager

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
                points_data = ""
                points_data = f"Points={points}"

                loop_data = ""
                if "bIsLooped" in value and "LoopKeyOffset" in value:
                    bIsLooped = value["bIsLooped"]
                    LoopKeyOffset = value["LoopKeyOffset"]
                    loop_data = f"bIsLooped={bIsLooped},LoopKeyOffset={LoopKeyOffset}"

                spline_parts.append(f"{key}=({points_data},{loop_data})")


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
    if obj.type == 'CURVE':
        # Set curve resolution_u
        for spline in obj.data.splines:
            spline.resolution_u = curve_resolution
        
        # Select object for conversion
        bbpl.utils.select_specific_object(obj)
        
        # Convert to Mesh
        bpy.ops.object.convert(target='MESH')

        # Convert back to Curve
        bpy.ops.object.convert(target='CURVE')
        
        # Set spline type to 'BEZIER'
        bbpl.utils.select_specific_object(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='BEZIER')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.object.mode_set(mode='OBJECT')

def create_resampled_spline(spline_data: bpy.types.Spline, curve_resolution=12):
    # Create a new curve data block
    new_curve_data = bpy.data.curves.new(name="ResampledCurve", type='CURVE')
    new_curve_data.dimensions = '3D'
    
    # Add a new spline to the curve data block based on source spline type
    if spline_data.type == 'BEZIER':
        new_spline = new_curve_data.splines.new(type='BEZIER')
        new_spline.bezier_points.add(len(spline_data.bezier_points) - 1)  # Adjust number of points
        
        # Copy source Bezier spline points
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
        new_spline.points.add(len(spline_data.points) - 1)  # Adjust number of points
        
        # Copy source NURBS spline points
        for i, point in enumerate(spline_data.points):
            new_point = new_spline.points[i]
            new_point.co = point.co  # copy coordinates and weight (w)
            new_point.weight = point.weight
            
        new_spline.use_cyclic_u = spline_data.use_cyclic_u
        new_spline.use_bezier_u = spline_data.use_bezier_u
        new_spline.use_endpoint_u = spline_data.use_endpoint_u
        new_spline.order_u = spline_data.order_u
        new_spline.resolution_u = spline_data.resolution_u
        new_spline.use_smooth = spline_data.use_smooth
            
    else:
        # Add handling for other types if necessary
        print(f"Spline type {spline_data.type} is not supported.")
        return
    
    # Create a new curve object with this curve data block
    new_curve_obj = bpy.data.objects.new("ResampledCurveObject", new_curve_data)
    
    # Add object to the active scene
    bpy.context.collection.objects.link(new_curve_obj)
    convert_curve_to_bezier(new_curve_obj, curve_resolution)
    return new_curve_obj

def contain_nurbs_spline(obj: bpy.types.Object):
    if obj.type == "CURVE":
        for spline in obj.data.splines:
            if spline.type == "NURBS":
                return True
    return False


def is_spline(obj):
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type_name(obj) == bfu_spline_config.asset_type_name:
            return True
    return False