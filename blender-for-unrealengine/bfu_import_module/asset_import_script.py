# This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose
# The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python
# Use this command in Unreal cmd consol: py "[ScriptLocation]\asset_import_script.py"

import importlib
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

def load_module(import_module_path):
    # Import and run the module
    module_name = os.path.basename(import_module_path).replace('.py', '')
    module_dir = os.path.dirname(import_module_path)

    if module_dir not in sys.path:
        sys.path.append(module_dir)

    imported_module = importlib.import_module(module_name)
    
    if "bfu_import_module" in locals():
        importlib.reload(imported_module)

    # Assuming the module has a main function to run
    if hasattr(imported_module, 'main'):
        imported_module.main()

    return imported_module, module_name

def unload_module(module_name):
    # Vérifier si le module est dans sys.modules
    if module_name in sys.modules:
        # Récupérer la référence du module
        module = sys.modules[module_name]
        # Supprimer la référence globale
        del sys.modules[module_name]
        del module

def RunImportScriptWithJsonData():
    # Prepare process import
    json_data_file = 'ImportAssetData.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))

    import_assets_data = JsonLoadFile(os.path.join(dir_path, json_data_file))
    
    import_module_path = import_assets_data["info"]["import_modiule_path"]  # Module to run    
    imported_module, module_name = load_module(import_module_path)

    unload_module(module_name)
    imported_module.run_asset_import(import_assets_data)

if __name__ == "__main__":
    RunImportScriptWithJsonData()
