# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List, Dict, Set, Any
from .. import bbpl
from . import bfu_check_list
from . import bfu_check_utils

class BFU_OT_CheckPotentialErrorPopup(bpy.types.Operator):
    bl_label = "Check Potential Issues"
    bl_idname = "object.checkpotentialerror"
    bl_description = "Check potential issues on assets to export."
    text = "none"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        invoke_info = ""

        fix_info: Dict[str, str] = bfu_check_utils.process_general_fix()
        check_info: Dict[str, str] = bfu_check_list.run_all_check()

        all_info: Dict[str, str] = {**fix_info, **check_info}
        for x, all_info_key in enumerate(all_info):
            all_info_data = all_info[all_info_key]
            invoke_info += all_info_key + ": " + str(all_info_data)
            if x < len(all_info)-1:
                invoke_info += "\n"

        bpy.ops.object.openpotentialerror("INVOKE_DEFAULT", invoke_info=invoke_info)  # type: ignore
        return {'FINISHED'}

class BFU_OT_OpenPotentialErrorPopup(bpy.types.Operator):
    bl_label = "Open potential errors"
    bl_idname = "object.openpotentialerror"
    bl_description = "Open potential errors"
    invoke_info: bpy.props.StringProperty(default="...")  # type: ignore

    class BFU_OT_FixitTarget(bpy.types.Operator):
        bl_label = "Fix it !"
        bl_idname = "object.fixit_objet"
        bl_description = "Correct target error"
        bl_options = {'REGISTER', 'UNDO'}
        error_index: bpy.props.IntProperty(default=-1)  # type: ignore

        def execute(self, context: bpy.types.Context) -> Set[Any]:
            result = bfu_check_utils.try_to_correct_potential_issues(self.error_index)  # type: ignore
            self.report({'INFO'}, result)
            return {'FINISHED'}

    class BFU_OT_SelectObjectButton(bpy.types.Operator):
        bl_label = "Select(Object)"
        bl_idname = "object.select_error_objet"
        bl_description = "Select target Object."
        bl_options = {'REGISTER', 'UNDO'}
        error_index: bpy.props.IntProperty(default=-1)  # type: ignore

        def execute(self, context: bpy.types.Context) -> Set[Any]:
            bfu_check_utils.select_potential_issue_object(self.error_index)  # type: ignore
            return {'FINISHED'}

    class BFU_OT_SelectVertexButton(bpy.types.Operator):
        bl_label = "Select(Vertex)"
        bl_idname = "object.select_error_vertex"
        bl_description = "Select target Vertex."
        bl_options = {'REGISTER', 'UNDO'}
        error_index: bpy.props.IntProperty(default=-1)  # type: ignore

        def execute(self, context: bpy.types.Context) -> Set[Any]:
            bfu_check_utils.select_potential_issue_vertices(self.error_index)  # type: ignore
            return {'FINISHED'}

    class BFU_OT_SelectPoseBoneButton(bpy.types.Operator):
        bl_label = "Select(PoseBone)"
        bl_idname = "object.select_error_posebone"
        bl_description = "Select target Pose Bone."
        bl_options = {'REGISTER', 'UNDO'}
        error_index: bpy.props.IntProperty(default=-1)  # type: ignore

        def execute(self, context: bpy.types.Context) -> Set[Any]:
            bfu_check_utils.select_potential_issue_pose_bone(self.error_index)  # type: ignore
            return {'FINISHED'}


    def execute(self, context: bpy.types.Context) -> Set[Any]:
        return {'FINISHED'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=1020)

    def check(self, context: bpy.types.Context) -> bool:
        return True

    def draw(self, context: bpy.types.Context):

        layout = self.layout

        potential_errors = bfu_check_utils.get_potential_errors()
        if len(potential_errors) > 0:
            popup_title = (
                str(len(potential_errors)) +
                " potential error(s) found!")
        else:
            popup_title = "No potential error to correct!"


        layout.label(text=popup_title)
        invoke_info_lines: List[str] = self.invoke_info.split("\n")
        for invoke_info_line in invoke_info_lines:
            layout.label(text="- "+invoke_info_line)
        
        layout.separator()
        row = layout.row()
        col = row.column()
        for x, error in enumerate(potential_errors):
            myLine = col.box().split(factor=0.85)
            # ----
            if error.type == 0:
                msg_type: str = 'INFO'
                msg_icon: str = 'INFO'
            elif error.type == 1:
                msg_type: str = 'WARNING'
                msg_icon: str = 'ERROR'
            elif error.type == 2:
                msg_type: str = 'ERROR'
                msg_icon: str = 'CANCEL'
            else:
                msg_type: str = 'UNKNOWN'
                msg_icon: str = 'QUESTION'
            # ----

            # Text
            TextLine = myLine.column()
            error_full_msg: str = msg_type + ": " + error.text
            splited_texts: List[str] = error_full_msg.split("\n")

            for text, Line in enumerate(splited_texts):
                if (text < 1):

                    if (error.docs_octicon != "None"):  # Doc button

                        url = "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/How-avoid-potential-errors" + "#" + error.docs_octicon
                        bbpl.blender_layout.layout_doc_button.add_left_doc_page_operator(TextLine, text="More Info", url=url)

                    first_text_line = TextLine.row()
                    first_text_line.label(text=Line, icon=msg_icon)
                else:
                    TextLine.label(text=Line)

            # Select and fix button
            ButtonLine = myLine.column()
            if (error.correct_ref != "None"):
                props = ButtonLine.operator("object.fixit_objet",text=error.correct_label)
                props.error_index = x
            if (error.object is not None):
                if (error.select_object_button):
                    props = ButtonLine.operator("object.select_error_objet")
                    props.error_index = x
                if (error.select_vertex_button):
                    props = ButtonLine.operator("object.select_error_vertex")
                    props.error_index = x
                if (error.select_pose_bone_button):
                    props = ButtonLine.operator("object.select_error_posebone")
                    props.error_index = x



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CheckPotentialErrorPopup,
    BFU_OT_OpenPotentialErrorPopup,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_FixitTarget,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectObjectButton,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectVertexButton,
    BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectPoseBoneButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

