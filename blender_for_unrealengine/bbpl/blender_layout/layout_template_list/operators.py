# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

# Action buttons (add / remove / move / duplicate) drawn next to a template list.

import bpy
from . import utils


def get_template_from_button(button):  # type: ignore
    return utils.resolve_template(button.target_id_data_type, button.target_id_data_name, button.target_id_data_path)  # type: ignore

class BBPL_OT_TemplateButtonBase(bpy.types.Operator):
    bl_label = "Template Actions"
    bl_options = {'REGISTER'}  # type: ignore

    target_id_data_path: bpy.props.StringProperty()  # type: ignore
    target_id_data_name: bpy.props.StringProperty()  # type: ignore
    target_id_data_type: bpy.props.StringProperty()  # type: ignore
    target_variable_name: bpy.props.StringProperty()  # type: ignore


# ----------------- Init Class Functions ----------------

def create_template_button_base_class():
    # Create a custom class using addon name to avoid name collision.
    BBPL_OT_TemplateButtonBase.__name__ = utils.get_template_button_class_name("base")
    return BBPL_OT_TemplateButtonBase

def create_template_button_duplicate_class(TemplateButtonBase):  # type: ignore
    # Create a custom class using addon name to avoid name collision.

    class BBPL_OT_TemplateButtonDuplicate(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("duplicate")
        bl_description = "Duplicate active item."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.add()  # type: ignore
            itemToCopy = template.template_collection[template.active_template_property]  # type: ignore
            for k, v in list(itemToCopy.items()):  # type: ignore
                new_item[k] = v
            last_index = len(template.template_collection)-1  # type: ignore
            template.active_template_property = last_index  # type: ignore
            template.sync_display_rows()  # type: ignore
            return {"FINISHED"}

    BBPL_OT_TemplateButtonDuplicate.__name__ = utils.get_template_button_class_name("duplicate")
    return BBPL_OT_TemplateButtonDuplicate

def create_template_button_add_class(TemplateButtonBase):  # type: ignore
    # Create a custom class using addon name to avoid name collision.

    class BBPL_OT_TemplateButtonAdd(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("add")
        bl_description = "Add item."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.add()  # type: ignore
            last_index = len(template.template_collection)-1  # type: ignore
            template.template_collection.move(last_index, template.active_template_property + 10)  # type: ignore
            template.active_template_property = last_index  # type: ignore
            template.sync_display_rows()  # type: ignore
            return {"FINISHED"}
        
    BBPL_OT_TemplateButtonAdd.__name__ = utils.get_template_button_class_name("add")
    return BBPL_OT_TemplateButtonAdd

def create_template_button_remove_class(TemplateButtonBase):  # type: ignore
    # Create a custom class using addon name to avoid name collision.

    class BBPL_OT_TemplateButtonRemove(TemplateButtonBase):  # type: ignore

        bl_idname = utils.get_template_button_idname("remove")
        bl_description = "Remove item."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            template.template_collection.remove(template.active_template_property)  # type: ignore
            template.active_template_property -= 1  # type: ignore
            if template.active_template_property < 0:  # type: ignore
                template.active_template_property = 0  # type: ignore
            template.sync_display_rows()  # type: ignore
            return {"FINISHED"}

    BBPL_OT_TemplateButtonRemove.__name__ = utils.get_template_button_class_name("remove")
    return BBPL_OT_TemplateButtonRemove

def create_template_button_moveup_class(TemplateButtonBase):  # type: ignore
    # Create a custom class using addon name to avoid name collision.

    class BBPL_OT_TemplateButtonMoveUp(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("moveup")
        bl_description = "Move items up."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.move(template.active_template_property, template.active_template_property - 1)  # type: ignore
            if template.active_template_property > 0:  # type: ignore
                template.active_template_property -= 1  # type: ignore
            template.sync_display_rows()  # type: ignore
            return {"FINISHED"}

    BBPL_OT_TemplateButtonMoveUp.__name__ = utils.get_template_button_class_name("moveup")
    return BBPL_OT_TemplateButtonMoveUp

def create_template_button_movedown_class(TemplateButtonBase):  # type: ignore
    # Create an custom class ussing addon name for avoid name collision.

    class BBPL_OT_TemplateButtonMoveDown(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("movedown")
        bl_description = "Move items down."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.move(template.active_template_property, template.active_template_property + 1)  # type: ignore
            if template.active_template_property < len(template.template_collection) - 1:  # type: ignore
                template.active_template_property += 1  # type: ignore
            template.sync_display_rows()  # type: ignore
            return {"FINISHED"}

    BBPL_OT_TemplateButtonMoveDown.__name__ = utils.get_template_button_class_name("movedown")
    return BBPL_OT_TemplateButtonMoveDown

# ----------------- Register ----------------

TemplateButtonsInit = False
BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS = None
BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS = None
BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS = None
BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS = None
BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS = None

def init_doc_template_buttons():
    global TemplateButtonsInit
    if TemplateButtonsInit is False:

        global BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS
        global BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS
        global BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS
        global BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS
        global BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS

        template_button_base = create_template_button_base_class()
        BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS = create_template_button_duplicate_class(template_button_base)
        BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS = create_template_button_add_class(template_button_base)
        BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS = create_template_button_remove_class(template_button_base)
        BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS = create_template_button_moveup_class(template_button_base)
        BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS = create_template_button_movedown_class(template_button_base)
        TemplateButtonsInit = True

init_doc_template_buttons()

def register():
    bpy.utils.register_class(BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS)  # type: ignore

def unregister():
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS)  # type: ignore
