# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from enum import Enum

class BFU_FileTypeEnum(Enum):
    # List of file types supported by the addon at export.
    FBX = "FBX"
    GLTF = "GLTF"
    ALEMBIC = "Alembic"
    JSON = "JSON"
    UNKNOWN = "Unknown"

    def get_file_extension(self) -> str:
        if self == BFU_FileTypeEnum.FBX:
            return ".fbx"
        elif self == BFU_FileTypeEnum.GLTF:
            return ".glb"
        elif self == BFU_FileTypeEnum.ALEMBIC:
            return ".abc"
        elif self == BFU_FileTypeEnum.JSON:
            return ".json"
        return ".unknown"