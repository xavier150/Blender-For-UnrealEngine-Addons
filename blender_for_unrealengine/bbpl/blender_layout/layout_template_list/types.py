# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import Optional, Any
from . import utils


# ----------------- Class Functions ----------------

def send_template_data_on_button(button, template):  # type: ignore
    if isinstance(template.id_data, bpy.types.Scene):  # type: ignore
        data_type = "Scene"
    elif isinstance(template.id_data, bpy.types.Object):  # type: ignore
        data_type = "Object"
    else:
        return

    button.target_id_data_path = template.path_from_id()  # type: ignore
    button.target_id_data_name = template.id_data.name
    button.target_id_data_type = data_type
    button.target_variable_name = template.get_name()  # type: ignore

class BBPL_UI_TemplateItem(bpy.types.PropertyGroup):
    use: bpy.props.BoolProperty(  # type: ignore
        name="Use",
        default=True
        )  # type: ignore

    name: bpy.props.StringProperty(  # type: ignore
        name="Bone groups name",
        description="Your bone group",
        default="MyGroup",
        )  # type: ignore
    
class BBPL_UL_TemplateItemDraw(bpy.types.UIList):
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
    ) -> None:

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))  # type: ignore

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "use", text="")  # type: ignore

        #icon = bbpl.ui_utils.getIconByGroupTheme(item.theme)
        icon = "NONE"  # type: ignore

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "name", text="")  # type: ignore
        prop_data.enabled = item.use  # type: ignore
    
# ----------------- Init Template Class Functions ----------------

def create_template_item_class():        
    BBPL_UI_TemplateItem.__name__ = utils.get_operator_class_name("TemplateItem")
    return BBPL_UI_TemplateItem

def create_template_item_draw_class():
    BBPL_UL_TemplateItemDraw.__name__ = utils.get_operator_class_name("TemplateItemDraw")
    return BBPL_UL_TemplateItemDraw

def create_template_list_class(TemplateItem, TemplateItemDraw):  # type: ignore

    class BBPL_UI_TemplateList(bpy.types.PropertyGroup):
        template_collection: bpy.props.CollectionProperty(type = TemplateItem)  # type: ignore
        template_collection_uilist_class_name = ""
        active_template_property: bpy.props.IntProperty(default = 0)  # type: ignore
        rows: bpy.props.IntProperty(default = 6)  # type: ignore
        maxrows: bpy.props.IntProperty(default = 6)  # type: ignore


        def __len__(self):
            return len(self.template_collection)  # type: ignore
        
        def __iter__(self):  # type: ignore
            return iter(self.template_collection)  # type: ignore
        
        def __getitem__(self, index):  # type: ignore
            return self.template_collection[index]  # type: ignore
        
        def find(self, item):  # type: ignore
            return self.template_collection.find(item)  # type: ignore
        
        def clear(self):  # type: ignore
            return self.template_collection.clear()  # type: ignore
        
        def add(self):  # type: ignore
            return self.template_collection.add()  # type: ignore

        def items(self):  # type: ignore
            return self.template_collection.items()  # type: ignore

        def get_template_collection(self):  # type: ignore
            return self.template_collection  # type: ignore
        
        def get_active_index(self):  # type: ignore
            return self.active_template_property  # type: ignore
        
        def get_active_item(self):  # type: ignore
            if len(self.template_collection) > 0:  # type: ignore
                return self.template_collection[self.active_template_property]  # type: ignore

        def get_name(self):
            if bpy.app.version >= (3, 0, 0):
                prop_name = self.id_properties_ensure().name
                return prop_name
            else:
                prop_name = self.path_from_id()
                return prop_name

        def draw(self, layout: bpy.types.UILayout) -> bpy.types.UILayout:
            template_row = layout.row()
            if self.template_collection_uilist_class_name == "":
                print("template_collection_uilist_class_name was not set!")

            else:
                template_row.template_list(  # type: ignore
                    self.template_collection_uilist_class_name, "",  # type and unique id
                    self, "template_collection",  # pointer to the CollectionProperty
                    self, "active_template_property",  # pointer to the active identifier
                    rows=self.rows,  # type: ignore
                    maxrows=self.maxrows,  # type: ignore
                    )


            template_column = template_row.column(align=True)
            button_add = template_column.operator(utils.get_template_button_idname("add"), icon='ADD', text="")  # type: ignore
            send_template_data_on_button(button_add, self)
            button_remove = template_column.operator(utils.get_template_button_idname("remove"), icon='REMOVE', text="")  # type: ignore
            send_template_data_on_button(button_remove, self)
            button_moveup = template_column.operator(utils.get_template_button_idname("moveup"), icon='TRIA_UP', text="")  # type: ignore
            send_template_data_on_button(button_moveup, self)
            button_movedown = template_column.operator(utils.get_template_button_idname("movedown"), icon='TRIA_DOWN', text="")  # type: ignore
            send_template_data_on_button(button_movedown, self)
            button_duplicate = template_column.operator(utils.get_template_button_idname("duplicate"), icon='ADD', text="")  # type: ignore
            send_template_data_on_button(button_duplicate, self)
            return template_row


    BBPL_UI_TemplateList.__name__ = utils.get_operator_class_name("TemplateList")
    return BBPL_UI_TemplateList

# ----------------- Template Button Class ----------------

def get_template_from_button(button):  # type: ignore

    if button.target_id_data_type == "Scene":  # type: ignore
        scene = bpy.data.scenes[button.target_id_data_name]  # type: ignore
        #return getattr(scene, button.target_variable_name)
        return scene.path_resolve(button.target_id_data_path)  # type: ignore
        

    if button.target_id_data_type == "Object":  # type: ignore
        obj = bpy.data.objects[button.target_id_data_name]  # type: ignore
        #return getattr(obj, button.target_variable_name)
        return obj.path_resolve(button.target_id_data_path)  # type: ignore

class BBPL_OT_TemplateButtonBase(bpy.types.Operator):
    bl_label = "Template Actions"
    bl_options = {'REGISTER'}  # type: ignore

    target_id_data_path: bpy.props.StringProperty()  # type: ignore
    target_id_data_name: bpy.props.StringProperty()  # type: ignore
    target_id_data_type: bpy.props.StringProperty()  # type: ignore
    target_variable_name: bpy.props.StringProperty()  # type: ignore


# ----------------- Init Template button Class Functions ----------------

def create_template_button_base_class():
    # Create an custom class ussing addon name for avoid name collision.
    BBPL_OT_TemplateButtonBase.__name__ = utils.get_template_button_class_name("base")
    return BBPL_OT_TemplateButtonBase

def create_template_button_duplicate_class(TemplateButtonBase):  # type: ignore
    # Create an custom class ussing addon name for avoid name collision.

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
            return {"FINISHED"}

    BBPL_OT_TemplateButtonDuplicate.__name__ = utils.get_template_button_class_name("duplicate")
    return BBPL_OT_TemplateButtonDuplicate

def create_template_button_add_class(TemplateButtonBase):  # type: ignore
    # Create an custom class ussing addon name for avoid name collision.

    class BBPL_OT_TemplateButtonAdd(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("add")
        bl_description = "Add item."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.add()  # type: ignore
            last_index = len(template.template_collection)-1  # type: ignore
            template.template_collection.move(last_index, template.active_template_property + 10)  # type: ignore
            template.active_template_property = last_index  # type: ignore
            return {"FINISHED"}
        
    BBPL_OT_TemplateButtonAdd.__name__ = utils.get_template_button_class_name("add")
    return BBPL_OT_TemplateButtonAdd

def create_template_button_remove_class(TemplateButtonBase):  # type: ignore
    # Create an custom class ussing addon name for avoid name collision.

    class BBPL_OT_TemplateButtonRemove(TemplateButtonBase):  # type: ignore

        bl_idname = utils.get_template_button_idname("remove")
        bl_description = "remove item."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            template.template_collection.remove(template.active_template_property)  # type: ignore
            template.active_template_property -= 1  # type: ignore
            if template.active_template_property < 0:  # type: ignore
                template.active_template_property = 0  # type: ignore
            return {"FINISHED"}

    BBPL_OT_TemplateButtonRemove.__name__ = utils.get_template_button_class_name("remove")
    return BBPL_OT_TemplateButtonRemove

def create_template_button_moveup_class(TemplateButtonBase):  # type: ignore
    # Create an custom class ussing addon name for avoid name collision.

    class BBPL_OT_TemplateButtonMoveUp(TemplateButtonBase):  # type: ignore
        bl_idname = utils.get_template_button_idname("moveup")
        bl_description = "Move items up."

        def invoke(self, context, event):  # type: ignore
            template = get_template_from_button(self)  # type: ignore
            new_item = template.template_collection.move(template.active_template_property, template.active_template_property - 1)  # type: ignore
            if template.active_template_property > 0:  # type: ignore
                template.active_template_property -= 1  # type: ignore
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

classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore

    global BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS

    bpy.utils.register_class(BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS)  # type: ignore


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore

    global BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS
    global BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS

    bpy.utils.unregister_class(BBPL_OT_TemplateButtonMoveDown_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonMoveUp_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonRemove_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonAdd_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_OT_TemplateButtonDuplicate_CUSTOM_CLASS)  # type: ignore



