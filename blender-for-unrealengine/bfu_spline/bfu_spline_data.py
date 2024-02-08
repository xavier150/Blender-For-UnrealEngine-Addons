import bpy
import math
import mathutils
from typing import Dict, Any
from . import bfu_spline_utils
from . import bfu_spline_unreal_utils
from .. import bps
from .. import bbpl
from .. import languages
from .. import bfu_basics
from .. import bfu_utils

def float_as_ue(float: float):
    return "{:.6f}".format(float)

def vector_as_ue(vector_data: mathutils.Vector):
    vector = {}
    vector["X"] = "{:.6f}".format(vector_data.x)
    vector["Y"] = "{:.6f}".format(vector_data.y)
    vector["Z"] = "{:.6f}".format(vector_data.z)
    return vector

class BFU_SimpleSplinePoint():
    
    def __init__(self, point_data, point_type):
        # Context stats
        scene = bpy.context.scene

        self.position = mathutils.Vector((0,0,0))
        self.handle_left = mathutils.Vector((0,0,0))
        self.handle_left_type = "FREE"
        self.handle_right = mathutils.Vector((0,0,0))
        self.handle_right_type = "FREE"  
        
        self.point_type = point_type

        if point_type in ["BEZIER"]:
            self.set_point_from_bezier(point_data)
        elif point_type in ["NURBS"]:
            print("NURBS curves need to be resampled!")
        elif point_type in ["POLY"]:
            self.set_point_from_poly(point_data)

    def set_point_from_bezier(self, point_data: bpy.types.BezierSplinePoint):
        self.handle_left = "VECTOR"
        self.handle_right = "VECTOR"
        self.position = point_data.co.copy()
        self.handle_left = point_data.handle_left.copy()
        self.handle_right = point_data.handle_right.copy()

    def set_point_from_poly(self, point_data: bpy.types.SplinePoint):
        self.handle_left = "VECTOR"
        self.handle_right = "VECTOR"
        real_position = mathutils.Vector((0,0,0))
        real_position.x = point_data.co.x
        real_position.y = point_data.co.y
        real_position.z = point_data.co.z
        self.position = real_position
        self.handle_left = real_position
        self.handle_right = real_position

    def get_ue_position(self):
        ue_position = self.position.copy()
        ue_position *= mathutils.Vector((1,-1,1))
        return ue_position
    
    def get_ue_handle_left(self):
        ue_handle_left = self.handle_left.copy()
        ue_handle_left -= self.position
        ue_handle_left *= mathutils.Vector((-3,3,-3))
        return ue_handle_left
    
    def get_ue_handle_right(self):
        ue_handle_right = self.handle_right.copy()
        ue_handle_right -= self.position
        ue_handle_right *= mathutils.Vector((3,-3,3))
        return ue_handle_right

    def get_ue_interp_curve_mode(self):
        if self.point_type in ["BEZIER"]:
            return "CIM_CurveUser"
        elif self.point_type in ["NURBS"]:
            return "CIM_CurveAuto"
        elif self.point_type in ["POLY"]:
            return "CIM_Linear" 

    def get_spline_point_as_dict(self) -> Dict[str, Any]:
        data = {}
        # Static data
        data["position"] = vector_as_ue(self.position)
        data["point_type"] = self.point_type
        return data



class BFU_SimpleSpline():

    def __init__(self, spline_data: bpy.types.Spline):
        # Context stats
        scene = bpy.context.scene

        self.spline_type = spline_data.type
        self.closed_loop = spline_data.use_cyclic_u
        self.spline_length = spline_data.calc_length(resolution=512) #512 is the res used in UE5 to calculate length.
        self.spline_points = []

        # Blender Spline Data
        # ...

        # Formated data for Unreal Engine
        # ...

        # Formated data for ArchVis Tools in Unreal Engine
        # ...

    def get_simple_spline_values_as_dict(self) -> Dict[str, Any]:
        data = {}
        # Static data
        data["spline_type"] = self.spline_type
        data["closed_loop"] = self.closed_loop
        data["points"] = []
        for spline_point in self.spline_points:
            data["points"].append(spline_point.get_spline_point_as_dict())

        return data
    

    def get_ue_format_spline(self):
        # handle right is leave Tangent in UE
        # handle left is arive Tangent in UE

        Position = {}
        Rotation = {}
        Scale = {}
        ReparamTable = {}
        Position["Points"] = []
        Rotation["Points"] = []
        Scale["Points"] = []
        ReparamTable["Points"] = []
        reparam_table_sample = 10

        spline_num = len(self.spline_points)
        spline_length = self.spline_length

        for x, spline_point in enumerate(self.spline_points):
            spline_point: BFU_SimpleSplinePoint
            point_location = {}
            point_rotation = {}
            point_scale = {}

            point_location["InVal"] = "{:.6f}".format(x)
            point_location["OutVal"] = vector_as_ue(spline_point.get_ue_position())
            point_location["ArriveTangent"] = vector_as_ue(spline_point.get_ue_handle_left())
            point_location["LeaveTangent"] = vector_as_ue(spline_point.get_ue_handle_right())
            point_location["InterpMode"] = spline_point.get_ue_interp_curve_mode()

            point_location["InVal"] = float_as_ue(x)
            point_rotation["OutVal"] = "(X=0.000000,Y=0.000000,Z=0.000000,W=1.000000)"
            point_rotation["ArriveTangent"] = "(X=0.000000,Y=0.000000,Z=0.000000,W=1.000000)"
            point_rotation["LeaveTangent"] = "(X=0.000000,Y=0.000000,Z=0.000000,W=1.000000)"
            point_rotation["InterpMode"] = spline_point.get_ue_interp_curve_mode()

            point_location["InVal"] = float_as_ue(x)
            point_scale["OutVal"] = "(X=1.000000,Y=1.000000,Z=1.000000)"
            point_scale["ArriveTangent"] = "(X=1.000000,Y=1.000000,Z=1.000000)"
            point_scale["LeaveTangent"] = "(X=1.000000,Y=1.000000,Z=1.000000)"
            point_scale["InterpMode"] = spline_point.get_ue_interp_curve_mode()
           
            Position["Points"].append(point_location)
            Position["bIsLooped"] = self.closed_loop
            Position["LoopKeyOffset"] = float_as_ue(1)
            Rotation["Points"].append(point_rotation)
            Rotation["bIsLooped"] = self.closed_loop
            Rotation["LoopKeyOffset"] = float_as_ue(spline_num)
            Scale["Points"].append(point_scale)
            Scale["bIsLooped"] = self.closed_loop
            Scale["LoopKeyOffset"] = float_as_ue(spline_num)

            for reparam_index in range(0, reparam_table_sample):
                reparam_table = {}
                spline_position_at_time = (reparam_index + reparam_table_sample*x + 1)/reparam_table_sample
                spline_length_at_time = spline_length*(reparam_index + reparam_table_sample*x + 1)/(reparam_table_sample*spline_num)
                InVal = spline_length_at_time
                OutVal = spline_position_at_time
                #print(float_as_ue(InVal), "->", float_as_ue(OutVal))
                reparam_table["InVal"] = float_as_ue(InVal)
                reparam_table["OutVal"] = float_as_ue(OutVal)
                ReparamTable["Points"].append(reparam_table)


        data = {}
        data["SplineCurves"] = {}
        data["SplineCurves"]["Position"] = Position
        data["SplineCurves"]["Rotation"] = Rotation
        data["SplineCurves"]["Scale"] = Scale
        data["SplineCurves"]["ReparamTable"] = ReparamTable
        str_data = bfu_spline_utils.json_to_ue_format(data)
        return str_data
    

    def evaluate_spline_data(self, spline_obj: bpy.types.Object, spline_data: bpy.types.Spline, index=0):
        
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        #print(f"Start evaluate spline_data index {str(index)}")
        counter = bps.utils.CounterTimer()
        
        if spline_data.type in ["POLY"]:
            for point in spline_data.points:
                point: bpy.types.SplinePoint
                self.spline_points.append(BFU_SimpleSplinePoint(point, spline_data.type))

        if spline_data.type in ["NURBS"]:
            
            # Duplicate and resample spline
            resampled_spline_obj = bfu_spline_utils.create_resampled_spline(spline_data, spline_obj.bfu_spline_resample_resolution)
            new_spline_data = resampled_spline_obj.data.splines[0]
            for point in new_spline_data.bezier_points:
                point: bpy.types.BezierSplinePoint
                self.spline_points.append(BFU_SimpleSplinePoint(point, new_spline_data.type))
            
            # Clear
            objects_to_remove = [resampled_spline_obj]
            data_to_remove = [resampled_spline_obj.data]
            bpy.data.batch_remove(objects_to_remove)
            bpy.data.batch_remove(data_to_remove)
            
        elif spline_data.type in ["BEZIER"]:
            for bezier_point in spline_data.bezier_points:
                bezier_point: bpy.types.BezierSplinePoint
                self.spline_points.append(BFU_SimpleSplinePoint(bezier_point, spline_data.type))

        #print("Evaluate index " + str(index) + " finished in " + counter.get_str_time())
        #print("-----")
        return

class BFU_SplinesList():

    def __init__(self, spline: bpy.types.Object):
        # Context stats
        scene = bpy.context.scene

        self.spline_name = spline.name
        self.desired_spline_type = spline.bfu_desired_spline_type
        self.ue_spline_component_class = bfu_spline_unreal_utils.get_spline_unreal_component(spline)
        self.simple_splines: Dict[int, BFU_SimpleSpline] = {}

    def get_spline_list_values_as_dict(self) -> Dict[str, Any]:
        data = {}
        # Static data
        data["spline_name"] = self.spline_name
        data["desired_spline_type"] = self.desired_spline_type
        data["ue_spline_component_class"] = self.ue_spline_component_class

        data["simple_splines"] = {}
        for x, simple_spline_key in enumerate(self.simple_splines):
            simple_spline: BFU_SimpleSpline = self.simple_splines[simple_spline_key]
            data["simple_splines"][x] = simple_spline.get_simple_spline_values_as_dict()

        return data
    
    def get_ue_format_spline_list(self):
        data = []
        for simple_spline_key in self.simple_splines:
            simple_spline: BFU_SimpleSpline = self.simple_splines[simple_spline_key]
            data.append(simple_spline.get_ue_format_spline())
        return data
    

    def evaluate_spline_obj_data(self, spline_obj: bpy.types.Object):
        
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        #print(f"Start evaluate spline {spline_obj.name}")
        counter = bps.utils.CounterTimer()
        
        for x, spline_data in enumerate(spline_obj.data.splines):
            simple_spline = self.simple_splines[x] = BFU_SimpleSpline(spline_data)
            simple_spline.evaluate_spline_data(spline_obj, spline_data, x)

        #print("Evaluate " + spline_obj.name + " finished in " + counter.get_str_time())
        #print("-----")
        return

 
class BFU_MultiSplineTracks():

    def __init__(self):
        self.splines_to_evaluate = []
        self.evaluate_splines: Dict[str, BFU_SplinesList] = {}

    def add_spline_to_evaluate(self, obj: bpy.types.Object):
        self.splines_to_evaluate.append(obj)


    def evaluate_all_splines(self):
        # Evalutate all splines at same time will avoid frames switch

        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        counter = bps.utils.CounterTimer()

        slms = bfu_utils.TimelineMarkerSequence()

        # Save scene data
        save_current_frame = scene.frame_current
        save_use_simplify = bpy.context.scene.render.use_simplify
        bpy.context.scene.render.use_simplify = True

        for spline in self.splines_to_evaluate:
            self.evaluate_splines[spline.name] = BFU_SplinesList(spline)

        print(f"Start evaluate {str(len(self.splines_to_evaluate))} spline(s).")
        for spline in self.splines_to_evaluate:
            evaluate = self.evaluate_splines[spline.name]
            evaluate.evaluate_spline_obj_data(spline)

        scene.frame_current = save_current_frame
        bpy.context.scene.render.use_simplify = save_use_simplify

    def get_evaluate_spline_data(self, obj: bpy.types.Object):
        return self.evaluate_splines[obj.name]
    
    def get_evaluate_spline_data_as_dict(self, obj: bpy.types.Object) -> Dict[str, Any]:
        data = {}
        data.update(self.evaluate_splines[obj.name].get_spline_list_values_as_dict())
        data.update(self.evaluate_splines[obj.name].get_spline_list_values_as_dict())
        return data