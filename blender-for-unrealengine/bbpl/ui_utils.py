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


def layout_scene_section(layout, prop_name, prop_label):
    """
    Add a collapsible section in the Blender UI layout for a scene property.
    """
    scene = bpy.context.scene
    expanded = getattr(scene, prop_name) #Old expanded = eval("scene." + prop_name)
    tria_icon = "TRIA_DOWN" if expanded else "TRIA_RIGHT"
    layout.row().prop(scene, prop_name, icon=tria_icon, icon_only=True, text=prop_label, emboss=False)
    return expanded


def get_icon_by_group_theme(theme_enum):
    """
    Get the icon name based on a group theme enum value.
    """
    if theme_enum == "RED":
        return "COLORSET_01_VEC"
    elif theme_enum == "BLUE":
        return "COLORSET_04_VEC"
    elif theme_enum == "YELLOW":
        return "COLORSET_09_VEC"
    elif theme_enum == "PURPLE":
        return "COLORSET_06_VEC"
    elif theme_enum == "GREEN":
        return "COLORSET_03_VEC"
    return "NONE"
