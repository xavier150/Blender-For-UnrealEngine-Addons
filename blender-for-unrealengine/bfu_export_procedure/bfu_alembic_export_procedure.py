import bpy

def get_alembic_export_procedure_enum_property_list():
    items=[
        ("blender-standard",
            "Blender Standard",
            "Standard ALEMBIC.",
            "OUTLINER_OB_FONT",
            1),
        ]
    return items

def get_default_alembic_export_procedure():
    return "blender-standard"

def get_alembic_procedure_preset(procedure: str): # Object.bfu_alembic_export_procedure
    preset = {}
    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.bfu_alembic_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a alembic animations should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_alembic_export_procedure_enum_property_list(),
        default=get_default_alembic_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)