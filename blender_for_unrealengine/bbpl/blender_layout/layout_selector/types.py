# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from typing import Optional, Callable, Any, List, Union

import bpy

from ... import __internal__



class StringSelector():

    def __init__(self, property_name: str, property_selector_name: str):
        self.property_name: str = property_name
        self.property_selector_name: str = property_selector_name
        self.name: str = ""
        self.default: str = ""
        self.description: str = ""
        self.items: Union[List[Any], Callable[..., List[Any]]] = []
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
            if callable(string_selector.items):
                value = getattr(property_self, string_selector.property_name)
                for identifier, number in _dynamic_enum_values(string_selector.items(property_self, context)):
                    if identifier == value and not isinstance(property_self, bpy.types.NodeSocket):
                        property_self[string_selector.property_selector_name] = number
                        break
            else:
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

        enum_kwargs = {}
        if callable(self.items):
            def dynamic_get(property_self: Any) -> int:
                items = list(_dynamic_enum_values(string_selector.items(property_self, bpy.context)))
                value = getattr(property_self, string_selector.property_name)
                for identifier, number in items:
                    if identifier == value:
                        return number
                previous = None if isinstance(property_self, bpy.types.NodeSocket) else property_self.get(string_selector.property_selector_name)
                for _, number in items:
                    if number == previous:
                        return number
                return items[0][1] if items else 0

            def dynamic_set(property_self: Any, number: int):
                for identifier, item_number in _dynamic_enum_values(string_selector.items(property_self, bpy.context)):
                    if item_number == number:
                        if not isinstance(property_self, bpy.types.NodeSocket):
                            property_self[string_selector.property_selector_name] = number
                        if getattr(property_self, string_selector.property_name) != identifier:
                            setattr(property_self, string_selector.property_name, identifier)
                        return
                raise ValueError(f"Unknown enum value {number} for {string_selector.property_selector_name}")

            enum_kwargs = {"get": dynamic_get, "set": dynamic_set}

        self.enum_selector = bpy.props.EnumProperty(  # type: ignore
            items=self.items,  # type: ignore
            update=enum_update_wrapper,
            options={"HIDDEN", "SKIP_SAVE"},
            **enum_kwargs
            )


def _dynamic_enum_values(items):
    for index, item in enumerate(items):
        if item is None or not item[0]:
            continue
        if len(item) == 5:
            number = item[4]
        elif len(item) == 4 and isinstance(item[3], int):
            number = item[3]
        else:
            number = index
        yield item[0], number


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
        items = string_selector.items
        if callable(items):
            valid = any(item[0] == new_value for item in items(self, bpy.context))
        else:
            valid = new_value in self.bl_rna.properties[selector_name].enum_items
        if valid:
            setattr(self, selector_name, new_value)

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore