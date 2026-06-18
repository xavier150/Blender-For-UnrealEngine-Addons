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
from . import bfu_groom_props
from . import bfu_groom_ui
from . import bfu_groom_utils
from . import bfu_groom_type
from . import bfu_groom_config
from . import bfu_export_groom_package

if "bfu_export_procedure" in locals():
    importlib.reload(bfu_export_procedure)  
if "bfu_groom_props" in locals():
    importlib.reload(bfu_groom_props)
if "bfu_groom_ui" in locals():
    importlib.reload(bfu_groom_ui)
if "bfu_groom_utils" in locals():
    importlib.reload(bfu_groom_utils)
if "bfu_groom_type" in locals():
    importlib.reload(bfu_groom_type)
if "bfu_groom_config" in locals():
    importlib.reload(bfu_groom_config)
if "bfu_export_groom_package" in locals():
    importlib.reload(bfu_export_groom_package)


classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bfu_export_procedure.register()
    bfu_groom_props.register()
    bfu_groom_type.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bfu_groom_type.unregister()
    bfu_groom_props.unregister()
    bfu_export_procedure.unregister()