import bpy

def get_collection_export_procedure_enum_property_list():
    items=[
        ("ue-standard",
            "UE Standard",
            "Modified fbx I/O for Unreal Engine",
            "OUTLINER_OB_GROUP_INSTANCE",
            1),
        ("blender-standard",
            "Blender Standard",
            "Standard fbx I/O.",
            "OUTLINER_OB_GROUP_INSTANCE",
            2),
        ]
    return items

def get_default_collection_export_procedure():
    return "blender-standard"

def get_collection_procedure_preset(procedure: str): # Object.bfu_static_export_procedure
    preset = {}
    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Collection.bfu_collection_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a collection should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_collection_export_procedure_enum_property_list(),
        default=get_default_collection_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)