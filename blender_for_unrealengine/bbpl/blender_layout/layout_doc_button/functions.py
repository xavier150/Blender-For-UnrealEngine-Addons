# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import TYPE_CHECKING
from . import types
from . import utils
from ... import __internal__

def add_doc_page_operator(layout: bpy.types.UILayout, url: str="", text: str="", icon: str="HELP"):
    doc_operator = layout.operator(
        utils.get_open_target_web_page_idname(),
        icon=icon,  # type: ignore
        text=text
        )
    if TYPE_CHECKING:
        doc_operator: types.CustomOpenTargetWebPage_Operator
    
    doc_operator.url = url

    return layout


def add_left_doc_page_operator(layout: bpy.types.UILayout, url: str="", text: str="", icon: str="HELP"):
    new_row = layout.row()
    doc_operator = new_row.operator(
        utils.get_open_target_web_page_idname(),
        icon=icon,  # type: ignore
        text=""
        )
    
    if TYPE_CHECKING:
        doc_operator: types.CustomOpenTargetWebPage_Operator
    doc_operator.url = url
    new_row.label(text=text)
    return new_row

def add_right_doc_page_operator(layout: bpy.types.UILayout, url: str="", text: str="", icon: str="HELP"):
    new_row = layout.row()
    new_row.label(text=text)
    doc_operator = new_row.operator(
        utils.get_open_target_web_page_idname(),
        icon=icon,  # type: ignore
        text=""
        )
    
    if TYPE_CHECKING:
        doc_operator: types.CustomOpenTargetWebPage_Operator
    doc_operator.url = url
    return new_row

