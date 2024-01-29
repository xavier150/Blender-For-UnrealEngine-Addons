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
import os
import webbrowser
from . import utils
from ... import __internal__


def create_operator_class():
    # Create an custom class ussing addon name for avoid name collision.
    
    class CustomOpenTargetWebPageOperator(bpy.types.Operator):
        bl_label = "Documentation"
        bl_idname = utils.get_operator_name()
        bl_description = "Click for open URL."
        url: bpy.props.StringProperty(default="https://github.com/xavier150/BleuRavenBlenderPythonLibrary")

        def execute(self, context):
            # Check if the URL starts with http:// or https://
            if self.url.startswith("http://") or self.url.startswith("https://"):
                webbrowser.open(self.url)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Invalid URL. Only HTTP and HTTPS URLs are allowed.")
                return {'CANCELLED'}

    CustomOpenTargetWebPageOperator.__name__ = utils.get_class_name()
    return CustomOpenTargetWebPageOperator





classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    BBPL_OT_OpenTargetWebPage = create_operator_class()
    bpy.utils.register_class(BBPL_OT_OpenTargetWebPage)



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)