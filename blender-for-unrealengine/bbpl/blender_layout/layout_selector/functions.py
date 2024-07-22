# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy
from typing import List
from . import types





def add_string_selector(property_name, property_selector_name, default: str="", name: str="", description: str="", items=[]) -> types.StringSelector:
    my_string_selector = types.StringSelector(property_name, property_selector_name)
    my_string_selector.name = name
    my_string_selector.default = default
    my_string_selector.description = description
    my_string_selector.items = items
    my_string_selector.create_propertys()
    return my_string_selector

def draw_string_selector(owner, layout: bpy.types.UILayout, prop_name = "my_prop_id", selector_prop_name = "my_porp_id_selector", icon = "PREFERENCES"):
    row = layout.row(align=True)
    row.prop(owner, prop_name)
    row.prop(owner, selector_prop_name, text="", icon=icon, icon_only=True)
    return row