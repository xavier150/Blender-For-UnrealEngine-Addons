
import bpy
from idprop.types import IDPropertyGroup
from typing import List, Callable, Optional, Any, Tuple, cast

def _property_sources(data: Any) -> Tuple[Any, ...]:
    # Blender 5.0+ can store registered RNA values separately from custom ID properties.
    if bpy.app.version >= (5, 0, 0):
        get_system_properties = getattr(data, "bl_system_properties_get", None)
        if get_system_properties is not None:
            system_properties = get_system_properties()
            if system_properties is not None:
                return (system_properties, data)
    return (data,)

def _legacy_value(data: Any, name: str) -> Any:
    for source in _property_sources(data):
        if name in source:
            return source[name]
    raise KeyError(name)

def enum_callback(data: Any, old_var_name: str, new_var_name: str) -> Any:
    value = _legacy_value(data, old_var_name)

    enum_definition = data.bl_rna.properties.get(new_var_name)

    if enum_definition and enum_definition.type == "ENUM":
        # Get the list of enum values and match by integer value
        for enum_item in enum_definition.enum_items:
            if value == enum_item.value or value == enum_item.identifier:
                return enum_item.identifier
        
        # If no match found by value, try the first enum item as fallback
        if enum_definition.enum_items:
            print(f"Warning: Could not find enum value {value} for {new_var_name}, using first enum item")
            return enum_definition.enum_items[0].identifier
    
    print(f"Warning: Could not find enum definition for {new_var_name}")
    # Return the first enum item's identifier as a safe default
    if enum_definition and enum_definition.enum_items:
        return enum_definition.enum_items[0].identifier
    
    return value

def object_pointer_callback(data: Any, old_var_name: str, new_var_name: str) -> Optional[bpy.types.Object]:
    del new_var_name  # Keep the migration callback signature.
    value = _legacy_value(data, old_var_name)
    if isinstance(value, bpy.types.Object):
        return value
    return None

def _copy_collection(data: Any, name: str, value: object) -> None:
    if not isinstance(value, list):
        raise TypeError("expected a stored collection of property groups")

    old_items = cast(List[object], value)
    collection = getattr(data, name)
    try:
        for old_item in old_items:
            if not isinstance(old_item, IDPropertyGroup):
                raise TypeError("expected a stored collection of property groups")
            item = collection.add()
            for field, field_value in old_item.items():
                setattr(item, field, field_value)
        if not old_items:
            # Clearing an untouched collection doesn't mark it as set.
            collection.add()
            collection.remove(0)
    except (AttributeError, RuntimeError, TypeError, ValueError):
        data.property_unset(name)
        raise

class DataVariableUpdater:
    """
    A class to update data variables in Blender by renaming them.
    """
    def __init__(self) -> None:
        self.update_variable: int = 0
        self.remove_variable: int = 0
        self.print_log: bool = False

    def update_data_variable(self, data: Any, old_var_names: List[str], new_var_name: str, callback: Optional[Callable[[Any, str, str], Any]] = None) -> None:
        property_sources = _property_sources(data)
        for old_var_name in old_var_names:
            sources = [source for source in property_sources if old_var_name in source]
            if sources:
                try:
                    if data.is_property_set(new_var_name) or new_var_name in data:
                        for source in sources:
                            del source[old_var_name]
                        self.remove_variable += 1
                        print(f'"{old_var_name}" removed from {data.name}; keeping "{new_var_name}"')
                    else:
                        value = callback(data, old_var_name, new_var_name) if callback else sources[0][old_var_name]
                        prop = data.bl_rna.properties[new_var_name]
                        if prop.type == "COLLECTION":
                            _copy_collection(data, new_var_name, value)
                        else:
                            setattr(data, new_var_name, value)

                        for source in sources:
                            del source[old_var_name]
                        self.update_variable += 1
                        print(f'"{old_var_name}" updated to "{new_var_name}" in {data.name}')
                except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as e:
                    print(f'Error updating "{old_var_name}" to "{new_var_name}" in {data.name}: {str(e)}')

    def remove_data_variable(self, data: Any, old_var_names: List[str]) -> None:
        for old_var_name in old_var_names:
            for source in _property_sources(data):
                if old_var_name in source:
                    try:
                        del source[old_var_name]
                        self.remove_variable += 1
                        print(f'"{old_var_name}" removed from {data.name}')
                    except (KeyError, RuntimeError, TypeError) as e:
                        print(f'Error removing "{old_var_name}" from {data.name}: {str(e)}')

    def print_update_log(self) -> None:
        """
        Print a log of the number of data variables updated and removed.

        Args:
            None

        Returns:
            None
        """
        print(f'{self.update_variable} data variables have been updated.')
        print(f'{self.remove_variable} data variables have been removed.')