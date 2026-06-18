# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .. import bbpl
from typing import TYPE_CHECKING, List


BBPL_UI_TemplateItem = bbpl.blender_layout.layout_template_list.types.create_template_item_class()
BBPL_UL_TemplateItemDraw = bbpl.blender_layout.layout_template_list.types.create_template_item_draw_class()
BBPL_UI_TemplateList = bbpl.blender_layout.layout_template_list.types.create_template_list_class(BBPL_UI_TemplateItem, BBPL_UL_TemplateItemDraw)

class BFU_UI_ModularSkeletalSpecifiedPartsTargetItem(BBPL_UI_TemplateItem): # Item class (bpy.types.PropertyGroup)


    if TYPE_CHECKING:
        enabled: bool
        target_type: str
        obj: bpy.types.Object
        collection: bpy.types.Collection
    else:
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

class BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw(BBPL_UL_TemplateItemDraw): # Draw Item class (bpy.types.UIList)
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
    
class BFU_UI_ModularSkeletalSpecifiedPartsTargetList(BBPL_UI_TemplateList): # Draw Item class (bpy.types.UIList)
    template_collection: bpy.props.CollectionProperty(type=BFU_UI_ModularSkeletalSpecifiedPartsTargetItem)
    template_collection_uilist_class_name = "BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw"
    rows: bpy.props.IntProperty(default = 3)
    maxrows: bpy.props.IntProperty(default = 3)

    if TYPE_CHECKING:
        template_collection: List[BFU_UI_ModularSkeletalSpecifiedPartsTargetItem]
        def get_template_collection(self) -> List[BFU_UI_ModularSkeletalSpecifiedPartsTargetItem]:
            return self.template_collection

class BFU_UI_ModularSkeletalSpecifiedPartsMeshItem(BBPL_UI_TemplateItem): # Item class (bpy.types.PropertyGroup)

    
    if TYPE_CHECKING:
        enabled: bool
        name: str
        sub_folder: str
        skeletal_parts: BFU_UI_ModularSkeletalSpecifiedPartsTargetList
    else:
        enabled: bpy.props.BoolProperty(
            name="Use",
            default=True
            )

        name: bpy.props.StringProperty(
            name="Name",
            description="Bone group name.",
            default="MyGroupName",
            )
        
        sub_folder: bpy.props.StringProperty(
            name="Sub Folder",
            description="sub_folder_to export the mesh",
            default="",
            )
        
        skeletal_parts: bpy.props.PointerProperty(
            type=BFU_UI_ModularSkeletalSpecifiedPartsTargetList
        )

class BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw(BBPL_UL_TemplateItemDraw): # Draw Item class (bpy.types.UIList)
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
        prop_data.enabled = item.enabled
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
 
class BFU_UI_ModularSkeletalSpecifiedPartsMeshs(BBPL_UI_TemplateList): # Draw Item class (bpy.types.UIList)
    template_collection: bpy.props.CollectionProperty(type=BFU_UI_ModularSkeletalSpecifiedPartsMeshItem)
    template_collection_uilist_class_name = "BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw"
    
    if TYPE_CHECKING:
        template_collection: List[BFU_UI_ModularSkeletalSpecifiedPartsMeshItem]
        def get_template_collection(self) -> List[BFU_UI_ModularSkeletalSpecifiedPartsMeshItem]:
            return self.template_collection

    def draw(self, layout: bpy.types.UILayout):
        super().draw(layout)

        box = layout.box()  # Create a box in the current layout
        item = self.get_active_item()
        box
        if item:
            prop_data = box.column()
            prop_data.enabled = item.enabled
            prop_data.prop(item, "name", text="")
            prop_data.prop(item, "sub_folder", text="")

            item.skeletal_parts.draw(box).enabled = item.enabled


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_UI_ModularSkeletalSpecifiedPartsTargetItem,
    BFU_UL_ModularSkeletalSpecifiedPartsTargetItemDraw,
    BFU_UI_ModularSkeletalSpecifiedPartsTargetList,

    BFU_UI_ModularSkeletalSpecifiedPartsMeshItem,
    BFU_UL_ModularSkeletalSpecifiedPartsMeshItemDraw,
    BFU_UI_ModularSkeletalSpecifiedPartsMeshs,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template = bpy.props.PointerProperty(type=BFU_UI_ModularSkeletalSpecifiedPartsMeshs)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_modular_skeletal_specified_parts_meshs_template