# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import importlib

from . import bfu_export_procedure
from . import bfu_alembic_animation_props
from . import bfu_alembic_animation_ui
from . import bfu_alembic_animation_utils
from . import bfu_alembic_animation_type
from . import bfu_alembic_animation_config
from . import bfu_export_alembic_package

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)
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
if "bfu_export_alembic_package" in locals():
    importlib.reload(bfu_export_alembic_package)    



classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_export_procedure.register()
    bfu_alembic_animation_props.register()
    bfu_alembic_animation_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_alembic_animation_type.unregister()
    bfu_alembic_animation_props.unregister()
    bfu_export_procedure.unregister()