# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Any, Set, Optional
import bpy
from . import bfu_anim_action_utils
from . import bfu_anim_action_props
from .bfu_anim_action_operator_action_group import BFU_OT_ObjExportAction

debug_show_override_info: bool = False # Private debug variable

class BFU_UL_ActionExportTarget(bpy.types.UIList):

    def print_override_library_actions(self, obj: bpy.types.Object):
        # Debug function
        if not obj.override_library:
            return False
        
        for prop in obj.override_library.properties:
            if prop.rna_path == "bfu_action_asset_list":
                for op in prop.operations:
                    print(f"Override Action: {op.subitem_local_name}")

    def get_data_is_from_linked_file(self, obj: bpy.types.Object, action_name: str) -> bool:
        if not obj.override_library:
            return False

        for prop in obj.override_library.properties:
            if prop.rna_path == "bfu_action_asset_list":
                for op in prop.operations:
                    if op.subitem_local_name == action_name:
                        # This is the overridden action in the current file on the linked file.
                        # If the action exists here that means it a override and the action it not from the linked file.
                        return False
        return True

    def get_object_source_file(self, obj: bpy.types.Object) -> str:
        if not obj.override_library:
            return "<unknown>"

        override_library = obj.override_library
        if(override_library):
            reference = override_library.reference
            if(reference):
                library = reference.library
                if(library):
                    return library.name_full
        return "<unknown>"
    
    
    def get_action_is_from_linked_file(self, action: bpy.types.Action) -> bool:
        if action.library:
            return True
        return False

    def get_action_source_file(self, action: bpy.types.Action) -> str:
        if action.library:
            return action.library.name_full
        return "<unknown>"


    def draw_item(
            self, 
            context: bpy.types.Context, 
            layout: bpy.types.UILayout, 
            data: Optional[Any], 
            item: Optional[Any], 
            icon: Optional[int], 
            active_data: Any, 
            active_property: Optional[str], 
            index: Optional[int],
            flt_flag: Optional[int]
        ):
        action_is_valid = False
        if not isinstance(item, BFU_OT_ObjExportAction):
            return

        if item.name in bpy.data.actions:
            action_is_valid = True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if data and debug_show_override_info:
                print("#############")
                print(self.print_override_library_actions(data))
                print("#############")

            if action_is_valid:  
                # If action is valid
                show_additional_info: bool = bfu_anim_action_props.get_window_manager_debug_show_action_list()
                action: bpy.types.Action = bpy.data.actions[item.name]
                action_detail = layout.row()
                if show_additional_info:  
                    action_detail.alignment = 'LEFT'
                action_detail.prop(
                    action,
                    "name",
                    text="",
                    emboss=False,
                    icon="ACTION"
                )
                
                if show_additional_info:  
                    name: str = action.name
                    first_frame: int = int(action.frame_range[0])
                    last_frame: int = int(action.frame_range[1])
                    frame_range: str = f"({first_frame} - {last_frame})"
                    if data and self.get_data_is_from_linked_file(data, action.name):
                        data_file_name: str = self.get_object_source_file(data)
                    else:
                        data_file_name: str = "Current .blend file"

                    if action and self.get_action_is_from_linked_file(action):
                        action_file_name: str = self.get_action_source_file(action)
                    else:
                        action_file_name: str = "Current .blend file"
                        
                    additional_action_info = f'Name: "{name}" Frames: {frame_range} Data: {data_file_name}, Action: {action_file_name}'
                    action_detail.label(text=additional_action_info, icon="INFO")
                action_use = layout.row()
                if show_additional_info:  
                    pass
                    action_use.alignment = 'RIGHT'
                    action_use.scale_x = 1.15
                action_use.prop(item, "use", text="")
            else:
                # If action is not valid
                name: str = item.name

                if data and self.get_data_is_from_linked_file(data, item.name):
                    data_file_name: str = self.get_object_source_file(data)
                    data_text = (f'Action data "{name}" Not Found. Please update it on the original file: "{data_file_name}"')
                    layout.alert = True
                    layout.label(text=data_text, icon="LIBRARY_DATA_OVERRIDE")
                else:
                    data_text = (f'Action data "{name}" Not found. Please click on update')
                    layout.alert = True
                    layout.label(text=data_text, icon="ERROR")

        # Not optimized for 'GRID' layout type.
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class BFU_OT_UpdateObjActionListButton(bpy.types.Operator):
    bl_label = "Update Action List"
    bl_idname = "object.updateobjactionlist"
    bl_description = "Update the list of actions in this file."

    def execute(self, context: bpy.types.Context) -> Set[Any]:

        
        obj = context.object
        if obj:
            bfu_anim_action_utils.update_export_action_list(obj)
        return {'FINISHED'}
    
class BFU_OT_ClearObjActionListButton(bpy.types.Operator):
    bl_label = "Clear Action List"
    bl_idname = "object.clearobjactionlist"
    bl_description = "Clear the list of actions in this file."

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        obj = context.object
        if obj:
            bfu_anim_action_props.object_clear_action_asset_list(obj)
        return {'FINISHED'}

class BFU_OT_SelectAllObjActionListButton(bpy.types.Operator):
    bl_label = "Select All"
    bl_idname = "object.selectallobjactionlist"
    bl_description = "Select all action list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        obj = context.object
        if obj:
            action_list = bfu_anim_action_props.object_action_asset_list(obj)
            for item in action_list:
                item.use = True
        return {'FINISHED'}

class BFU_OT_DeselectAllObjActionListButton(bpy.types.Operator):
    bl_label = "Deselect All"
    bl_idname = "object.deselectallobjactionlist"
    bl_description = "Deselect all action list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        obj = context.object
        if obj:
            for action_asset in bfu_anim_action_props.object_action_asset_list(obj):
                action_asset.use = False
        return {'FINISHED'}

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_UL_ActionExportTarget,
    BFU_OT_UpdateObjActionListButton,
    BFU_OT_ClearObjActionListButton,
    BFU_OT_SelectAllObjActionListButton,
    BFU_OT_DeselectAllObjActionListButton,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

