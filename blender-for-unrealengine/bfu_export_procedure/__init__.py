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

from . import bfu_skeleton_export_procedure
from . import bfu_static_export_procedure
from . import bfu_alembic_export_procedure
from . import bfu_groom_export_procedure
from . import bfu_camera_export_procedure
from . import bfu_collection_export_procedure
from . import bfu_export_procedure_ui


if "bfu_skeleton_export_procedure" in locals():
    importlib.reload(bfu_skeleton_export_procedure)
if "bfu_static_export_procedure" in locals():
    importlib.reload(bfu_static_export_procedure)
if "bfu_alembic_export_procedure" in locals():
    importlib.reload(bfu_alembic_export_procedure)
if "bfu_groom_export_procedure" in locals():
    importlib.reload(bfu_groom_export_procedure)
if "bfu_camera_export_procedure" in locals():
    importlib.reload(bfu_camera_export_procedure)
if "bfu_collection_export_procedure" in locals():
    importlib.reload(bfu_collection_export_procedure)
if "bfu_export_procedure_ui" in locals():
    importlib.reload(bfu_export_procedure_ui)


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_skeleton_export_procedure.register()
    bfu_static_export_procedure.register()
    bfu_alembic_export_procedure.register()
    bfu_groom_export_procedure.register()
    bfu_camera_export_procedure.register()
    bfu_collection_export_procedure.register()
    bfu_export_procedure_ui.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_export_procedure_ui.unregister()
    bfu_collection_export_procedure.unregister()
    bfu_camera_export_procedure.unregister()
    bfu_groom_export_procedure.unregister()
    bfu_alembic_export_procedure.register()
    bfu_static_export_procedure.unregister()
    bfu_skeleton_export_procedure.unregister()