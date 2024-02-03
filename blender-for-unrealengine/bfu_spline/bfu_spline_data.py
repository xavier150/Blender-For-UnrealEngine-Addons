import bpy
import math
from typing import Dict, Any
from . import bfu_spline_unreal_utils
from .. import bps
from .. import bbpl
from .. import languages
from .. import bfu_basics
from .. import bfu_utils



class BFU_SplineTracks():

    def __init__(self, spline: bpy.types.Object):
        # Context stats
        scene = bpy.context.scene

        self.spline_name = spline.name
        self.spline_type = spline.bfu_desired_spline_type
        self.ue_spline_component = bfu_spline_unreal_utils.get_spline_unreal_component(spline)

        # Blender Spline Data
        # ...

        # Formated data for Unreal Engine
        # ...

        # Formated data for ArchVis Tools in Unreal Engine
        # ...


    def get_spline_values_as_dict(self) -> Dict[str, Any]:
        data = {}
        # Static data
        data["spline_name"] = self.spline_name
        data["spline_type"] = self.spline_type
        data["ue_spline_component"] = self.ue_spline_component

        # Animated Tracks
        data["SplineCurves"] = str(-1)

        return data
    

    def evaluate_spline_data(self, spline):
        
        scene = bpy.context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        print(f"Start evaluate spline {spline.name}")
        counter = bps.utils.CounterTimer()
        


        print("Evaluate " + spline.name + " finished in " + counter.get_str_time())
        print("-----")
        return

 
class BFU_MultiSplineTracks():

    def __init__(self):
        self.splines_to_evaluate = []
        self.evaluate_splines: Dict[str, BFU_SplineTracks] = {}

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
            self.evaluate_splines[spline.name] = BFU_SplineTracks(spline)

        print(f"Start evaluate {str(len(self.splines_to_evaluate))} spline(s).")
        for spline in self.splines_to_evaluate:
            evaluate = self.evaluate_splines[spline.name]
            
            # Bake all frames
            evaluate.evaluate_spline_data(spline)

        scene.frame_current = save_current_frame
        bpy.context.scene.render.use_simplify = save_use_simplify

    def get_evaluate_spline_data(self, obj: bpy.types.Object):
        return self.evaluate_splines[obj.name]
    
    def get_evaluate_spline_data_as_dict(self, obj: bpy.types.Object) -> Dict[str, Any]:
        data = {}
        data.update(self.evaluate_splines[obj.name].get_spline_values_as_dict())
        data.update(self.evaluate_splines[obj.name].get_spline_values_as_dict())
        return data