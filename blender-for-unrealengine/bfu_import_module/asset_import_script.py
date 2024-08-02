# This script was generated with the addons Unreal Engine Assets Exporter.
# This script should be run in Unreal Engine to import into Unreal Engine 4 and 5 assets.
# The assets are exported from from Unreal Engine Assets Exporter. More detail here. https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# Use the following command in Unreal Engine cmd consol to import assets: 
# py "[ScriptLocation]\asset_import_script.py"

import importlib
import importlib.util
import sys
import os
import json

def JsonLoad(json_file):
    # Changed in Python 3.9: The keyword argument encoding has been removed.
    if sys.version_info >= (3, 9):
        return json.load(json_file)
    else:
        return json.load(json_file, encoding="utf8")

def JsonLoadFile(json_file_path):
    if sys.version_info[0] < 3:
        with open(json_file_path, "r") as json_file:
            return JsonLoad(json_file)
    else:
        with open(json_file_path, "r", encoding="utf8") as json_file:
            return JsonLoad(json_file)

def RunImportScriptWithJsonData():
    # Prepare process import
    json_data_file = 'ImportAssetData.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    import_file_path = os.path.join(dir_path, json_data_file)
    assets_data = JsonLoadFile(import_file_path)
    
    file_path = os.path.join(assets_data["info"]["addon_path"],'run_unreal_import_script.py')
    spec = importlib.util.spec_from_file_location("__import_assets__", file_path)
    module = importlib.util.module_from_spec(spec)

    # Run script module function
    spec.loader.exec_module(module)
    module.run_from_asset_import_script(import_file_path)

if __name__ == "__main__":
    RunImportScriptWithJsonData()

