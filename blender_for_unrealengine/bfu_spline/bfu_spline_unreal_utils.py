# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from . import bfu_spline_props

def get_spline_unreal_component(spline: bpy.types.Object) -> str:
    # Engin ref:
    spline_type = spline.bfu_desired_spline_type  # type: ignore
    if spline_type == bfu_spline_props.BFU_SplineDesiredComponent.SPLINE.value:
        return "/Script/Engine.SplineComponent"
    else:
        return spline.bfu_custom_spline_component  # type: ignore
    