# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

# Categories overlay of a template list: per-category expanded state, display rows shown by the
# UIList instead of the real collection, and the selection sync between both.

import bpy
from typing import Any
from . import utils


class BBPL_UI_TemplateCategoryState(bpy.types.PropertyGroup):
    # `name` is the category key so `category_states.get("MyCategory")` works as a map lookup.
    name: bpy.props.StringProperty()  # type: ignore
    expanded: bpy.props.BoolProperty(  # type: ignore
        name="Expanded",
        description="Click to expand / collapse",
        default=True
        )  # type: ignore

class BBPL_UI_TemplateDisplayRow(bpy.types.PropertyGroup):
    # A row shown by the template_list in categories mode: a category header or a real item reference.
    is_category: bpy.props.BoolProperty(default=False)  # type: ignore
    category: bpy.props.StringProperty()  # type: ignore
    item_index: bpy.props.IntProperty(default=-1)  # type: ignore

# ----------------- Selection sync ----------------

# Guards against update callbacks re-triggering each other while syncing selection.
_display_sync_guard = False
# Templates (id type, id name, path) waiting for a deferred display rows sync (requested from draw()).
_pending_display_sync = set()

def set_active_display_row_silently(template: Any, index: int) -> None:
    # Set active_display_row without triggering the selection update callback.
    global _display_sync_guard
    previous_guard = _display_sync_guard
    _display_sync_guard = True
    try:
        template.active_display_row = index
    finally:
        _display_sync_guard = previous_guard

def on_active_display_row_update(self: Any, context: bpy.types.Context) -> None:
    global _display_sync_guard
    if _display_sync_guard:
        return
    rows = self.display_rows
    index = self.active_display_row
    if not 0 <= index < len(rows):
        return
    row = rows[index]
    _display_sync_guard = True
    try:
        if row.is_category:
            # Clicking a category row toggles it, the selection goes back to the active item.
            self.set_category_expanded(row.category, not self.is_category_expanded(row.category))
            self.sync_display_rows()
        else:
            self.active_template_property = row.item_index
    finally:
        _display_sync_guard = False

def on_active_template_property_update(self: Any, context: bpy.types.Context) -> None:
    if _display_sync_guard:
        return
    self.sync_active_display_row()

def request_deferred_display_rows_sync(template: Any) -> None:
    # draw() can't write properties, so the sync is deferred to a timer.
    data_type = utils.get_template_id_data_type(template)
    if data_type is None:
        return
    key = (data_type, template.id_data.name, template.path_from_id())
    if key in _pending_display_sync:
        return
    _pending_display_sync.add(key)

    def deferred_sync():
        _pending_display_sync.discard(key)
        resolved = utils.resolve_template(*key)
        if resolved is not None:
            resolved.sync_display_rows()
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
        return None

    bpy.app.timers.register(deferred_sync, first_interval=0.0)

# ----------------- Init Class Functions ----------------

def create_template_category_state_class():
    BBPL_UI_TemplateCategoryState.__name__ = utils.get_operator_class_name("TemplateCategoryState")
    return BBPL_UI_TemplateCategoryState

def create_template_display_row_class():
    BBPL_UI_TemplateDisplayRow.__name__ = utils.get_operator_class_name("TemplateDisplayRow")
    return BBPL_UI_TemplateDisplayRow

# ----------------- Register ----------------

BBPL_UI_TemplateCategoryState_CUSTOM_CLASS = create_template_category_state_class()
BBPL_UI_TemplateDisplayRow_CUSTOM_CLASS = create_template_display_row_class()

def register():
    bpy.utils.register_class(BBPL_UI_TemplateCategoryState_CUSTOM_CLASS)  # type: ignore
    bpy.utils.register_class(BBPL_UI_TemplateDisplayRow_CUSTOM_CLASS)  # type: ignore

def unregister():
    bpy.utils.unregister_class(BBPL_UI_TemplateDisplayRow_CUSTOM_CLASS)  # type: ignore
    bpy.utils.unregister_class(BBPL_UI_TemplateCategoryState_CUSTOM_CLASS)  # type: ignore
