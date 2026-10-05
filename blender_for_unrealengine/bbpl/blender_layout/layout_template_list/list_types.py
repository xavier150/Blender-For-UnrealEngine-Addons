# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

# The template list PropertyGroup: holds the item collection, the active index, the optional
# categories overlay and draws the UIList with its action buttons.

import bpy
from typing import List, Tuple
from . import utils
from . import category_types


def create_template_list_class(TemplateItem, TemplateItemDraw):  # type: ignore

    class BBPL_UI_TemplateList(bpy.types.PropertyGroup):
        template_collection: bpy.props.CollectionProperty(type = TemplateItem)  # type: ignore
        template_collection_uilist_class_name = ""
        # Opt-in overlay: items are grouped under collapsible headers by get_item_category().
        # When enabled the template_list shows `display_rows` (synced from template_collection)
        # instead of the collection itself; rows/maxrows are ignored.
        use_categories = False
        active_template_property: bpy.props.IntProperty(default = 0, update = category_types.on_active_template_property_update)  # type: ignore
        rows: bpy.props.IntProperty(default = 6)  # type: ignore
        maxrows: bpy.props.IntProperty(default = 6)  # type: ignore
        category_states: bpy.props.CollectionProperty(type = category_types.BBPL_UI_TemplateCategoryState_CUSTOM_CLASS)  # type: ignore
        display_rows: bpy.props.CollectionProperty(type = category_types.BBPL_UI_TemplateDisplayRow_CUSTOM_CLASS)  # type: ignore
        active_display_row: bpy.props.IntProperty(default = 0, update = category_types.on_active_display_row_update)  # type: ignore


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

        # ----------------- Categories ----------------

        def get_item_category(self, item) -> str:  # type: ignore
            # Override to return the category of an item. "" means no category (root).
            return ""

        def get_category_state(self, category: str):  # type: ignore
            return self.category_states.get(category)  # type: ignore

        def is_category_expanded(self, category: str) -> bool:
            state = self.category_states.get(category)  # type: ignore
            if state is None:
                return True
            return state.expanded  # type: ignore

        def set_category_expanded(self, category: str, expanded: bool) -> None:
            state = self.category_states.get(category)  # type: ignore
            if state is None:
                state = self.category_states.add()  # type: ignore
                state.name = category
            state.expanded = expanded

        def get_item_indexes_by_category(self):  # type: ignore
            # Categories are ordered by first appearance in the item list.
            indexes_by_category = {}
            for index, item in enumerate(self.template_collection):  # type: ignore
                category = self.get_item_category(item)  # type: ignore
                indexes_by_category.setdefault(category, []).append(index)
            return indexes_by_category

        def compute_display_rows(self) -> List[Tuple[bool, str, int]]:
            # Rows as (is_category, category, item_index). Root items keep their position,
            # a category header (followed by its items if expanded) is placed where it first appears.
            indexes_by_category = self.get_item_indexes_by_category()  # type: ignore
            rows: List[Tuple[bool, str, int]] = []
            done = set()
            for index, item in enumerate(self.template_collection):  # type: ignore
                category = self.get_item_category(item)  # type: ignore
                if category == "":
                    rows.append((False, "", index))
                elif category not in done:
                    done.add(category)
                    rows.append((True, category, -1))
                    if self.is_category_expanded(category):
                        for item_index in indexes_by_category[category]:
                            rows.append((False, category, item_index))
            return rows

        def display_rows_need_sync(self) -> bool:
            expected = self.compute_display_rows()
            if len(expected) != len(self.display_rows):  # type: ignore
                return True
            for row, (is_category, category, item_index) in zip(self.display_rows, expected):  # type: ignore
                if row.is_category != is_category or row.category != category or row.item_index != item_index:
                    return True
            return False

        def sync_display_rows(self) -> None:
            # Must be called outside of draw (operators, update callbacks, timers).
            if not self.use_categories:
                return
            self.display_rows.clear()  # type: ignore
            for is_category, category, item_index in self.compute_display_rows():
                row = self.display_rows.add()  # type: ignore
                row.is_category = is_category
                row.category = category
                row.item_index = item_index
            self.sync_active_display_row()

        def sync_active_display_row(self) -> None:
            # Point active_display_row to the active item row, or to its category header when collapsed.
            if not self.use_categories:
                return
            active = self.active_template_property  # type: ignore
            target = -1
            for index, row in enumerate(self.display_rows):  # type: ignore
                if not row.is_category and row.item_index == active:
                    target = index
                    break
            if target == -1 and 0 <= active < len(self.template_collection):  # type: ignore
                category = self.get_item_category(self.template_collection[active])  # type: ignore
                for index, row in enumerate(self.display_rows):  # type: ignore
                    if row.is_category and row.category == category:
                        target = index
                        break
            if target != -1 and self.active_display_row != target:  # type: ignore
                category_types.set_active_display_row_silently(self, target)

        # ----------------- Draw ----------------

        def draw(self, layout: bpy.types.UILayout) -> bpy.types.UILayout:
            template_row = layout.row()
            if self.template_collection_uilist_class_name == "":
                print("template_collection_uilist_class_name was not set!")

            elif self.use_categories:
                if self.display_rows_need_sync():
                    category_types.request_deferred_display_rows_sync(self)
                rows = max(1, len(self.display_rows))  # type: ignore
                template_row.template_list(  # type: ignore
                    self.template_collection_uilist_class_name, "",
                    self, "display_rows",
                    self, "active_display_row",
                    rows=rows,  # type: ignore
                    maxrows=rows,  # type: ignore
                    )

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
            utils.send_template_data_on_button(button_add, self)
            button_remove = template_column.operator(utils.get_template_button_idname("remove"), icon='REMOVE', text="")  # type: ignore
            utils.send_template_data_on_button(button_remove, self)
            button_moveup = template_column.operator(utils.get_template_button_idname("moveup"), icon='TRIA_UP', text="")  # type: ignore
            utils.send_template_data_on_button(button_moveup, self)
            button_movedown = template_column.operator(utils.get_template_button_idname("movedown"), icon='TRIA_DOWN', text="")  # type: ignore
            utils.send_template_data_on_button(button_movedown, self)
            button_duplicate = template_column.operator(utils.get_template_button_idname("duplicate"), icon='ADD', text="")  # type: ignore
            utils.send_template_data_on_button(button_duplicate, self)
            return template_row


    BBPL_UI_TemplateList.__name__ = utils.get_operator_class_name("TemplateList")
    return BBPL_UI_TemplateList
