import bpy

def get_static_export_procedure_enum_property_list():
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

def get_default_static_export_procedure():
    return "blender-standard"

def get_obj_static_procedure_preset(obj: bpy.types.Object):
    return get_static_procedure_preset(obj.bfu_static_export_procedure)

def get_static_procedure_preset(procedure: str): # Object.bfu_static_export_procedure
    preset = {}
    if procedure == "ue-standard":
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'

    if procedure == "blender-standard":
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'

    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_static_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a skeletal mesh should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_static_export_procedure_enum_property_list(),
        default=get_default_static_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)