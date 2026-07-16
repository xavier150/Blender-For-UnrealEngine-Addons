# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from enum import Enum


class BFU_ExportTypeEnum(Enum):
    AUTO = "auto" # Export only if a parent is set to "Export recursive"
    EXPORT_RECURSIVE = "export_recursive" # Export self object and all children
    EXPORT_SELF = "export_self" # Export self object only
    DONT_EXPORT = "dont_export" # Will never export

    def is_export_self(self) -> bool:
        return self.value in (BFU_ExportTypeEnum.EXPORT_RECURSIVE.value, BFU_ExportTypeEnum.EXPORT_SELF.value)
    
    def is_export_recursive(self) -> bool:
        return self.value == BFU_ExportTypeEnum.EXPORT_RECURSIVE.value

    @staticmethod
    def default() -> "BFU_ExportTypeEnum":
        return BFU_ExportTypeEnum.AUTO

