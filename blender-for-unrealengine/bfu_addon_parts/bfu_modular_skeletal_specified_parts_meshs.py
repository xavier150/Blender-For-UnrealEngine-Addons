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

import bpy
from .. import bbpl


def get_preset_values():
    preset_values = [
        'obj.bfu_modular_skeletal_mesh_mode',
        'obj.bfu_modular_skeletal_mesh_every_meshs_separate',
        'obj.bfu_modular_skeletal_specified_parts_meshs_template'
        ]
    return preset_values

BBPL_UI_TemplateItem = bbpl.blender_layout.layout_template_list.types.create_template_item_class()
BBPL_UI_TemplateItemDraw = bbpl.blender_layout.layout_template_list.types.create_template_item_draw_class()
BBPL_UI_TemplateList = bbpl.blender_layout.layout_template_list.types.create_template_list_class(BBPL_UI_TemplateItem, BBPL_UI_TemplateItemDraw)

class BFU_UL_ModularSkeletalSpecifiedPartsTargetItem(BBPL_UI_TemplateItem):
    enabled: bpy.props.BoolProperty(
        name="Use",
        default=True
        )

    target_type: bpy.props.EnumProperty(
        name="Target Type",
        description="Choose the type of target (Object or Collection)",
        items=[
            ('OBJECT', 'Object', 'Use an Object as the target'),
            ('COLLECTION', 'Collection', 'Use a Collection as the target'),
        ],
        default='OBJECT',
    )

    obj: bpy.props.PointerProperty(
        name="Obj target",
        description="Target object for modular skeletal mesh.",
        type=bpy.types.Object,
    )

    collection: bpy.props.PointerProperty(
        name="Collection target",
        description="Target collection for modular skeletal mesh.",
        type=bpy.types.Collection,
    )


class BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw(BBPL_UI_TemplateItemDraw):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "enabled", text="")

        #icon = bbpl.ui_utils.getIconByGroupTheme(item.theme)
        icon = "NONE"

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "target_type", text="")
        if item.target_type == "OBJECT":
            prop_data.prop(item, "obj", text="")
        elif item.target_type == "COLLECTION":
            prop_data.prop(item, "collection", text="")
        prop_data.enabled = item.enabled

    
class BFU_ModularSkeletalSpecifiedPartsTargetList(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsTargetItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw")
    rows: bpy.props.IntProperty(default = 3)
    maxrows: bpy.props.IntProperty(default = 3)




class BFU_UL_ModularSkeletalSpecifiedPartsMeshItem(BBPL_UI_TemplateItem):
    enabled: bpy.props.BoolProperty(
        name="Use",
        default=True
        )

    name: bpy.props.StringProperty(
        name="Bone groups name",
        description="Your bone group",
        default="MyGroup",
        )
    
    skeletal_parts: bpy.props.PointerProperty(
       type=BFU_ModularSkeletalSpecifiedPartsTargetList
       )

class BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw(BBPL_UI_TemplateItemDraw):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        prop_line = layout

        indexText = layout.row()
        indexText.alignment = 'LEFT'
        indexText.scale_x = 1
        indexText.label(text=str(index))

        prop_use = prop_line.row()
        prop_use.alignment = 'LEFT'
        prop_use.prop(item, "enabled", text="")

        prop_data = prop_line.row()
        prop_data.alignment = 'EXPAND'
        prop_data.prop(item, "name", text="")
        if item.enabled:
            obj_len = 0
            col_len = 0
            for part_item in item.skeletal_parts.get_template_collection():
                if part_item.target_type == "OBJECT":
                    obj_len += 1
                elif part_item.target_type == "COLLECTION":
                    col_len += 1
            preview_text = str(obj_len) + " obj(s) and " + str(col_len) + " collections(s)."
            prop_data.label(text=preview_text)

            if obj_len+col_len == 0:
                prop_data.label(text="", icon="ERROR")
        prop_data.enabled = item.enabled

    
class BFU_ModularSkeletalSpecifiedPartsMeshs(BBPL_UI_TemplateList):
    template_collection: bpy.props.CollectionProperty(type=BFU_UL_ModularSkeletalSpecifiedPartsMeshItem)
    template_collection_uilist_class: bpy.props.StringProperty(default = "BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw")
    def draw(self, layout: bpy.types.UILayout):
        super().draw(layout)

        box = layout.box()  # Créez un box dans le layout courant
        item = self.get_active_item()
        box
        if item:
            prop_line = box.row()
            prop_use = prop_line.row()
            prop_use.alignment = 'LEFT'
            prop_use.prop(item, "enabled", text="enabled")

            prop_data = prop_line.row()
            prop_data.alignment = 'EXPAND'
            prop_data.prop(item, "name", text="")
            prop_data.enabled = item.enabled

            item.skeletal_parts.draw(box).enabled = item.enabled
        


classes = (
    BFU_UL_ModularSkeletalSpecifiedPartsTargetItem,
    BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw,
    BFU_ModularSkeletalSpecifiedPartsTargetList,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItem,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw,
    BFU_ModularSkeletalSpecifiedPartsMeshs,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_modular_skeletal_mesh_mode = bpy.props.EnumProperty(
        name="Modular Skeletal Mesh Mode",
        description='Modular skeletal mesh mode',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("all_in_one",
                "All In One",
                "Export all child meshs  of the armature as one skeletal mesh.",
                1),
            ("every_meshs",
                "Every Meshs",
                "Export one skeletal mesh for every child meshs of the armature.",
                2),
            ("specified_parts",
                "Specified Parts",
                "Export specified mesh parts.",
                3)
            ]
        )
    
    bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate = bpy.props.StringProperty(
        name="Separate string",
        description="String between armature name and mesh name",
        override={'LIBRARY_OVERRIDABLE'},
        default="_"
        )


    bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template = bpy.props.PointerProperty(type=BFU_ModularSkeletalSpecifiedPartsMeshs)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template
    del bpy.types.Object.bfu_modular_skeletal_mesh_every_meshs_separate
    del bpy.types.Object.bfu_modular_skeletal_mesh_mode