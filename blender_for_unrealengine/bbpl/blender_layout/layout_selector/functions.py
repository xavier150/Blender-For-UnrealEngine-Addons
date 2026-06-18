# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import List, Callable, Optional, Any
from . import types

def add_string_selector(
    property_name: str, 
    property_selector_name: str, 
    default: str="", 
    name: str="", 
    description: str="", 
    items: List[Any] = [], 
    update: Optional[Callable[..., None]] = None
) -> types.StringSelector:
    my_string_selector = types.StringSelector(property_name, property_selector_name)
    my_string_selector.name = name
    my_string_selector.default = default
    my_string_selector.description = description
    my_string_selector.items = items
    my_string_selector.update = update
    my_string_selector.create_properties()
    return my_string_selector

def draw_string_selector(
        owner: Any, 
        layout: bpy.types.UILayout, 
        prop_name: str = "my_prop_id", 
        selector_prop_name: str = "my_prop_id_selector", 
        icon: str = "PREFERENCES", 
        text: Optional[str] = None
    ) -> bpy.types.UILayout:

    prop_layout = layout.column(align=True)
    row = prop_layout.row(align=True)

    # Draw the properties
    if isinstance(text, str):
        row.prop(owner, prop_name, text=text)
    else:
        row.prop(owner, prop_name)
    
    row.prop(
        owner, 
        selector_prop_name, 
        text="", 
        icon=icon,  # type: ignore
        icon_only=True
        )
    # Draw warning when the property don't match the selector value
    string_value = getattr(owner, prop_name)
    if string_value != getattr(owner, selector_prop_name):
        prop_layout.label(text="Value not in list!", icon="ERROR")

    return prop_layout