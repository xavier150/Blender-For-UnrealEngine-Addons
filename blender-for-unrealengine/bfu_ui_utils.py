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

if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
from . import bfu_basics
from .bfu_basics import *


def LayoutSection(layout, PropName, PropLabel):
    scene = bpy.context.scene
    expanded = eval("scene."+PropName)
    tria_icon = "TRIA_DOWN" if expanded else "TRIA_RIGHT"
    layout.row().prop(scene, PropName, icon=tria_icon, icon_only=True, text=PropLabel, emboss=False)
    return expanded


def DisplayPropertyFilter(active_tab, active_sub_tab):
    # Define more easily the options which must be displayed or not

    scene = bpy.context.scene
    if scene.bfu_active_tab == active_tab == "OBJECT":
        if scene.bfu_active_object_tab == active_sub_tab or scene.bfu_active_object_tab == "ALL":
            return True

    if scene.bfu_active_tab == active_tab == "SCENE":
        if scene.bfu_active_scene_tab == active_sub_tab or scene.bfu_active_scene_tab == "ALL":
            return True
    return False
