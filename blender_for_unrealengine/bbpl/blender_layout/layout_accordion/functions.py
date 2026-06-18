# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import typing
from typing import Optional, Tuple
from . import types


def add_ui_accordion(name: str=""):
    return bpy.props.PointerProperty(type=types.get_layout_accordion_class(), name=name)  # type: ignore

def get_accordion(data: typing.Any, property: str) -> Optional[types.CustomAccordionUI_PropertyGroup]:
    prop = getattr(data, property, None)
    if isinstance(prop, types.CustomAccordionUI_PropertyGroup):
        return prop
    else:
        print(f"The property '{property}' was not found.")
        return None

def draw_accordion(layout: bpy.types.UILayout, data: typing.Any, property: str) -> Tuple[Optional[bpy.types.UILayout], Optional[bpy.types.UILayout]]:
    prop = getattr(data, property, None)
    if isinstance(prop, types.CustomAccordionUI_PropertyGroup):
        return prop.draw(layout)
        
    else:
        print(f"The property '{property}' was not found.")
        return None, None
