import bpy

def draw_custom_property_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_export_with_custom_props")
    