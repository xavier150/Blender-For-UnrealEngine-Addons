# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

def get_icon_by_group_theme(theme_enum: str) -> str:
    """
    Get the icon name based on a group theme enum value.
    """
    if theme_enum == "RED":
        return "COLORSET_01_VEC"
    elif theme_enum == "BLUE":
        return "COLORSET_04_VEC"
    elif theme_enum == "YELLOW":
        return "COLORSET_09_VEC"
    elif theme_enum == "PURPLE":
        return "COLORSET_06_VEC"
    elif theme_enum == "GREEN":
        return "COLORSET_03_VEC"
    return "NONE"
