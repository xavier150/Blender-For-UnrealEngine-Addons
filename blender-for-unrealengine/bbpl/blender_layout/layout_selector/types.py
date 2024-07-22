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

def update_string_from_selector(self, context, string_selector):
    if context.region.type != "UI":
        return
    string_name = string_selector.property_name
    selector_name = string_selector.property_selector_name
    if getattr(self, string_name) != getattr(self, selector_name):
        setattr(self, string_name, getattr(self, selector_name))
        print("Selector update...")

def update_selector_from_string(self, context, string_selector):
    if context.region.type != "UI":
        return
    string_name = string_selector.property_name
    selector_name = string_selector.property_selector_name
    if getattr(self, selector_name) != getattr(self, string_name):
        setattr(self, selector_name, getattr(self, string_name))
        print("Selector update...")

class StringSelector():

    def __init__(self, property_name, property_selector_name):
        self.property_name = property_name
        self.property_selector_name = property_selector_name
        self.name = ""
        self.default = ""
        self.description = ""
        self.items = []
        self.string_property = None
        self.enum_selector = None


    def create_propertys(self):
        string_selector = self
        def string_update_wrapper(self, context):
            update_selector_from_string(self, context, string_selector)

        def selector_update_wrapper(self, context):
            update_string_from_selector(self, context, string_selector)

        self.string_property = bpy.props.StringProperty(
            default=self.default,
            name=self.name,
            description=self.description,
            update=string_update_wrapper
            )

        self.enum_selector = bpy.props.EnumProperty(
            items=self.items,
            update=selector_update_wrapper,
            options={"HIDDEN", "SKIP_SAVE"}
            )




classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)