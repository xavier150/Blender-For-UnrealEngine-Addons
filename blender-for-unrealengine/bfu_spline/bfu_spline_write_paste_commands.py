import bpy
from . import bfu_spline_data
from . import bfu_spline_unreal_utils
from . import bfu_spline_write_text
from .. import bbpl

def AddSplineToCommand(spline: bpy.types.Object, pre_bake_spline: bfu_spline_data.BFU_SplinesList = None):
    if spline.type == "CURVE":
        spline_type = spline.bfu_desired_spline_type

        t = ""
        # Get Spline Data
        scene = bpy.context.scene

        # First I get the spline data.
        # This is a very bad way to do this. I need do a new python file specific to spline with class to get data.
        data = bfu_spline_write_text.WriteSplinePointsData(spline, pre_bake_spline)

        # Engin ref:
        target_spline_component = bfu_spline_unreal_utils.get_spline_unreal_component(spline)
        ue_format_spline_list = pre_bake_spline.get_ue_format_spline_list()

        for x, spline_key in enumerate(data["simple_splines"]):
            simple_spline: bfu_spline_data.BFU_SimpleSpline
            simple_spline = data["simple_splines"][spline_key]
            if x == 0:
                spline_name = spline.name
            else:
                spline_name = spline.name+str(x)
                

    
            # Component 
            t += "" + f"Begin Object Class={target_spline_component} Name=\"{spline_name}_GEN_VARIABLE\" ExportPath=\"{target_spline_component}'/Engine/Transient.{spline_name}_GEN_VARIABLE'\"" + "\n"

            # Init SplineCurves
            t += "   " + ue_format_spline_list[x] + "\n"
            t += "   " + f"bClosedLoop={simple_spline['closed_loop']}" + "\n"
            t += "   " + f"CreationMethod=Instance" + "\n"

            # Close
            t += "" + "End Object" + "\n"
        return t
    return None

def GetImportSplineScriptCommand(objs):
    # Return (success, command)
    scene = bpy.context.scene
    save_select = bbpl.utils.UserSelectSave()
    save_select.save_current_select()

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
    command = t
    report = str(add_spline_num) + " Spline(s) copied. Paste in Unreal Engine scene for import the spline. (Use CTRL+V in Unreal viewport)"
    save_select.reset_select_by_name()
    return (success, command, report)