import bpy

def draw_ui_custom_property(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_export_with_custom_props")
    custom_props_layout = layout.column()
    custom_props_layout.enabled = obj.bfu_export_with_custom_props
    custom_props_layout.prop(obj, "bfu_do_not_import_curve_with_zero")
    