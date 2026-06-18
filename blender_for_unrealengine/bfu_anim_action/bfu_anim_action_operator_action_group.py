# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import TYPE_CHECKING
import bpy

class BFU_OT_ObjExportAction(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Action data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'}) # type: ignore
    use: bpy.props.BoolProperty(name="use this action", default=False, override={'LIBRARY_OVERRIDABLE'}) # type: ignore

    if TYPE_CHECKING:
        name: str
        use: bool

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ObjExportAction,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

