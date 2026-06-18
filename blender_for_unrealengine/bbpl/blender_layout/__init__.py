# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
import importlib
from . import layout_accordion
from . import layout_template_list
from . import layout_doc_button
from . import layout_selector
from . import layout_utils

if "layout_accordion" in locals():
    importlib.reload(layout_accordion)
if "layout_template_list" in locals():
    importlib.reload(layout_template_list)
if "layout_doc_button" in locals():
    importlib.reload(layout_doc_button)
if "layout_selector" in locals():
    importlib.reload(layout_selector)
if "layout_utils" in locals():
    importlib.reload(layout_utils)


classes = (
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    layout_accordion.register()
    layout_template_list.register()
    layout_doc_button.register()
    layout_selector.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    layout_selector.unregister()
    layout_doc_button.unregister()
    layout_template_list.unregister()
    layout_accordion.unregister()
