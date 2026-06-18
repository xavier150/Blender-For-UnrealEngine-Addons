# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import math
import mathutils
from typing import Dict, Any, List, Union, TYPE_CHECKING, Optional, Tuple
from .. import bbpl
from .. import bpl
from . import bfu_spline_utils
from . import bfu_spline_unreal_utils

def float_as_ue(my_float: float) -> str:
    return "{:.6f}".format(my_float)

def vector_as_ue(vector_data: mathutils.Vector) -> Dict[str, str]:
    vector: Dict[str, str] = {}        
    vector["X"] = "{:.6f}".format(vector_data.x)
    vector["Y"] = "{:.6f}".format(vector_data.y)
    vector["Z"] = "{:.6f}".format(vector_data.z)
    return vector

def quad_as_ue(quad_data: mathutils.Quaternion) -> Dict[str, str]:
    quad: Dict[str, str] = {}
    quad["X"] = "{:.6f}".format(quad_data.x)
    quad["Y"] = "{:.6f}".format(quad_data.y)
    quad["Z"] = "{:.6f}".format(quad_data.z)
    quad["W"] = "{:.6f}".format(quad_data.w)
    return quad

class BFU_SimpleSplinePoint():

    def __init__(self, current_index: int, spline_owner: 'BFU_SimpleSpline', spline_obj: bpy.types.Object, point_data: Union[bpy.types.SplinePoint, bpy.types.BezierSplinePoint], point_type: str):

        """
        # Please notes:
        # Blender spline progress from Left handle to Right handle.
        # Unreal Engine spline progress from Arrive Tangent to Leave Tangent.
        # This means that the left handle in Blender is the "Arrive Tangent" in UE,
        # and the right handle in Blender is the "Leave Tangent" in UE.
        """

        # Spline context
        self.current_index: int = current_index
        self.spline_owner: 'BFU_SimpleSpline' = spline_owner

        # Context stats
        self.position: mathutils.Vector = mathutils.Vector((0,0,0))
        self.handle_left: mathutils.Vector = mathutils.Vector((0,0,0)) 
        self.handle_left_type = "FREE"
        self.handle_right: mathutils.Vector = mathutils.Vector((0,0,0)) 
        self.handle_right_type = "FREE"
        self.curve_roll: float = self.get_curve_roll(spline_obj, point_data)
        self.curve_radius: float = point_data.radius

        self.point_type = point_type

        if point_type in ["BEZIER"]:
            if isinstance(point_data, bpy.types.BezierSplinePoint):
                self.set_point_from_bezier(point_data)
        elif point_type in ["NURBS"]:
            print("NURBS curves need to be resampled!")
        elif point_type in ["POLY"]:
            if isinstance(point_data, bpy.types.SplinePoint):
                self.set_point_from_poly(point_data)



    def get_previous_point(self) -> Optional['BFU_SimpleSplinePoint']:
        return self.spline_owner.spline_points.get(self.current_index - 1)

    def get_next_point(self) -> Optional['BFU_SimpleSplinePoint']:
        return self.spline_owner.spline_points.get(self.current_index + 1)

    def get_curve_roll(self, spline_obj: bpy.types.Object, point_data: Union[bpy.types.SplinePoint, bpy.types.BezierSplinePoint]) -> float:
        if isinstance(point_data, bpy.types.BezierSplinePoint):
            if isinstance(spline_obj.data, bpy.types.Curve):
                # For the momment roll work only with Z_UP mode.
                # Need a way to evaluate the roll at spline points.
                # It possible to brut force using a PathDummy with Follow Path constraint but that very heavy...
                # Please.
                if spline_obj.data.twist_mode == 'Z_UP':
                    return point_data.tilt
        else:
            return point_data.tilt
            
        return 0.0
    
    def set_point_from_bezier(self, point_data: bpy.types.BezierSplinePoint):
        self.handle_left_type = "VECTOR"
        self.handle_right_type = "VECTOR"
        self.position = point_data.co.copy()
        self.handle_left = point_data.handle_left.copy()
        self.handle_right = point_data.handle_right.copy()

    def set_point_from_poly(self, point_data: bpy.types.SplinePoint):
        self.handle_left_type = "VECTOR"
        self.handle_right_type = "VECTOR"
        real_position = mathutils.Vector((0,0,0))
        real_position.x = point_data.co.x
        real_position.y = point_data.co.y
        real_position.z = point_data.co.z
        self.position = real_position
        self.handle_left = real_position
        self.handle_right = real_position

    def get_ue_position(self) -> mathutils.Vector:
        """
        Converts the Blender point position to Unreal.
        - Applies Y symmetry (Right-handed → Left-handed)
        - Applies user scale
        """
        ue_position = self.position.copy()
        ue_position.x = self.position.x
        ue_position.y = -self.position.y  # Invert Y
        ue_position.z = self.position.z

        vector_scale = (
            mathutils.Vector((1, 1, 1))
            if TYPE_CHECKING else
                mathutils.Vector(bpy.context.scene.bfu_spline_vector_scale)
        )
        ue_position *= vector_scale
        return ue_position

    def get_arrive_tangent_loc(self) -> mathutils.Vector:
        """
        NOTES:
        - Unreal Engine requires the 'ArriveTangent' to be the *inverse* of the actual direction vector.
        - Therefore, in Blender: (handle_left - position) must become (position - handle_left)
        - Unreal multiplies tangent magnitude by 3.0 internally.
        - Y-axis is flipped (Blender is right-handed Z-up; Unreal is left-handed Z-up pre-5.6)
        - Apply vector scaling after conversion.
        """
        tangent = (self.position - self.handle_left).copy()
        tangent.x = tangent.x * 3.0
        tangent.y = -tangent.y * 3.0  # Invert Y
        tangent.z = tangent.z * 3.0

        vector_scale = (
            mathutils.Vector((1, 1, 1))
            if TYPE_CHECKING else
            mathutils.Vector(bpy.context.scene.bfu_spline_vector_scale)
        )
        return tangent * vector_scale

    def get_leave_tangent_loc(self) -> mathutils.Vector:
        """
        Same for the right (outgoing) tangent
        """
        tangent = (self.handle_right - self.position).copy()
        tangent.x = tangent.x * 3.0
        tangent.y = -tangent.y * 3.0
        tangent.z = tangent.z * 3.0

        vector_scale = (
            mathutils.Vector((1, 1, 1))
            if TYPE_CHECKING else
            mathutils.Vector(bpy.context.scene.bfu_spline_vector_scale)
        )
        return tangent * vector_scale


    def get_ue_point_rotation(self) -> Tuple[float, float, float]:
        return bfu_spline_utils.get_spline_unreal_rotation(
            self.position, 
            self.handle_right, 
            self.curve_roll
        )

    def get_out_val_rotation(self) -> mathutils.Quaternion:
        roll, pitch, yaw = self.get_ue_point_rotation()  # mathutils.Quaternion (WXYZ)

        # Normalize angles like Unreal
        degrees_roll = math.degrees(roll)
        degrees_pitch = -math.degrees(pitch)
        degrees_yaw = math.degrees(yaw)

        in_up_vector = self.rotator_to_up_vector_fixed(degrees_roll, degrees_pitch, degrees_yaw)
        default_up = mathutils.Vector((0, 0, 1))
        
        if in_up_vector.dot(default_up) >= 1.0:
            # Same direction
            return mathutils.Quaternion()
        elif in_up_vector.dot(default_up) <= -1.0:
            # Opposite direction
            # Choose an arbitrary axis perpendicular to default_up
            ortho = mathutils.Vector((1, 0, 0)) if abs(default_up.x) < 0.99 else mathutils.Vector((0, 1, 0))
            axis: mathutils.Vector = default_up.cross(ortho)  # type: ignore
            axis = axis.normalized()
            return mathutils.Quaternion(axis, math.pi)

        return default_up.rotation_difference(in_up_vector)


    def get_arrive_tangent_rotation(self) -> mathutils.Quaternion:
        """
        Unreal Engine stores Rotation tangents (ArriveTangent and LeaveTangent)
        as *quaternion deltas*, linearly interpolated between neighboring keys.

        - They are not rotation_differences!
        - Unreal internally uses: Tangent = (NeighborQuat - CurrentQuat) * 0.5
        - Then stores: CurrentQuat + Tangent → as tangent key

        This function mimics that: (Next/Prev - Current) * 0.5 + Current
        """
        return self.get_leave_tangent_rotation()

    @staticmethod
    def rotator_to_up_vector_fixed(roll: float, pitch: float, yaw: float) -> mathutils.Vector:
        def deg_to_rad(deg: float) -> float: return deg * math.pi / 180.0
        def normalize(a: float) -> float: return ((a + 180) % 360) - 180

        # Unreal: Pitch left-handed, Roll left-handed, Yaw normal
        pitch = deg_to_rad(-normalize(pitch))
        yaw   = deg_to_rad(normalize(yaw))
        roll  = deg_to_rad(-normalize(roll))  # invert roll too

        cz, sz = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        m = [
            [cz*cp, cz*sp*sr - sz*cr, cz*sp*cr + sz*sr],
            [sz*cp, sz*sp*sr + cz*cr, sz*sp*cr - cz*sr],
            [ -sp ,       cp*sr     ,      cp*cr     ],
        ]
        up = (
            round(m[0][2], 3),
            round(m[1][2], 3),
            round(m[2][2], 3),
        )
        return mathutils.Vector((up[0], up[1], up[2]))

    def get_leave_tangent_rotation(self) -> mathutils.Quaternion:
        next_p = self.get_next_point()
        prev_p = self.get_previous_point()
        if next_p is None or prev_p is None:
            # Use the point rotation at spline start and end
            roll, pitch, yaw = self.get_ue_point_rotation()
            return bfu_spline_utils.get_as_unreal_quaternion(roll, pitch, yaw)

        roll, pitch, yaw = self.get_ue_point_rotation()  # mathutils.Quaternion (WXYZ)

        # Normalize angles like Unreal
        degrees_roll = math.degrees(roll)
        degrees_pitch = -math.degrees(pitch)
        degrees_yaw = math.degrees(yaw)

        spline_rot_up_vector = self.rotator_to_up_vector_fixed(degrees_roll, degrees_pitch, degrees_yaw)

        spline_rot_up_vector *= 0.5
        spline_z_up_vector = mathutils.Vector((0, 0, 0.5))  # Unreal Engine Z-up vector
        tan = spline_z_up_vector + (spline_rot_up_vector - spline_z_up_vector) * 0.5  # Calculate the tangent vector

        # Save the vector in a quaternion format.
        # Unreal Engine uses a quaternion to store the tangent vector here.

        # X -> Y
        # -Y -> X
        # Z -> w
        quat = mathutils.Quaternion((0, 0, 0, 1))
        quat.w = tan.z
        quat.x = -tan.y
        quat.y = tan.x
        quat.z = 0
        return quat


    def get_human_readable_ue_rotation(self) -> str:
        """
        Returns the angles in degrees (Roll, Pitch, Yaw) in Unreal format
        from a quaternion, respecting the ZYX rotation order.
        """
        roll, pitch, yaw = self.get_ue_point_rotation()

        str_yaw = f"{math.degrees(yaw):.2f}"
        str_pitch = f"{-math.degrees(pitch):.2f}"
        str_roll = f"{math.degrees(roll):.2f}"

        return f"Roll: {str_roll}, Pitch: {str_pitch}, Yaw: {str_yaw}"

    def get_ue_scale(self) -> mathutils.Vector:
        radius = self.curve_radius
        ue_scale = mathutils.Vector((radius, radius, radius))
        return ue_scale

    def get_ue_interp_curve_mode(self) -> str:
        if self.point_type in ["BEZIER"]:
            return "CIM_CurveUser"
        elif self.point_type in ["NURBS"]:
            return "CIM_CurveAuto"
        elif self.point_type in ["POLY"]:
            return "CIM_Linear" 
        return "CIM_CurveAuto"

    def get_spline_point_as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        # Static data
        data["position"] = vector_as_ue(self.position)
        data["point_type"] = self.point_type
        return data


class BFU_SimpleSpline():

    def __init__(self, spline_data: bpy.types.Spline):
        # Context stats
        self.spline_type = spline_data.type
        self.closed_loop = spline_data.use_cyclic_u
        self.spline_length = spline_data.calc_length(resolution=512) #512 is the res used in UE5 to calculate length.
        self.spline_points: Dict[int, BFU_SimpleSplinePoint] = {}

        # Blender Spline Data
        # ...

        # Formated data for Unreal Engine
        # ...

        # Formated data for ArchVis Tools in Unreal Engine
        # ...

    def get_simple_spline_values_as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        # Static data
        data["spline_type"] = self.spline_type
        data["closed_loop"] = self.closed_loop
        points: List[Any] = []
        for spline_point_index in self.spline_points:
            points.append(self.spline_points[spline_point_index].get_spline_point_as_dict())
        data["points"] = points

        return data
    

    def get_ue_format_spline(self) -> str:
        # handle right is leave Tangent in UE
        # handle left is arive Tangent in UE

        Position: Dict[str, Any] = {}
        Rotation: Dict[str, Any] = {}
        Scale: Dict[str, Any] = {}
        ReparamTable: Dict[str, Any] = {}
        Position["Points"] = []
        Rotation["Points"] = []
        Scale["Points"] = []
        ReparamTable["Points"] = []
        reparam_table_sample = 10

        spline_num = len(self.spline_points)
        spline_length = self.spline_length


        Position_Points: List[Any] = []
        Rotation_Points: List[Any] = []
        Scale_Points: List[Any] = []
        ReparamTable_Points: List[Any] = []

        for spline_point_index in self.spline_points:

            spline_point: BFU_SimpleSplinePoint = self.spline_points[spline_point_index]
            point_location = {}
            point_rotation = {}
            point_scale = {}

            point_location["InVal"] = float_as_ue(spline_point_index)
            point_location["OutVal"] = vector_as_ue(spline_point.get_ue_position())
            point_location["ArriveTangent"] = vector_as_ue(spline_point.get_arrive_tangent_loc())
            point_location["LeaveTangent"] = vector_as_ue(spline_point.get_leave_tangent_loc())
            point_location["InterpMode"] = spline_point.get_ue_interp_curve_mode()

            point_rotation["InVal"] = float_as_ue(spline_point_index)
            point_rotation["OutVal"] = quad_as_ue(spline_point.get_out_val_rotation())
            point_rotation["ArriveTangent"] = quad_as_ue(spline_point.get_arrive_tangent_rotation())
            point_rotation["LeaveTangent"] = quad_as_ue(spline_point.get_leave_tangent_rotation())
            point_rotation["InterpMode"] = spline_point.get_ue_interp_curve_mode()

            point_scale["InVal"] = float_as_ue(spline_point_index)
            point_scale["OutVal"] = vector_as_ue(spline_point.get_ue_scale())
            point_scale["ArriveTangent"] = vector_as_ue(mathutils.Vector((1, 1, 1)))
            point_scale["LeaveTangent"] = vector_as_ue(mathutils.Vector((1, 1, 1)))
            point_scale["InterpMode"] = spline_point.get_ue_interp_curve_mode()
           
            Position_Points.append(point_location)
            Position["bIsLooped"] = self.closed_loop
            Position["LoopKeyOffset"] = float_as_ue(1)
            Rotation_Points.append(point_rotation)
            Rotation["bIsLooped"] = self.closed_loop
            Rotation["LoopKeyOffset"] = float_as_ue(spline_num)
            Scale_Points.append(point_scale)
            Scale["bIsLooped"] = self.closed_loop
            Scale["LoopKeyOffset"] = float_as_ue(spline_num)

            for reparam_index in range(0, reparam_table_sample):
                reparam_table = {}
                spline_position_at_time = (reparam_index + reparam_table_sample*spline_point_index + 1)/reparam_table_sample
                spline_length_at_time = spline_length*(reparam_index + reparam_table_sample*spline_point_index + 1)/(reparam_table_sample*spline_num)
                InVal = spline_length_at_time
                OutVal = spline_position_at_time
                #print(float_as_ue(InVal), "->", float_as_ue(OutVal))
                reparam_table["InVal"] = float_as_ue(InVal)
                reparam_table["OutVal"] = float_as_ue(OutVal)
                ReparamTable_Points.append(reparam_table)

        Position["Points"] = Position_Points
        Rotation["Points"] = Rotation_Points
        Scale["Points"] = Scale_Points
        ReparamTable["Points"] = ReparamTable_Points

        data: Dict[str, Any] = {}
        data["SplineCurves"] = {}
        data["SplineCurves"]["Position"] = Position
        data["SplineCurves"]["Rotation"] = Rotation
        data["SplineCurves"]["Scale"] = Scale
        data["SplineCurves"]["ReparamTable"] = ReparamTable
        str_data = bfu_spline_utils.json_to_ue_format(data)
        return str_data
    

    def evaluate_spline_data(self, spline_obj: bpy.types.Object, spline_data: bpy.types.Spline, index: int = 0):

        # Clear previous data
        self.spline_points = {}
        
        if spline_data.type in ["POLY"]:
            for i, poly_point in enumerate(spline_data.points):
                poly_point: bpy.types.SplinePoint
                self.spline_points[i] = BFU_SimpleSplinePoint(i, self, spline_obj, poly_point, spline_data.type)

        elif spline_data.type in ["NURBS"]:
            
            # Duplicate and resample spline
            if TYPE_CHECKING:
                spline_resample_resolution: int = 12
            else:
                spline_resample_resolution: int = spline_obj.bfu_spline_resample_resolution

            resampled_spline_obj: Optional[bpy.types.Object] = bfu_spline_utils.create_resampled_spline(spline_data, spline_resample_resolution)
            if resampled_spline_obj and resampled_spline_obj.data:
                if isinstance(resampled_spline_obj.data, bpy.types.Curve):
                    new_spline_data = resampled_spline_obj.data.splines[0]
                    for i, nurbs_point in enumerate(new_spline_data.bezier_points):
                        nurbs_point: bpy.types.BezierSplinePoint
                        self.spline_points[i] = BFU_SimpleSplinePoint(i, self, spline_obj, nurbs_point, new_spline_data.type)

                # Clear temporary objects
                objects_to_remove: List[bpy.types.Object] = [resampled_spline_obj]
                data_to_remove: List[bpy.types.ID] = [resampled_spline_obj.data]
                bpy.data.batch_remove(objects_to_remove)
                bpy.data.batch_remove(data_to_remove)
            
        elif spline_data.type in ["BEZIER"]:
            for i, bezier_point in enumerate(spline_data.bezier_points):
                bezier_point: bpy.types.BezierSplinePoint
                self.spline_points[i] = BFU_SimpleSplinePoint(i, self, spline_obj, bezier_point, spline_data.type)

        #print("Evaluate index " + str(index) + " finished in " + counter.get_str_time())
        #print("-----")
        return


class BFU_SplinesList():

    def __init__(self, spline: bpy.types.Object):
        # Context stats
        self.spline_name: str = spline.name
        self.desired_spline_type: str = spline.bfu_desired_spline_type  # type: ignore
        self.ue_spline_component_class: str = bfu_spline_unreal_utils.get_spline_unreal_component(spline)
        self.simple_splines: Dict[int, BFU_SimpleSpline] = {}

    def get_spline_list_values_as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        # Static data
        data["spline_name"] = self.spline_name
        data["desired_spline_type"] = self.desired_spline_type
        data["ue_spline_component_class"] = self.ue_spline_component_class

        data["simple_splines"] = {}
        for x, simple_spline_key in enumerate(self.simple_splines):
            simple_spline: BFU_SimpleSpline = self.simple_splines[simple_spline_key]
            data["simple_splines"][x] = simple_spline.get_simple_spline_values_as_dict()

        return data

    def get_ue_format_spline_list(self) -> List[str]:
        data: List[str] = []
        for simple_spline_key in self.simple_splines:
            simple_spline: BFU_SimpleSpline = self.simple_splines[simple_spline_key]
            data.append(simple_spline.get_ue_format_spline())
        return data
    

    def evaluate_spline_obj_data(self, spline_obj: bpy.types.Object) -> None:
        if spline_obj and spline_obj.data and isinstance(spline_obj.data, bpy.types.Curve):
            for x, spline_data in enumerate(spline_obj.data.splines):
                simple_spline = self.simple_splines[x] = BFU_SimpleSpline(spline_data)
                simple_spline.evaluate_spline_data(spline_obj, spline_data, x)

        return
 

class BFU_MultiSplineTracks():

    def __init__(self):
        self.splines_to_evaluate: List[bpy.types.Object] = []
        self.evaluate_splines: Dict[str, BFU_SplinesList] = {}

    def add_spline_to_evaluate(self, obj: bpy.types.Object):
        self.splines_to_evaluate.append(obj)


    def evaluate_all_splines(self, preview: bool = False, print_counter: bool = False):
        # Evaluate all splines at the same time to avoid frame switching

        scene = bpy.context.scene
        if scene is None:
            return

        counter = bpl.utils.CounterTimer()
        save_simplfy = bbpl.utils.SaveUserRenderSimplify()

        # Save scene data
        if not preview:
            save_simplfy.save_scene()
            save_simplfy.simplify_scene()

        for spline in self.splines_to_evaluate:
            self.evaluate_splines[spline.name] = BFU_SplinesList(spline)

        #print(f"Start evaluate {str(len(self.splines_to_evaluate))} spline(s).")
        for spline in self.splines_to_evaluate:
            evaluate = self.evaluate_splines[spline.name]
            evaluate.evaluate_spline_obj_data(spline)

        if not preview:
            save_simplfy.reset_scene()

        if print_counter:
            print("Evaluate all splines finished in " + counter.get_str_time())
            print("-----")


    def get_evaluate_spline_data(self, obj: bpy.types.Object):
        return self.evaluate_splines[obj.name]
    
    def get_evaluate_spline_data_as_dict(self, obj: bpy.types.Object) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        data.update(self.evaluate_splines[obj.name].get_spline_list_values_as_dict())
        data.update(self.evaluate_splines[obj.name].get_spline_list_values_as_dict())
        return data