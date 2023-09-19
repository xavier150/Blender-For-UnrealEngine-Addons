import bpy

from bpy.types import (
        Operator,
        )

from .. import bfu_utils

class BFU_PT_CorrectAndImprov(bpy.types.Panel):
    # Is Clipboard panel

    bl_idname = "BFU_PT_CorrectAndImprov"
    bl_label = "Correct and improv"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine 4 bis"
    bl_parent_id = "BFU_PT_BlenderForUnrealObject"

    class BFU_OT_CorrectExtremUV(Operator):
        bl_label = "Correct extrem UV For Unreal"
        bl_idname = "object.correct_extrem_uv"
        bl_description = (
            "Correct extrem UV island of the selected object" +
            " for better use in real time engines"
            )
        bl_options = {'REGISTER', 'UNDO'}

        stepScale: bpy.props.IntProperty(
            name="Step scale",
            default=2,
            min=1,
            max=100)

        def execute(self, context):
            if bpy.context.active_object.mode == "EDIT":
                bfu_utils.CorrectExtremeUV(stepScale=self.stepScale)
                self.report(
                    {'INFO'},
                    "UV corrected!")
            else:
                self.report(
                    {'WARNING'},
                    "Move to Edit mode for correct extrem UV.")
            return {'FINISHED'}


def menu_func(self, context):
    print(context)
    layout = self.layout
    col = layout.column()
    col.separator(factor=1.0)
    col.operator(BFU_PT_CorrectAndImprov.BFU_OT_CorrectExtremUV.bl_idname)

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_CorrectAndImprov.BFU_OT_CorrectExtremUV,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_uv_map.append(menu_func)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_uv_map.remove(menu_func)
