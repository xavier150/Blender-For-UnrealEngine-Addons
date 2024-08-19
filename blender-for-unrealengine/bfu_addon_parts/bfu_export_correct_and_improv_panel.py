import bpy

from .. import bfu_utils
from .. import languages

class BFU_PT_CorrectAndImprov(bpy.types.Panel):
    # Is Clipboard panel

    bl_idname = "BFU_PT_CorrectAndImprov"
    bl_label = "Correct and improv"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    class BFU_OT_CorrectExtremUV(bpy.types.Operator):
        bl_label = (languages.ti('correct_use_extrem_uv_scale_name'))
        bl_idname = "object.correct_extrem_uv"
        bl_description = (languages.ti('correct_extrem_uv_scale_operator_desc'))
        bl_options = {'REGISTER', 'UNDO'}

        step_scale: bpy.props.IntProperty(
            name=(languages.ti('correct_extrem_uv_scale_step_scale_name')),
            description =(languages.ti('correct_use_extrem_uv_scale_desc')),
            default=2,
            min=1,
            max=100,
            )
        
        move_to_absolute: bpy.props.BoolProperty(
            name=(languages.ti('correct_extrem_uv_scale_use_absolute_name')),
            description =(languages.ti('correct_extrem_uv_scale_use_absolute_desc')),
            default=False,
            )

        def execute(self, context):
            if bpy.context.active_object.mode == "EDIT":
                bfu_utils.CorrectExtremeUV(step_scale=self.step_scale, move_to_absolute=self.move_to_absolute)
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
