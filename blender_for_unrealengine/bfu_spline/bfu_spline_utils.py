# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List, Dict, Any, Tuple, Optional
import math
import mathutils
from .. import bbpl
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType

def get_spline_unreal_rotation(
    point_position: mathutils.Vector, 
    right_handle: mathutils.Vector, 
    tilt_rad: float
) -> Tuple[float, float, float]:
    """
    Returns a quaternion aligned with the forward direction (from point_position to right_handle),
    and applies a tilt angle as roll. This matches Unreal Engine 5.6's conventions.

    NOTES:
    - Unreal Engine 5.6 uses a **left-handed**, **Z-up**, **X-forward** coordinate system.
    - Blender uses **right-handed**, **Z-up**, **-Y-forward** system.
    - Unreal applies rotations in ZYX order (Yaw → Pitch → Roll).
    - When exporting from Blender, you must flip the Y axis of vectors to match Unreal space.
    - The spline point rotation in Unreal is aligned to the **Leave Tangent**, which corresponds to **handle_right** in Blender.
    """

    """
    Returns a quaternion aligned with the forward direction (from point_position to right_handle),
    and applies a tilt angle as roll. This matches Unreal Engine 5.6's conventions.

    NOTES:
    - Unreal Engine 5.6 uses a left-handed, Z-up, X-forward coordinate system.
    - Blender uses right-handed, Z-up, -Y-forward system.
    """
    bebug_print = False

    direction = (right_handle - point_position).normalized()

    if direction.length == 0:
        return (0.0, 0.0, 0.0)

    # Convert to Unreal space: flip Y
    direction = mathutils.Vector((direction.x, -direction.y, direction.z))

    yaw = math.atan2(direction.y, direction.x)
    xy_len = math.sqrt(direction.x ** 2 + direction.y ** 2)
    pitch = -math.atan2(direction.z, xy_len)
    roll = tilt_rad
    roll = ((roll + math.pi) % (2 * math.pi)) - math.pi

    if bebug_print:
        print("Yaw:", math.degrees(yaw), "Pitch:", math.degrees(pitch), "Roll:", math.degrees(roll))

    return roll, pitch, yaw

def get_as_unreal_quaternion(roll: float, pitch: float, yaw: float) -> mathutils.Quaternion:
    # Invert pitch to compensate Blender's right-handed system
    euler = mathutils.Euler((roll, -pitch, yaw), 'ZYX')
    quat = euler.to_quaternion()
    quat.normalize()
    return quat

def transform_point_data(points: List[Any]) -> str:
    transformed_points: List[str] = []
    for point in points:
        point_parts: List[str] = []
        for key, val in point.items():
            if isinstance(val, dict):  # Pour OutVal, ArriveTangent, LeaveTangent
                val_str = ",".join([f"{k}={v}" for k, v in val.items()])  # type: ignore
                point_parts.append(f"{key}=({val_str})")
            else:  # Pour InVal, InterpMode
                point_parts.append(f"{key}={val}")
        transformed_points.append(f"({','.join(point_parts)})")
    return f"({','.join(transformed_points)})"


def json_to_ue_format(json_data: Dict[str, Any]) -> str:
    result_parts: List[str] = []
    for spline, data in json_data.items():  # SplineCurves, ReparamTable, etc.
        if spline == "SplineCurves":
            spline_parts: List[str] = []
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
        else:  # For ReparamTable or similar elements
            points = transform_point_data(data["Points"])
            result_parts.append(f"{spline}=(Points={points})")
    return ", ".join(result_parts)

def convert_select_curves_to_bezier(curve_resolution: int = 12):
    context = bpy.context
    for obj in context.selected_objects:
        convert_curve_to_bezier(obj, curve_resolution)

def convert_curve_to_bezier(obj: bpy.types.Object, curve_resolution: int = 12):
    if obj.type == 'CURVE':
        if isinstance(obj.data, bpy.types.Curve):
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

def create_resampled_spline(spline_data: bpy.types.Spline, curve_resolution: int = 12) -> Optional[bpy.types.Object]:
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
        return None

    # Create a new curve object with this curve data block
    new_curve_obj = bpy.data.objects.new("ResampledCurveObject", new_curve_data)
    
    # Add object to the active scene
    if bpy.context.collection:
        bpy.context.collection.objects.link(new_curve_obj)
    convert_curve_to_bezier(new_curve_obj, curve_resolution)
    return new_curve_obj

def contain_nurbs_spline(obj: bpy.types.Object) -> bool:
    if obj.type == "CURVE":
        if isinstance(obj.data, bpy.types.Curve):
            for spline in obj.data.splines:
                if spline.type == "NURBS":
                    return True
    return False


def is_spline(obj: bpy.types.Object) -> bool:
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type(obj) == AssetType.SPLINE:
            return True
    return False