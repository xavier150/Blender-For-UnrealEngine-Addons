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
import importlib

from . import bfu_alembic_animation_props
from . import bfu_alembic_animation_ui
from . import bfu_alembic_animation_utils
from . import bfu_alembic_animation_type
from . import bfu_alembic_animation_config

if "bfu_alembic_animation_props" in locals():
    importlib.reload(bfu_alembic_animation_props)
if "bfu_alembic_animation_ui" in locals():
    importlib.reload(bfu_alembic_animation_ui)
if "bfu_alembic_animation_utils" in locals():
    importlib.reload(bfu_alembic_animation_utils)
if "bfu_alembic_animation_type" in locals():
    importlib.reload(bfu_alembic_animation_type)
if "bfu_alembic_animation_config" in locals():
    importlib.reload(bfu_alembic_animation_config)



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_alembic_animation_props.register()
    bfu_alembic_animation_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_alembic_animation_type.unregister()
    bfu_alembic_animation_props.unregister()