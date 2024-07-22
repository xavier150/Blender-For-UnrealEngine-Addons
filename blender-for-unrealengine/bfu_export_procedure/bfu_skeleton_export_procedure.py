import bpy

def get_skeleton_export_procedure_enum_property_list():
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
        ("auto-rig-pro",
            "AutoRigPro",
            "Export using AutoRigPro.",
            "ARMATURE_DATA",
            3),
        ]
    return items

def get_default_skeleton_export_procedure():
    return "blender-standard"

def get_obj_skeleton_procedure_preset(obj: bpy.types.Object):
    return get_skeleton_procedure_preset(obj.bfu_skeleton_export_procedure)

def get_skeleton_procedure_preset(procedure: str): # Object.bfu_skeleton_export_procedure
    preset = {}
    if procedure == "ue-standard":
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='X' 
        preset["secondary_bone_axis"]='-Z'

    # Use Default FBX values
    if procedure == "blender-standard":
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='Y'
        preset["secondary_bone_axis"]='X'

    if procedure == "auto-rig-pro":
        preset["use_space_transform"]=True
        preset["axis_forward"]='-Z'
        preset["axis_up"]='Y'
        preset["primary_bone_axis"]='Y'
        preset["secondary_bone_axis"]='X'

    return preset


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_skeleton_export_procedure = bpy.props.EnumProperty(
        name="Export Procedure",
        description=(
            "This will define how a static mesh should be exported."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=get_skeleton_export_procedure_enum_property_list(),
        default=get_default_skeleton_export_procedure()
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)