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

from bpy.props import (
        StringProperty,
        )

from bpy.types import (
        Operator,
        )


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


def LabelWithDocButton(tagetlayout, name, docOcticon):  # OLD
    newRow = tagetlayout.row()
    newRow.label(text=name)
    docOperator = newRow.operator(
        "object.open_documentation_target_page",
        icon="HELP",
        text=""
        )
    docOperator.octicon = docOcticon


def DocPageButton(layout, doc_page, doc_octicon=""):
    docOperator = layout.operator(
        "object.open_documentation_target_page",
        icon="HELP",
        text=""
        )
    docOperator.page = doc_page
    docOperator.octicon = doc_octicon


def PropWithDocButton(self, tagetlayout, name, doc_octicon):  # OLD
    newRow = tagetlayout.row()
    newRow.prop(self, name)
    docOperator = newRow.operator(
        "object.open_documentation_target_export_page",
        icon="HELP",
        text=""
        )
    docOperator.octicon = doc_octicon


class BFU_AP_UI_UTILS(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    class BFU_OT_OpenDocumentationTargetPage(Operator):
        bl_label = "Documentation"
        bl_idname = "object.open_documentation_target_page"
        bl_description = "Clic for open documentation page on GitHub"
        page: StringProperty(default="")
        octicon: StringProperty(default="")

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/" + self.page + "#" + self.octicon
                )
            return {'FINISHED'}

    class BFU_OT_OpenDocumentationTargetExportPage(Operator):
        bl_label = "Documentation"
        bl_idname = "object.open_documentation_target_export_page"
        bl_description = "Clic for open documentation page on GitHub"
        octicon: StringProperty(default="")

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/How-export-assets" +
                "#"+self.octicon
                )
            return {'FINISHED'}


classes = (
    BFU_AP_UI_UTILS,
    BFU_AP_UI_UTILS.BFU_OT_OpenDocumentationTargetPage,
    BFU_AP_UI_UTILS.BFU_OT_OpenDocumentationTargetExportPage
)


def register():
    """
    Register.
    """
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    """
    unregister.
    """
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
