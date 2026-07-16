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
    EXPORT_SELF_ONLY = "export_self_only" # Export self object only
    DONT_EXPORT = "dont_export" # Will never export


    # Direct type check functions
    def is_auto(self) -> bool:
        return self.value == BFU_ExportTypeEnum.AUTO.value

    def is_export_recursive(self) -> bool:
        return self.value == BFU_ExportTypeEnum.EXPORT_RECURSIVE.value
    
    def is_export_self_only(self) -> bool:
        return self.value == BFU_ExportTypeEnum.EXPORT_SELF_ONLY.value
    
    def is_dont_export(self) -> bool:
        return self.value == BFU_ExportTypeEnum.DONT_EXPORT.value
    
    # Type check functions
    def is_export_self(self) -> bool:
        return self.value in (BFU_ExportTypeEnum.EXPORT_RECURSIVE.value, BFU_ExportTypeEnum.EXPORT_SELF_ONLY.value)
    

    @staticmethod
    def default() -> "BFU_ExportTypeEnum":
        return BFU_ExportTypeEnum.AUTO

