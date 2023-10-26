# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

import bpy

# Définissez un dictionnaire global pour stocker des références aux instances de PropertyGroup

def send_template_data_on_button(button, template):

    if isinstance(template.id_data, bpy.types.Scene):
        data_type = "Scene"
    elif isinstance(template.id_data, bpy.types.Object):
        data_type = "Object"
    else:
        return

    button.target_id_data_path = template.path_from_id()
    button.target_id_data_name = template.id_data.name
    button.target_id_data_type = data_type
    button.target_variable_name = template.get_name()

def get_template_from_button(button):

    

    if button.target_id_data_type == "Scene":
        scene = bpy.data.scenes[button.target_id_data_name]
        #return getattr(scene, button.target_variable_name)
        return scene.path_resolve(button.target_id_data_path)
        

    if button.target_id_data_type == "Object":
        obj = bpy.data.objects[button.target_id_data_name]
        #return getattr(obj, button.target_variable_name)
        return obj.path_resolve(button.target_id_data_path)




class BBPL_UI_TemplateItem(bpy.types.PropertyGroup):
    use: bpy.props.BoolProperty(
        name="Use",
        default=True
        )

    name: bpy.props.StringProperty(
        name="Bone groups name",
        description="Your bone group",
        default="MyGroup",
        )


class BBPL_UI_TemplateItemDraw(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "use", text="")

        #icon = bbpl.ui_utils.getIconByGroupTheme(item.theme)
        icon = "NONE"

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "name", text="")
        prop_data.enabled = item.use


class BBPL_UI_TemplateList(bpy.types.PropertyGroup):

    template_collection: bpy.props.CollectionProperty(type = BBPL_UI_TemplateItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BBPL_UI_TemplateItemDraw")
    active_template_property: bpy.props.IntProperty(default = 0)

    def get_template_collection(self):
        return self.template_collection
    
    def get_active_index(self):
        return self.active_template_property
    
    def get_active_item(self):
        if len(self.template_collection) > 0:
            return self.template_collection[self.active_template_property]

    def get_name(self):
        #ath_from_id()

        prop_name = self.id_properties_ensure().name
        #print(self.id_properties_ensure())
        #self.id_data.bl_rna.properties[prop_name].path_from_id("template_collection")
        #print(self.path_from_id())
        return prop_name

    def draw(self, layout: bpy.types.UILayout):

        template_row = layout.row()
        template_row.template_list(
            self.template_collection_uilist_class, "",  # type and unique id
            self, "template_collection",  # pointer to the CollectionProperty
            self, "active_template_property",  # pointer to the active identifier
            rows=6,
            maxrows=6
            )


        template_column = template_row.column(align=True)
        button_add = template_column.operator("data.template_button_add", icon='ADD', text="")
        send_template_data_on_button(button_add, self)
        button_remove = template_column.operator("data.template_button_remove", icon='REMOVE', text="")
        send_template_data_on_button(button_remove, self)
        button_moveup = template_column.operator("data.template_button_moveup", icon='TRIA_UP', text="")
        send_template_data_on_button(button_moveup, self)
        button_movedown = template_column.operator("data.template_button_movedown", icon='TRIA_DOWN', text="")
        send_template_data_on_button(button_movedown, self)
        button_duplicate = template_column.operator("data.template_button_duplicate", icon='ADD', text="")
        send_template_data_on_button(button_duplicate, self)


class BBPL_OT_TemplateButtonBase (bpy.types.Operator):
    bl_label = "Template Actions"
    bl_options = {'REGISTER'}

    target_id_data_path: bpy.props.StringProperty()
    target_id_data_name: bpy.props.StringProperty()
    target_id_data_type: bpy.props.StringProperty()
    target_variable_name: bpy.props.StringProperty()


class BBPL_OT_TemplateButtonDuplicate (BBPL_OT_TemplateButtonBase):
    bl_idname = "data.template_button_duplicate"
    bl_description = "Duplicate active item."

    def invoke(self, context, event):
        template = get_template_from_button(self)
        new_item = template.template_collection.add()
        itemToCopy = template.template_collection[template.active_template_property]
        for k, v in list(itemToCopy.items()):
            new_item[k] = v
        last_index = len(template.template_collection)-1
        template.active_template_property = last_index
        return {"FINISHED"}


class BBPL_OT_TemplateButtonAdd(BBPL_OT_TemplateButtonBase):
    bl_idname = "data.template_button_add"
    bl_description = "Add item."

    def invoke(self, context, event):
        template = get_template_from_button(self)
        new_item = template.template_collection.add()
        last_index = len(template.template_collection)-1
        template.template_collection.move(
            last_index,
            template.active_template_property + 10
            )
        template.active_template_property = last_index
        return {"FINISHED"}



class BBPL_OT_TemplateButtonRemove(BBPL_OT_TemplateButtonBase):
    bl_idname = "data.template_button_remove"
    bl_description = "remove item."

    def invoke(self, context, event):
        template = get_template_from_button(self)
        template.template_collection.remove(template.active_template_property)
        template.active_template_property -= 1
        if template.active_template_property < 0:
            template.active_template_property = 0
        return {"FINISHED"}


class BBPL_OT_TemplateButtonMoveUp(BBPL_OT_TemplateButtonBase):
    bl_idname = "data.template_button_moveup"
    bl_description = "Move items up."

    def invoke(self, context, event):
        template = get_template_from_button(self)
        new_item = template.template_collection.move(
            template.active_template_property,
            template.active_template_property-1
            )
        if template.active_template_property > 0:
            template.active_template_property -= 1
        return {"FINISHED"}


class BBPL_OT_TemplateButtonMoveDown(BBPL_OT_TemplateButtonBase):
    bl_idname = "data.template_button_movedown"
    bl_description = "Move items down."

    def invoke(self, context, event):
        template = get_template_from_button(self)
        new_item = template.template_collection.move(
            template.active_template_property,
            template.active_template_property+1
            )
        if template.active_template_property < len(template.template_collection)-1:
            template.active_template_property += 1
        return {"FINISHED"}



classes = (
    BBPL_OT_TemplateButtonDuplicate,
    BBPL_OT_TemplateButtonAdd,
    BBPL_OT_TemplateButtonRemove,
    BBPL_OT_TemplateButtonMoveUp,
    BBPL_OT_TemplateButtonMoveDown,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)