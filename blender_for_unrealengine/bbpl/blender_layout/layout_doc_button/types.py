# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import webbrowser
from typing import Set, TYPE_CHECKING
from . import utils



class CustomOpenTargetWebPage_Operator(bpy.types.Operator):
    bl_label = "Documentation"
    bl_idname = utils.get_open_target_web_page_idname()
    bl_description = "Click for open URL."
    url: bpy.props.StringProperty(default="https://github.com/xavier150/BleuRavenBlenderPythonLibrary")  # type: ignore

    if TYPE_CHECKING:
        url: str

    def execute(self, context: bpy.types.Context) -> Set[str]:  # type: ignore
        # Check if the URL starts with http:// or https://
        if self.url.startswith("http://") or self.url.startswith("https://"):
            webbrowser.open(self.url)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Invalid URL. Only HTTP and HTTPS URLs are allowed.")
            return {'CANCELLED'}

def create_doc_operator_class():
    # Create a custom class using addon name to avoid name collision.
    CustomOpenTargetWebPage_Operator.__name__ = utils.get_open_target_web_page_class_name()
    return CustomOpenTargetWebPage_Operator

# ----------------- Register ----------------

BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS = None

def init_doc_button():
    global BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS
    if BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS is None:
        BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS = create_doc_operator_class()


init_doc_button()

classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    global BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS
    if BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS:
        bpy.utils.register_class(BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    global BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS
    if BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS:
        bpy.utils.unregister_class(BBPL_OT_OpenTargetWebPage_CUSTOM_CLASS)