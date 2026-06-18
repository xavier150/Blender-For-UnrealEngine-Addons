# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy

from typing import Tuple, Optional, TYPE_CHECKING
from . import utils
from .. import layout_utils
from ... import __internal__

class CustomAccordionUI_PropertyGroup(bpy.types.PropertyGroup):
    expend: bpy.props.BoolProperty(  # type: ignore
        name="Use",
        description="Click to expand / collapse",
        default=False,
        options={"HIDDEN", "SKIP_SAVE"}
    )

    if TYPE_CHECKING:
        expend: bool

    def get_name(self):
        return layout_utils.get_property_name_from_property_group(self, CustomAccordionUI_PropertyGroup)
    

    def support_panel_prop(self, layout: bpy.types.UILayout):
        # Use panel_prop() was added only in Blender 4.1 and work on UI region.type only.
        # The BBPL one work since Blender 2.8 on any regions.

        if bpy.context.region is None:
            return False

        if bpy.app.version >= (4, 1, 0):
            if bpy.context.region.type == "UI":
                return True
        return False


    def draw(self, layout: bpy.types.UILayout, text: Optional[str] = None) -> Tuple[bpy.types.UILayout, Optional[bpy.types.UILayout]]:
        """Similar to layout.panel_prop(...) Use panel_prop() in Blender 4.1 and new versions.
                :param layout: layout body
                :type layout: bpy.types.UILayout
                :param text: header text (Optional) Use registed text if None.
                :type text: str
                :return: layout_header, Sub-layout to put items in, `UILayout`

        layout_body, Sub-layout to put items in. Will be none if the panel is collapsed., `UILayout`
        """

        # Details
        if text:
            header_text = text
        else:
            header_text = self.get_name()

        # Draw
        if self.support_panel_prop(layout): 
            header, panel = layout.panel_prop(self, "expend")
            header.label(text=header_text)
        else:
            tria_icon = "TRIA_DOWN" if self.expend else "TRIA_RIGHT"
            header: bpy.types.UILayout = layout.row()
            header.prop(self, "expend", icon=tria_icon, icon_only=True, text=header_text, emboss=False, toggle=True, expand=True)
            if self.expend:
                panel = layout
            else:
                panel = None

        # Return
        return header, panel

    def is_expanded(self):
        return self.expend

    def is_collapsed(self):
        return not self.expend

def get_layout_accordion_class():
    global BBPL_UI_Accordion_CUSTOM_CLASS
    return BBPL_UI_Accordion_CUSTOM_CLASS

def create_layout_accordion_class():
    # Create an custom class ussing addon name for avoid name collision.
    CustomAccordionUI_PropertyGroup.__name__ = utils.get_class_name()
    return CustomAccordionUI_PropertyGroup

# ----------------- Register ----------------

BBPL_UI_Accordion_CUSTOM_CLASS = None

def init_layout_accordion():
    global BBPL_UI_Accordion_CUSTOM_CLASS
    if BBPL_UI_Accordion_CUSTOM_CLASS is None:
        BBPL_UI_Accordion_CUSTOM_CLASS = create_layout_accordion_class()

init_layout_accordion()

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    global BBPL_UI_Accordion_CUSTOM_CLASS
    if BBPL_UI_Accordion_CUSTOM_CLASS:
        bpy.utils.register_class(BBPL_UI_Accordion_CUSTOM_CLASS)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    global BBPL_UI_Accordion_CUSTOM_CLASS
    if BBPL_UI_Accordion_CUSTOM_CLASS:
        bpy.utils.unregister_class(BBPL_UI_Accordion_CUSTOM_CLASS)