# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import time
from typing import Dict
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToExport, AssetPackage

class ExportedPackageLog():
    # [PackageName, PackageType, ExportPath, ExportTime]

    def __init__(self):
        self.export_start_time = 0.0
        self.export_end_time = 0.0
        self.export_success = False

    def start_package_export(self):
        self.export_start_time = time.perf_counter()

    def end_package_export(self, success: bool):
        self.export_end_time = time.perf_counter()
        self.export_success = success

    def get_package_export_time(self):
        return self.export_end_time - self.export_start_time

class ExportedAssetLog():
    # [AssetName , AssetType , ExportPath, ExportTime]

    def __init__(self, exported_asset: AssetToExport):
        self.exported_asset = exported_asset
        self.package_logs: Dict[str, ExportedPackageLog] = {}

    def start_asset_export(self):
        self.export_start_time = time.perf_counter()

    def end_asset_export(self, success: bool):
        self.export_end_time = time.perf_counter()
        self.export_success = success

    def get_asset_export_time(self):
        return self.export_end_time - self.export_start_time

    def start_package_export(self, package: AssetPackage):
        new_package_log = ExportedPackageLog()
        new_package_log.start_package_export()
        self.package_logs[package.name] = new_package_log

    def end_package_export(self, package: AssetPackage, success: bool):
        if package.name in self.package_logs:
            self.package_logs[package.name].end_package_export(success)
        else:
            raise KeyError(f"Package {package.name} not found in logs for asset {self.exported_asset.name}.")
        
    def get_package_export_time(self, package: AssetPackage):
        if package.name in self.package_logs:
            return self.package_logs[package.name].get_package_export_time()
        else:
            raise KeyError(f"Package {package.name} not found in logs for asset {self.exported_asset.name}.")
        
    def get_package_export_success(self, package: AssetPackage):
        if package.name in self.package_logs:
            return self.package_logs[package.name].export_success
        else:
            raise KeyError(f"Package {package.name} not found in logs for asset {self.exported_asset.name}.")






classes = (
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)  # type: ignore



def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)  # type: ignore
