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
from . import utils
from ... import __internal__

layout_accordion_class = None

def get_layout_accordion_class():
    global layout_accordion_class
    return layout_accordion_class


def create_ui_accordion_class():
    # Create an custom class ussing addon name for avoid name collision.

    class CustomAccordionUI_PropertyGroup(bpy.types.PropertyGroup):
        expend: bpy.props.BoolProperty(
            name="Use",
            description="Click to expand / collapse",
            default=False,
            options={"HIDDEN", "SKIP_SAVE"}
        )
        
        def get_name(self):
            if bpy.app.version >= (3, 0, 0):
                prop_rna = self.id_data.bl_rna.properties[self.id_properties_ensure().name]
                return prop_rna.name
            else:
                prop_rna = self.id_data.bl_rna.properties[self.path_from_id()]
                return prop_rna.name


        def draw(self, layout: bpy.types.UILayout):
            tria_icon = "TRIA_DOWN" if self.expend else "TRIA_RIGHT"
            description = "Click to collapse" if self.expend else "Click to expand"
            layout.row().prop(self, "expend", icon=tria_icon, icon_only=True, text=self.get_name(), emboss=False, toggle=True, expand=True)
            if self.expend:
                pass

        def is_expend(self):
            return self.expend
        
    CustomAccordionUI_PropertyGroup.__name__ = utils.get_class_name()
    return CustomAccordionUI_PropertyGroup

classes = (
)

def register():
    global layout_accordion_class
    for cls in classes:
        bpy.utils.register_class(cls)

    BBPL_UI_Accordion = create_ui_accordion_class()
    layout_accordion_class = BBPL_UI_Accordion
    bpy.utils.register_class(BBPL_UI_Accordion)



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)