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
import importlib
from . import layout_accordion
from . import layout_template_list
from . import layout_doc_button
from . import layout_selector

if "layout_accordion" in locals():
    importlib.reload(layout_accordion)
if "layout_template_list" in locals():
    importlib.reload(layout_template_list)
if "layout_doc_button" in locals():
    importlib.reload(layout_doc_button)
if "layout_selector" in locals():
    importlib.reload(layout_selector)



classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    layout_accordion.register()
    layout_template_list.register()
    layout_doc_button.register()
    layout_selector.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    layout_selector.unregister()
    layout_doc_button.unregister()
    layout_template_list.unregister()
    layout_accordion.unregister()
