# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

# Public entry points of the template list. Implementation lives in:
#   item_types.py      -> base item PropertyGroup and base UIList drawer
#   category_types.py  -> categories overlay (expanded states, display rows, selection sync)
#   list_types.py      -> the template list PropertyGroup and its draw()
#   operators.py       -> add / remove / move / duplicate buttons

from . import item_types
from . import list_types
from . import category_types
from . import operators

create_template_item_class = item_types.create_template_item_class
create_template_item_draw_class = item_types.create_template_item_draw_class
create_template_list_class = list_types.create_template_list_class

# ----------------- Register ----------------

def register():
    category_types.register()
    operators.register()


def unregister():
    operators.unregister()
    category_types.unregister()
