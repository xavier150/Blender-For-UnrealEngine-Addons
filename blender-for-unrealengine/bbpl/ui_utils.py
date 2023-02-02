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


import bpy
import fnmatch
import mathutils
import math
import time
import sys


def LayoutSceneSection(layout, PropName, PropLabel):
    scene = bpy.context.scene
    expanded = eval("scene."+PropName)
    tria_icon = "TRIA_DOWN" if expanded else "TRIA_RIGHT"
    layout.row().prop(scene, PropName, icon=tria_icon, icon_only=True, text=PropLabel, emboss=False)
    return expanded


def getIconByGroupTheme(theme_enum):
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
