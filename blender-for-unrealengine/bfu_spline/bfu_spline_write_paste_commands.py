import bpy

from . import bfu_spline_data
from . import bfu_spline_unreal_utils
from . import bfu_spline_write_text



def AddSplineToCommand(spline: bpy.types.Object, pre_bake_spline: bfu_spline_data.BFU_SplineTracks = None):
    if spline.type == "CURVE":
        spline_type = spline.bfu_desired_spline_type

        t = ""
        # Get Spline Data
        scene = bpy.context.scene

        # First I get the spline data.
        # This is a very bad way to do this. I need do a new python file specific to spline with class to get data.
        data = bfu_spline_write_text.WriteSplineAnimationTracks(spline, pre_bake_spline)
        SplineName = spline.name

        # Engin ref:
        target_spline_component = bfu_spline_unreal_utils.get_spline_unreal_component(spline)

        # Component 
        t += "" + f"Begin Object Class={target_spline_component} Name={SplineName} ExportPath={target_spline_component}" + "\n"

        # Init SplineCurves
        t += "    " + data["SplineCurves"] + "\n"

        # Close
        t += "" + "End Object" + "\n"
        return t
    return None

def GetImportSplineScriptCommand(objs):
    # Return (success, command)
    scene = bpy.context.scene
    frame_current = scene.frame_current

    success = False
    command = ""
    report = ""
    add_spline_num = 0

    splines = []
    for obj in objs:
        if obj.type == "CURVE":
            splines.append(obj)

    if len(splines) == 0:
        report = "Please select at least one spline (Curve)."
        return (success, command, report)

    pre_bake_spline = bfu_spline_data.BFU_MultiSplineTracks()
    for spline in splines:
        pre_bake_spline.add_spline_to_evaluate(spline)
    pre_bake_spline.evaluate_all_splines()

    # And I apply the camrta data to the copy paste text.
    t = ""
    for spline in splines:
        add_command = AddSplineToCommand(spline, pre_bake_spline.get_evaluate_spline_data(obj))
        if add_command:
            t += add_command
            add_spline_num += 1

    success = True
    report = str(add_spline_num) + " Spline(s) copied. Paste in Unreal Engine scene for import the spline. (Use CTRL+V in Unreal viewport)"

    return (success, command, report)