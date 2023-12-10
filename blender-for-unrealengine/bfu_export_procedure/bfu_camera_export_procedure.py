import bpy

def get_camera_export_procedure_enum_property_list():
    items=[
        ("ue-standard",
            "UE Standard",
            "Modified fbx I/O for Unreal Engine",
            "ARMATURE_DATA",
            1),
        ("blender-standard",
            "Blender Standard",
            "Standard fbx I/O.",
            "ARMATURE_DATA",
            2),
        ]
    return items

def get_default_camera_export_procedure():
    return "blender-standard"

def get_camera_procedure_preset(procedure: str): # Object.bfu_camera_export_procedure
    preset = {}
    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_camera_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a static mesh should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_camera_export_procedure_enum_property_list(),
        default=get_default_camera_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)