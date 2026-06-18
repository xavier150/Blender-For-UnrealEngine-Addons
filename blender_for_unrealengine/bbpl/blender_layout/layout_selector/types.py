# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from typing import Optional, Callable, Any

import bpy

from ... import __internal__



class StringSelector():

    def __init__(self, property_name: str, property_selector_name: str):
        self.property_name: str = property_name
        self.property_selector_name: str = property_selector_name
        self.name: str = ""
        self.default: str = ""
        self.description: str = ""
        self.items = []
        self.update: Optional[Callable[..., None]] = None
        self.string_property: Any = None
        self.enum_selector: Any = None


    def get_string_property(self) -> str:
        '''
        Returns the StringProperty _PropertyDeferred definition used to declare the property
        inside a Blender class annotation.
        use:
        my_value: selector.get_string_property()
        '''
        return self.string_property
    
    def get_enum_selector_property(self) -> str:
        '''
        Returns the EnumProperty _PropertyDeferred definition used to declare the property
        inside a Blender class annotation.
        use:
        my_value_selector: selector.get_enum_selector_property()
        '''
        return self.enum_selector


    def create_properties(self):
        string_selector = self

        def string_update_wrapper(property_self: Any, context: bpy.types.Context):
            update_selector_from_string(property_self, string_selector)
            if string_selector.update:
                string_selector.update()

        def enum_update_wrapper(property_self: Any, context: bpy.types.Context):
            update_string_from_enum(property_self, string_selector)
            if string_selector.update:
                string_selector.update()
            

        self.string_property = bpy.props.StringProperty(  # type: ignore
            default=self.default,
            name=self.name,
            description=self.description,
            update=string_update_wrapper
            )

        self.enum_selector = bpy.props.EnumProperty(  # type: ignore
            items=self.items,  # type: ignore
            update=enum_update_wrapper,
            options={"HIDDEN", "SKIP_SAVE"}
            )


def update_string_from_enum(self: Any, string_selector: StringSelector):
    string_name = string_selector.property_name
    selector_name = string_selector.property_selector_name
    if getattr(self, string_name) != getattr(self, selector_name):
        setattr(self, string_name, getattr(self, selector_name))
        #print("Selector update...")

def update_selector_from_string(self: Any, string_selector: StringSelector):
    string_name = string_selector.property_name
    selector_name = string_selector.property_selector_name
    new_value = getattr(self, string_name)
    if getattr(self, selector_name) != new_value:
        # Update only if the new value exists in the enum items, otherwise keep the previous value (Avoid script errors)
        if new_value in self.bl_rna.properties[selector_name].enum_items:
            setattr(self, selector_name, new_value)

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore