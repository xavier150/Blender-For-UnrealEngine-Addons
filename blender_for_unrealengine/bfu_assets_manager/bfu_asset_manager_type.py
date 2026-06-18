# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from enum import Enum
import pathlib
from typing import List, Optional, Tuple, Callable, Any, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod
from pathlib import Path
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_basics
from .. import bfu_base_collection
from .. import bfu_addon_prefs
from .. import bfu_base_object

class AssetToSearch(Enum):
    ALL_ASSETS = "all_assets"  # Search for all assets.
    ANIMATION_ONLY = "animation_only"  # Search only for animation assets.
    COLLECTION_ONLY = "collection_only"  # Search only for scene collection assets.

    def get_friendly_name(self) -> str:
        if self.value == AssetToSearch.ALL_ASSETS.value:
            return "All Assets"
        elif self.value == AssetToSearch.ANIMATION_ONLY.value:
            return "Animation Only"
        elif self.value == AssetToSearch.COLLECTION_ONLY.value:
            return "Collection Only"
        else:
            return "Unknown"
        
    def get_asset_title_text(self, asset_count: int) -> str:
        if self.value == AssetToSearch.ALL_ASSETS.value:
            if asset_count == 0:
                return "No exportable assets were found."
            elif asset_count == 1:
                return "1 asset will be exported."
            else:
                return f"{asset_count} assets will be exported."
        elif self.value == AssetToSearch.ANIMATION_ONLY.value:
            if asset_count == 0:
                return "No exportable animations were found."
            elif asset_count == 1:
                return "1 animation will be exported."
            else:
                return f"{asset_count} animations will be exported."
        elif self.value == AssetToSearch.COLLECTION_ONLY.value:
            if asset_count == 0:
                return "No exportable collections were found."
            elif asset_count == 1:
                return "1 collection will be exported."
            else:
                return f"{asset_count} collections will be exported."
        else:
            return "Unknown asset type."

class AssetDataSearchMode(Enum):
    FULL = "Full" # Search for all assets data.
    PREVIEW = "Preview" # Search assets data for user interface preview.
    ASSET_NUMBER = "AssetNumber" # Search for asset number.
    
    def search_packages(self):
        if self.value == AssetDataSearchMode.FULL.value:
            return True
        elif self.value == AssetDataSearchMode.PREVIEW.value:
            return True
        elif self.value == AssetDataSearchMode.ASSET_NUMBER.value:
            return False
        else:
            return False
        
    def search_package_content(self):
        if self.value == AssetDataSearchMode.FULL.value:
            return True
        elif self.value == AssetDataSearchMode.PREVIEW.value:
            return False
        elif self.value == AssetDataSearchMode.ASSET_NUMBER.value:
            return False
        else:
            return False

class AssetType(Enum):
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
        if self.value == AssetType.UNKNOWN.value:
            return "Unknown Asset Type"
        elif self.value == AssetType.SKELETAL_MESH.value:
            return "Skeletal Mesh"
        elif self.value == AssetType.STATIC_MESH.value:
            return "Static Mesh"
        elif self.value == AssetType.COLLECTION_AS_STATIC_MESH.value:
            return "Collection Static Mesh"
        elif self.value == AssetType.CAMERA.value:
            return "Camera"
        elif self.value == AssetType.GROOM_SIMULATION.value:
            return "Groom Simulation"
        elif self.value == AssetType.SPLINE.value:
            return "Spline"
        elif self.value == AssetType.ANIM_ACTION.value:
            return "Action Animation"
        elif self.value == AssetType.ANIM_POSE.value:
            return "Pose Animation"
        elif self.value == AssetType.ANIM_NLA.value:
            return "Non Linear Animation"
        elif self.value == AssetType.ANIM_ALEMBIC.value:
            return "Alembic Animation"
        else:
            return "Unknown"    
        
    def get_type_as_string(self):
        if self.value == AssetType.UNKNOWN.value:
            return "Unknown"
        elif self.value == AssetType.SKELETAL_MESH.value:
            return "SkeletalMesh"
        elif self.value == AssetType.STATIC_MESH.value:
            return "StaticMesh"
        elif self.value == AssetType.COLLECTION_AS_STATIC_MESH.value:
            return "CollectionStaticMesh"
        elif self.value == AssetType.CAMERA.value:
            return "Camera"
        elif self.value == AssetType.GROOM_SIMULATION.value:
            return "GroomSimulation"
        elif self.value == AssetType.SPLINE.value:
            return "Spline"
        elif self.value == AssetType.ANIM_ACTION.value:
            return "Action"
        elif self.value == AssetType.ANIM_POSE.value:
            return "Pose"
        elif self.value == AssetType.ANIM_NLA.value:
            return "NonLinearAnimation"
        elif self.value == AssetType.ANIM_ALEMBIC.value:
            return "AlembicAnimation"
        else:
            return "Unknown"

    

    def can_use_frame_range(self) -> bool:
        return self in [
            AssetType.ANIM_ACTION,
            AssetType.ANIM_POSE,
            AssetType.ANIM_NLA,
            AssetType.ANIM_ALEMBIC,
            AssetType.CAMERA
        ]
    
    def can_contain_objects(self) -> bool:
        return self in [
            AssetType.SKELETAL_MESH,
            AssetType.STATIC_MESH,
            AssetType.COLLECTION_AS_STATIC_MESH,
        ]

    def is_skeletal(self) -> bool:
        return self in [
            AssetType.SKELETAL_MESH, 
            AssetType.ANIM_ACTION, 
            AssetType.ANIM_POSE, 
            AssetType.ANIM_NLA
        ]
    
    def is_skeletal_animation(self) -> bool:
        return self in [
            AssetType.ANIM_ACTION, 
            AssetType.ANIM_POSE, 
            AssetType.ANIM_NLA
        ]

class PackageFile:
    def __init__(self, dirpath: Path, filename: str, file_type: BFU_FileTypeEnum = BFU_FileTypeEnum.UNKNOWN):
        self.dirpath: Path = dirpath
        self.filename: str = filename
        self.file_type: BFU_FileTypeEnum = file_type  # Type of the file, e.g., FBX, GLTF, etc.
        self.file_content_type: str = "" # Content type, LOD, MATERIAL, etc.

    def get_full_path(self) -> Path:
        # Return the full path of the package file
        return pathlib.Path(self.dirpath) / self.filename
    
    def get_file_as_data(self) -> Dict[str, Any]:
        # Get the file as data, useful for exporting to JSON or other formats
        file_data: Dict[str, Any] = {}
        file_data["type"] = self.file_type.value
        file_data["content_type"] = self.file_content_type
        file_data["file_path"] = str(self.get_full_path())
        return file_data

class AssetPackage:
    def __init__(self, name: str, details: Optional[List[str]] = None):
        self.name: str = name
        self.details: Optional[List[str]] = details
        self.file: Optional[PackageFile] = None
        self.objects: List[bpy.types.Object] = []
        self.collection: Optional[bpy.types.Collection] = None
        self.action: Optional[bpy.types.Action] = None  # Action for animations
        self.export_function: Optional[Callable[..., Any]] = None
        self.frame_range: Optional[Tuple[float, float]] = None  # Frame range for animations, e.g., (start, end)

    def set_file(self, dirpath: Path, filename: str, file_type: BFU_FileTypeEnum) -> PackageFile:
        # Set the package file with the given directory path and filename
        self.file = PackageFile(dirpath, filename, file_type)
        return self.file

    def check_object_in_scene(self, obj: bpy.types.Object) -> bool:
        # Check if the object is valid in the current scene
        scene = bpy.context.scene
        if not scene:
            raise ValueError("No active scene found in the current context.")
        
        if not obj.name in scene.objects:
            raise ValueError(f"Object {obj.name} not found in the current scene.")
        
        scene_obj = scene.objects[obj.name]
        if scene_obj != obj:
            error_text = (f"Object {obj.name} is not valid in the current scene. " + 
            "if the object comes from a library, you need get scene reference created at the link.")  
            raise ValueError(error_text)
        return True
    
    def check_objects_in_scene(self, objects: List[bpy.types.Object]) -> bool:
        # Check if all objects are valid in the current scene
        for obj in objects:
            self.check_object_in_scene(obj)
        return True

    def add_object(self, obj: bpy.types.Object) -> None:
        # Add an object to the package
        self.check_object_in_scene(obj)
        self.objects.append(obj)

    def add_objects(self, objects: List[bpy.types.Object]) -> None:
        # Add multiple objects to the package
        self.check_objects_in_scene(objects)
        self.objects.extend(objects)

    def set_collection(self, collection: bpy.types.Collection) -> None:
        # Set the collection for the package
        self.collection = collection

    def set_action(self, action: bpy.types.Action) -> None:
        # Set the action for the package
        self.action = action

    def set_frame_range(self, start: float, end: float) -> None:
        # Set the frame range for animations
        self.frame_range = (start, end)

class AdditionalAssetData:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data
        self.file: Optional[PackageFile] = None

    def set_file(self, dirpath: Path, filename: str) -> PackageFile:
        # Set the additional data file with the given directory path and filename
        self.file = PackageFile(dirpath, filename)
        self.file.file_type = BFU_FileTypeEnum.JSON
        self.file.file_content_type = "ADDITIONAL_DATA"
        return self.file

class AssetToExport:
    def __init__(
        self,
        asset_class: "BFU_BaseAssetClass",
        asset_name: str,
        asset_type: AssetType
    ):
        # Base info
        self.name: str = asset_name
        self.asset_type: AssetType = asset_type
        self.import_name: str = ""
        self.import_dirpath: Path = Path()
        self.original_asset_class: BFU_BaseAssetClass = asset_class

        # Asset Pakages
        self.asset_packages: List[AssetPackage] = []

        # Asset Additional Data:
        self.additional_data: Optional[AdditionalAssetData] = None

    def get_asset_files_as_data(self) -> List[Dict[str, Any]]:
        # Get the asset files as data, useful for exporting to JSON or other formats
        files_data: List[Dict[str, Any]] = []
        
        for package in self.asset_packages:
            if package.file:
                files_data.append(package.file.get_file_as_data())
        
        if self.additional_data and self.additional_data.file:
            files_data.append(self.additional_data.file.get_file_as_data())
        
        return files_data

    def add_asset_package(self, package_name: str, details: Optional[List[str]] = None) -> AssetPackage:
        # Create a new asset package and add it to the list
        new_package = AssetPackage(package_name, details)
        self.asset_packages.append(new_package)
        return new_package

    def set_asset_additional_data(self, data: Dict[str, Any]) -> AdditionalAssetData:
        # Set the additional data for the asset
        self.additional_data = AdditionalAssetData(data)
        return self.additional_data
    
    def get_primary_asset_package(self) -> Optional[bpy.types.Object]:
        # Get the primary asset package, which is the first one in the list
        if self.asset_packages:
            if len(self.asset_packages) > 0:
                if len(self.asset_packages[0].objects) > 0:
                    return self.asset_packages[0].objects[0]
        return None

    def set_import_name(self, new_import_name: str) -> None:
        self.import_name = new_import_name

    def set_import_dirpath(self, new_import_dirpath: Path) -> None:
        self.import_dirpath = new_import_dirpath

# ###################################################################

class BFU_BaseAssetClass(ABC):
    def __init__(self):
        self.use_lods = False
        self.use_materials = False
        self.use_sockets = False

        self.asset_folder_name: str = ""  # Sub folder name. Can be empty. You can also overide get_asset_folder_path() to provide a custom path.

# ###################################################################
# # Asset Root Class
# ###################################################################

    @abstractmethod
    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        # Used to detect if the data is supported by this asset type.
        return False

    @abstractmethod
    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.UNKNOWN

    @abstractmethod
    def can_export_asset_type(self) -> bool:
        # Can export the asset for this asset type.
        # Used with scene filters. Export Static Meshes ? Export Skeletal Meshes ? etc.
        return False

    def can_export_asset(self, data: Any) -> bool:
        # Can export this specific asset (data)
        # By default True if the asset type can be exported.
        if not self.can_export_asset_type(): # First type the type before checking the data.
            return False

        return True

    @abstractmethod
    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        return Path()

# ###################################################################
# # Asset Package Management
# ###################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        # Prefix for the package file. Can be empty.
        # Get the package file prefix, used for naming the package files.
        return ""
    
    def get_package_file_suffix(self, data: Any, details: Any = None) -> str:
        # Get the package file suffix, used for naming the package files.
        # Suffix for the package file. Can be empty.
        return ""

    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        # Get the export file path
        return ""
    
# ---------------------------------------------------

    @abstractmethod
    def get_package_file_type(self, data: Any, details: Any = None) -> BFU_FileTypeEnum:
        return BFU_FileTypeEnum.UNKNOWN

    @abstractmethod
    def get_package_file_name(self, data: Any, details: Any = None, desired_name: str = "", without_extension: bool = False) -> str:
        return "<Unknown>"

    def get_asset_folder_path(self, data: Any, details: Any = None) -> Path:
        # Add asset folder path if provided
        if self.asset_folder_name:
            return Path(self.asset_folder_name)
        return Path()

    def get_package_export_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None, absolute: bool = True) -> Path:
        # Asset root Path
        export_file_path = self.get_export_file_path(data, details)
        if absolute:
            dirpath = Path(bpy.path.abspath(export_file_path)).resolve()  # type: ignore
        else:
            dirpath = Path(export_file_path)
        
        # Add subfolder path if provided         
        asset_folder_name = self.get_asset_folder_path(data, details)
        if asset_folder_name:
            dirpath /= asset_folder_name

        # Add extra path if provided
        if extra_path:
            dirpath /= extra_path

        return dirpath

# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: Any) -> bpy.types.UILayout:
        # If object supports export procedure, draw the UI for it
        return layout
    
# ####################################################################
# # Asset Construction
# ####################################################################

    def set_package_file(self, package: AssetPackage, data: Any, details: Any) -> None:
        dirpath = self.get_package_export_directory_path(data, details, absolute=True)
        file_name = self.get_package_file_name(data, details)
        file_type = self.get_package_file_type(data, details)
        package.set_file(dirpath, file_name, file_type)

    def set_additional_data_file(self, additional_data: AdditionalAssetData, data: Any, details: Any) -> None:
        dirpath = self.get_package_export_directory_path(data, details, absolute=True)
        file_name = self.get_package_file_name(data, details, without_extension=True) + "_additional_data.json"
        additional_data.set_file(dirpath, file_name)

    def set_additional_data_in_asset(self, asset_to_export: AssetToExport, data: Any, details: Any, search_mode: AssetDataSearchMode) -> None:
        if search_mode.search_packages():
            scene = bpy.context.scene
            if scene:
                addon_prefs = bfu_addon_prefs.get_addon_preferences()
                if (scene.bfu_use_text_additional_data and addon_prefs.useGeneratedScripts):  # type: ignore[attr-defined]

                    # Set additional data for the asset to export.
                    additional_data_data = self.get_asset_additional_data(data, details, search_mode)
                    additional_data = asset_to_export.set_asset_additional_data(additional_data_data)
                    if additional_data:
                        self.set_additional_data_file(additional_data, data, details)

    @abstractmethod
    def get_asset_export_data(self, data: Any, details: Any, search_mode: AssetDataSearchMode) -> List[AssetToExport]:
        # Direct access asset export data. without checking can_export_asset()
        # Include data from additional data.
        return []
    
    def get_asset_additional_data(self, data: Any, details: Any, search_mode: AssetDataSearchMode) -> Dict[str, Any]:
        return {}
    
    def get_batch_asset_export_data(self, search_mode: AssetDataSearchMode, force_cache_update: bool = False) -> List[AssetToExport]:
        return []
    
class BFU_ObjectAssetClass(BFU_BaseAssetClass):

    def __init__(self):
        super().__init__()

    def get_package_file_name(self, data: bpy.types.Object, details: Any = None, desired_name: str = "", without_extension: bool = False) -> str:

        # Use custom export name if set
        if TYPE_CHECKING:
            class FakeObject(bpy.types.Object): 
                bfu_use_custom_export_name: str = ""
                bfu_custom_export_name: str = ""
            data = FakeObject()
        

        if data.bfu_use_custom_export_name and data.bfu_custom_export_name:
            if without_extension:
                return bfu_basics.valid_file_name(data.bfu_custom_export_name)
            else:
                return bfu_basics.valid_file_name(data.bfu_custom_export_name + self.get_package_file_type(data).get_file_extension())

        # Use desired name if provided and add prefix and suffix
        base_name = desired_name if desired_name else data.name
        file_prefix = self.get_package_file_prefix(data, details)
        file_suffix = self.get_package_file_suffix(data, details)
        base_name = file_prefix + base_name + file_suffix

        # Validate the base name and add file extension if needed
        if without_extension:
            return bfu_basics.valid_file_name(base_name)
        else:
            file_extension = self.get_package_file_type(data).get_file_extension()
            return bfu_basics.valid_file_name(base_name + file_extension)
        
    def get_asset_folder_path(self, data: bpy.types.Object, details: Any = None) -> Path:
        # Add object folder path
        obj_folder_path = bfu_base_object.bfu_base_obj_utils.get_obj_export_folder(data)
        if obj_folder_path:
            return Path(obj_folder_path)
        return Path()

class BFU_CollectionAssetClass(BFU_BaseAssetClass):
    
    def __init__(self):
        super().__init__()

    def get_package_file_name(self, data: bpy.types.Collection, details: Any = None, desired_name: str = "", without_extension: bool = False) -> str:

        # Use desired name if provided and add prefix and suffix
        base_name = desired_name if desired_name else data.name
        file_prefix = self.get_package_file_prefix(data, details)
        file_suffix = self.get_package_file_suffix(data, details)
        base_name = file_prefix + base_name + file_suffix


        # Validate the base name and add file extension if needed
        if without_extension:
            return bfu_basics.valid_file_name(base_name)
        else:
            file_extension = self.get_package_file_type(data).get_file_extension()
            return bfu_basics.valid_file_name(base_name + file_extension)
        
    def get_asset_folder_path(self, data: bpy.types.Collection, details: Any = None) -> Path:
        # Add collection folder path
        col_folder_path = bfu_base_collection.bfu_base_col_utils.get_col_export_folder(data)
        if col_folder_path:
            return Path(col_folder_path)
        return Path()

