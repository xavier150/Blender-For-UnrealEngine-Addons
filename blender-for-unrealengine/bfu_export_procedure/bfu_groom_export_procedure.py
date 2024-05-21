import bpy

def get_groom_export_procedure_enum_property_list():
    items=[
        ("blender-standard",
            "Blender Standard",
            "Standard ALEMBIC.",
            "OUTLINER_OB_FONT",
            1),
        ]
    return items

def get_default_groom_export_procedure():
    return "blender-standard"

def get_groom_procedure_preset(procedure: str): # Object.bfu_groom_export_procedure
    preset = {}
    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.bfu_groom_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a groom animations should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_groom_export_procedure_enum_property_list(),
        default=get_default_groom_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)