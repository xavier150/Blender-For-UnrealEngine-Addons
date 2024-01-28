import bpy
from .. import languages

classes = (
)

def get_preset_values():
    preset_values = [
        'obj.bfu_export_with_custom_props'
        ]
    return preset_values

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_export_with_custom_props = bpy.props.BoolProperty(
        name=(languages.ti('export_with_custom_props_name')),
        description=(languages.tt('export_with_custom_props_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
