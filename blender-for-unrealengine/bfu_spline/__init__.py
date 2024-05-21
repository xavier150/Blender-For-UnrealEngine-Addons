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

from . import bfu_spline_utils
from . import bfu_spline_unreal_utils
from . import bfu_spline_data
from . import bfu_spline_export_utils
from . import bfu_spline_write_text
from . import bfu_spline_write_paste_commands
from . import bfu_spline_ui_and_props
from . import bfu_spline_type
from . import bfu_spline_config

if "bfu_spline_utils" in locals():
    importlib.reload(bfu_spline_utils)
if "bfu_spline_unreal_utils" in locals():
    importlib.reload(bfu_spline_unreal_utils)
if "bfu_spline_data" in locals():
    importlib.reload(bfu_spline_data)
if "bfu_spline_export_utils" in locals():
    importlib.reload(bfu_spline_export_utils)
if "bfu_spline_write_text" in locals():
    importlib.reload(bfu_spline_write_text)
if "bfu_spline_write_paste_commands" in locals():
    importlib.reload(bfu_spline_write_paste_commands)
if "bfu_spline_ui_and_props" in locals():
    importlib.reload(bfu_spline_ui_and_props)
if "bfu_spline_type" in locals():
    importlib.reload(bfu_spline_type)
if "bfu_spline_config" in locals():
    importlib.reload(bfu_spline_config)

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_spline_ui_and_props.register()
    bfu_spline_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_spline_type.unregister()
    bfu_spline_ui_and_props.unregister()