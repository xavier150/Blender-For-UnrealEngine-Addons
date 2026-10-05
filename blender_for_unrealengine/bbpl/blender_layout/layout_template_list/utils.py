# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import Optional, Any
from ... import __internal__

def get_template_button_idname(name: str) -> str:
    return __internal__.utils.get_data_operator_idname("tpl_btn_" + name)  # type: ignore

def get_template_button_class_name(name: str) -> str:
    return __internal__.utils.get_operator_class_name("tpl_btn_" + name)  # type: ignore

def get_operator_class_name(name: str) -> str:
    return __internal__.utils.get_operator_class_name(name)  # type: ignore

# ----------------- Template resolution ----------------
# A template (list PropertyGroup) is referenced by its ID owner and its RNA path so operators
# and deferred callbacks can find it back without holding a direct reference.

def get_template_id_data_type(template: Any) -> Optional[str]:
    if isinstance(template.id_data, bpy.types.Scene):
        return "Scene"
    elif isinstance(template.id_data, bpy.types.Object):
        return "Object"
    return None

def resolve_template(id_data_type: str, id_data_name: str, id_data_path: str) -> Optional[Any]:
    if id_data_type == "Scene":
        id_data = bpy.data.scenes.get(id_data_name)
    elif id_data_type == "Object":
        id_data = bpy.data.objects.get(id_data_name)
    else:
        return None
    if id_data is None:
        return None
    try:
        return id_data.path_resolve(id_data_path)
    except ValueError:
        return None

def send_template_data_on_button(button: Any, template: Any) -> None:
    data_type = get_template_id_data_type(template)
    if data_type is None:
        return

    button.target_id_data_path = template.path_from_id()
    button.target_id_data_name = template.id_data.name
    button.target_id_data_type = data_type
    button.target_variable_name = template.get_name()
