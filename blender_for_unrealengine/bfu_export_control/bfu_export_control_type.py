# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from enum import Enum


class BFU_ExportTypeEnum(Enum):
    AUTO = "auto"
    EXPORT_RECURSIVE = "export_recursive"
    DONT_EXPORT = "dont_export"

    @staticmethod
    def default() -> "BFU_ExportTypeEnum":
        return BFU_ExportTypeEnum.AUTO

