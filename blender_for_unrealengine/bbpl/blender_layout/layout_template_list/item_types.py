# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

# Base item (PropertyGroup) and base item drawer (UIList) of a template list.

import bpy
import fnmatch
from typing import Optional, Any
from . import utils


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
        # Categories mode: the list shows `display_rows`, `item` is a row that is either a category
        # header or a reference to a real item. Subclasses should override draw_item_content().
        if getattr(data, "use_categories", False):
            if item.is_category:  # type: ignore
                tria_icon = 'TRIA_DOWN' if data.is_category_expanded(item.category) else 'TRIA_RIGHT'  # type: ignore
                layout.label(text=item.category, icon=tria_icon)  # type: ignore
                return

            collection = data.template_collection  # type: ignore
            if not 0 <= item.item_index < len(collection):  # type: ignore
                layout.label(text="", icon='ERROR')
                return
            if item.category != "":  # type: ignore
                layout = layout.row(align=True)
                layout.separator(factor=2.0)
            self.draw_item_content(context, layout, data, collection[item.item_index], icon, active_data, active_property, item.item_index, flt_flag)  # type: ignore
            return

        self.draw_item_content(context, layout, data, item, icon, active_data, active_property, index, flt_flag)

    def draw_item_content(
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

    def filter_items(self, context: bpy.types.Context, data: Any, propname: str):  # type: ignore
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []

        if getattr(data, "use_categories", False):
            # Rows are already ordered by sync_display_rows(). Name filter applies to the real items,
            # category headers always stay visible.
            flt_flags = [self.bitflag_filter_item] * len(items)
            if self.filter_name:
                pattern = "*" + self.filter_name + "*"
                collection = data.template_collection  # type: ignore
                for index, row in enumerate(items):
                    if row.is_category or not 0 <= row.item_index < len(collection):
                        continue
                    if not fnmatch.fnmatch(collection[row.item_index].name, pattern):
                        flt_flags[index] &= ~self.bitflag_filter_item
            return flt_flags, flt_neworder

        # Default UIList behavior (name filter / alphabetical sort). Invert and reverse are handled by Blender.
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "name")  # type: ignore
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)
        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(items, "name")  # type: ignore
        return flt_flags, flt_neworder

# ----------------- Init Class Functions ----------------

def create_template_item_class():        
    BBPL_UI_TemplateItem.__name__ = utils.get_operator_class_name("TemplateItem")
    return BBPL_UI_TemplateItem

def create_template_item_draw_class():
    BBPL_UL_TemplateItemDraw.__name__ = utils.get_operator_class_name("TemplateItemDraw")
    return BBPL_UL_TemplateItemDraw
