import bpy
import importlib

from . import bfu_custom_property_props
from . import bfu_custom_property_utils

if "bfu_custom_property_props" in locals():
    importlib.reload(bfu_custom_property_props)
if "bfu_custom_property_utils" in locals():
    importlib.reload(bfu_custom_property_utils)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_custom_property_props.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_custom_property_props.unregister()