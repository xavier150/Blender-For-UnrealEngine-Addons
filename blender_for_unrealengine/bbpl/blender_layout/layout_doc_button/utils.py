# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

from ... import __internal__

def get_open_target_web_page_idname():
    return __internal__.utils.get_object_operator_idname("open_target_web_page")  # type: ignore

def get_open_target_web_page_class_name():
    return __internal__.utils.get_operator_class_name("OpenTargetWebPage")  # type: ignore
