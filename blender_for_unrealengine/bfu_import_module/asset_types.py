# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

# Export asset types from Blender
from enum import Enum

class ExportAssetType(Enum):
    UNKNOWN = "Unknown" # Unknown asset type.
    SKELETAL_MESH = "SkeletalMesh"
    STATIC_MESH = "StaticMesh"
    COLLECTION_AS_STATIC_MESH = "Collection StaticMesh"
    CAMERA = "Camera"
    GROOM_SIMULATION = "GroomSimulation" # Groom simulation.
    SPLINE = "Spline" # Curve and spline objects.
    ANIM_ACTION = "Action" 
    ANIM_POSE = "Pose" # Action but only one frame.
    ANIM_NLA = "NonLinearAnimation" # Non linear animations.
    ANIM_ALEMBIC = "AlembicAnimation" # Alembic animations.

    def get_friendly_name(self):
        if self.value == ExportAssetType.UNKNOWN.value:
            return "Unknown Asset Type"
        elif self.value == ExportAssetType.SKELETAL_MESH.value:
            return "Skeletal Mesh"
        elif self.value == ExportAssetType.STATIC_MESH.value:
            return "Static Mesh"
        elif self.value == ExportAssetType.COLLECTION_AS_STATIC_MESH.value:
            return "Collection Static Mesh"
        elif self.value == ExportAssetType.CAMERA.value:
            return "Camera"
        elif self.value == ExportAssetType.GROOM_SIMULATION.value:
            return "Groom Simulation"
        elif self.value == ExportAssetType.SPLINE.value:
            return "Spline"
        elif self.value == ExportAssetType.ANIM_ACTION.value:
            return "Action Animation"
        elif self.value == ExportAssetType.ANIM_POSE.value:
            return "Pose Animation"
        elif self.value == ExportAssetType.ANIM_NLA.value:
            return "Non Linear Animation"
        elif self.value == ExportAssetType.ANIM_ALEMBIC.value:
            return "Alembic Animation"
        else:
            return "Unknown"    
        
    def get_type_as_string(self):
        if self.value == ExportAssetType.UNKNOWN.value:
            return "Unknown"
        elif self.value == ExportAssetType.SKELETAL_MESH.value:
            return "SkeletalMesh"
        elif self.value == ExportAssetType.STATIC_MESH.value:
            return "StaticMesh"
        elif self.value == ExportAssetType.COLLECTION_AS_STATIC_MESH.value:
            return "CollectionStaticMesh"
        elif self.value == ExportAssetType.CAMERA.value:
            return "Camera"
        elif self.value == ExportAssetType.GROOM_SIMULATION.value:
            return "GroomSimulation"
        elif self.value == ExportAssetType.SPLINE.value:
            return "Spline"
        elif self.value == ExportAssetType.ANIM_ACTION.value:
            return "Action"
        elif self.value == ExportAssetType.ANIM_POSE.value:
            return "Pose"
        elif self.value == ExportAssetType.ANIM_NLA.value:
            return "NonLinearAnimation"
        elif self.value == ExportAssetType.ANIM_ALEMBIC.value:
            return "AlembicAnimation"
        else:
            return "Unknown"
    
    @staticmethod
    def get_asset_type_from_string(asset_type_str: str) -> 'ExportAssetType':
        for asset_type in ExportAssetType:
            if asset_type.value == asset_type_str:
                return asset_type
        return ExportAssetType.UNKNOWN
    
    def is_skeletal(self) -> bool:
        return self.value in [
            ExportAssetType.SKELETAL_MESH.value, 
            ExportAssetType.ANIM_ACTION.value, 
            ExportAssetType.ANIM_POSE.value, 
            ExportAssetType.ANIM_NLA.value
        ]
    
    def is_skeletal_animation(self) -> bool:
        return self.value in [
            ExportAssetType.ANIM_ACTION.value, 
            ExportAssetType.ANIM_POSE.value, 
            ExportAssetType.ANIM_NLA.value
        ]
    
class AssetFileTypeEnum(Enum):
    # List of file types supported by the addon at export.
    FBX = "FBX"
    GLTF = "GLTF"
    ALEMBIC = "Alembic"
    JSON = "JSON"
    UNKNOWN = "Unknown"

    @staticmethod
    def get_file_type_from_string(file_type_str: str) -> 'AssetFileTypeEnum':
        for file_type in AssetFileTypeEnum:
            if file_type.value == file_type_str:
                return file_type
        return AssetFileTypeEnum.UNKNOWN

    def get_file_extension(self) -> str:
        if self == AssetFileTypeEnum.FBX:
            return ".fbx"
        elif self == AssetFileTypeEnum.GLTF:
            return ".glb"
        elif self == AssetFileTypeEnum.ALEMBIC:
            return ".abc"
        elif self == AssetFileTypeEnum.JSON:
            return ".json"
        return ".unknown"