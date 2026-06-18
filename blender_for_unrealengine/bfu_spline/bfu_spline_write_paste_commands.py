# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import Optional, List, Dict, Any, Tuple
import bpy
from . import bfu_spline_data
from . import bfu_spline_unreal_utils
from . import bfu_spline_write_text
from .. import bbpl

def add_spline_to_command(spline: bpy.types.Object, pre_bake_spline: bfu_spline_data.BFU_SplinesList) -> Optional[str]:
    if spline.type == "CURVE":

        t = ""

        # First I get the spline data.
        # This is a very bad way to do this. I need do a new python file specific to spline with class to get data.
        data: Dict[str, Any] = bfu_spline_write_text.write_spline_points_data(spline, pre_bake_spline)

        # Engine ref:
        target_spline_component = bfu_spline_unreal_utils.get_spline_unreal_component(spline)
        ue_format_spline_list: List[str] = pre_bake_spline.get_ue_format_spline_list()

        for x, spline_key in enumerate(data["simple_splines"]):
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
            t += "   " + f"bShouldVisualizeScale=True" + "\n"
            t += "   " + f"RelativeLocation=(X=0.000000,Y=0.000000,Z=0.000000)" + "\n"

            # Close
            t += "" + "End Object" + "\n"
        return t
    return None

def get_spline_unreal_clipboard(objs: List[bpy.types.Object]) -> Tuple[bool, str, str]:
    # Return (success, command)
    save_select = bbpl.save_data.select_save.UserSelectSave()
    save_select.save_current_select()

    success = False
    command = ""
    report = ""
    add_spline_num = 0

    splines: List[bpy.types.Object] = []
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
        add_command = add_spline_to_command(spline, pre_bake_spline.get_evaluate_spline_data(spline))
        if add_command:
            t += add_command
            add_spline_num += 1

    success = True
    command = t
    report = str(add_spline_num) + " Spline(s) copied. Paste in Unreal Engine scene for import the spline. (Use CTRL+V in Unreal viewport)"
    save_select.reset_select(use_names = True)
    return (success, command, report)