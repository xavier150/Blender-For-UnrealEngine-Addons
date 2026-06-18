# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from ... import __internal__

def get_template_button_idname(name: str) -> str:
    return __internal__.utils.get_data_operator_idname("tpl_btn_" + name)  # type: ignore

def get_template_button_class_name(name: str) -> str:
    return __internal__.utils.get_operator_class_name("tpl_btn_" + name)  # type: ignore

def get_operator_class_name(name: str) -> str:
    return __internal__.utils.get_operator_class_name(name)  # type: ignore
