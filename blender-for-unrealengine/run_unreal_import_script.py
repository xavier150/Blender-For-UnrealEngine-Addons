# This script should be run in Unreal Engine to import assets into Unreal Engine 4 and 5.
# The assets are exported from the Unreal Engine Assets Exporter. More details can be found here: https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# Use the following command in Unreal cmd console and follow the instructions: 
# py "[ScriptLocation]\run_unreal_import_script.py" -h 
# py "M:\MMVS_ProjectFiles\content\Level\TalasCozyHouse\ExportedFbx\ImportAssetScript.py" -h

import os
import sys
import importlib.util
import argparse
import json

def json_load(json_file):
    # In Python 3.9: The keyword argument encoding has been removed.
    if sys.version_info >= (3, 9):
        return json.load(json_file)
    else:
        return json.load(json_file, encoding="utf8")

def json_load_file(json_file_path):
    # In Python 3.9: The keyword argument encoding has been removed.
    if sys.version_info[0] < 3:
        with open(json_file_path, "r") as json_file:
            return json_load(json_file)
    else:
        with open(json_file_path, "r", encoding="utf8") as json_file:
            return json_load(json_file)

def import_unreal_module():
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    module_name = "bfu_import_module"
    module_file = os.path.join(script_dir, module_name, "__init__.py")

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def clear_unreal_module():
    module_name = "bfu_import_module"
    del sys.modules[module_name]

def run_from_asset_import_script(import_data_filepath):
    module = import_unreal_module()
    try:
        module.run_asset_import(json_load_file(import_data_filepath))
    except Exception as e:
        print(f"An error has occurred: {e}")
    clear_unreal_module()

def run_from_sequencer_import_script(import_data_filepath):
    module = import_unreal_module()
    try:
        module.run_sequencer_import(json_load_file(import_data_filepath))
    except Exception as e:
        print(f"An error has occurred: {e}")
    clear_unreal_module()

def run_from_arguments():
    args_valid = False
    parser = argparse.ArgumentParser(description='Process Unreal Engine asset or sequencer import.')
    parser.add_argument('--type', type=str, required=True, help='Content type to import in Unreal Engine. (required)')
    parser.add_argument('--data_filepath', type=str, required=True, help='JSON filename with data to import. (required)')
    parser.add_argument('--show_finished_popup', action='store_true', help='Show a popup when finished. (optional)')

    try:
        args = parser.parse_args()
        args_valid = True
    except argparse.ArgumentError as e:
        print(f"Argument error: {e}")
    except SystemExit as e:
        print("Error: Required arguments are missing. Use -h in arguments for help.")

    if(args_valid):
        import_type = args.type
        import_data_filepath = args.data_filepath
        show_finished_popup = args.show_finished_popup

        if import_type == "assets":
            asset_data = json_load_file(import_data_filepath)
            module = import_unreal_module()
            try:
                module.run_asset_import(asset_data, show_finished_popup)
            except Exception as e:
                print(f"An error has occurred: {e}")
            clear_unreal_module()
        elif import_type == "sequencer":
            asset_data = json_load_file(import_data_filepath)
            module = import_unreal_module()
            try:
                module.run_sequencer_import(asset_data, show_finished_popup)
            except Exception as e:
                print(f"An error has occurred: {e}")
            clear_unreal_module()
        else:
            print("Error: --type must be 'assets' or 'sequencer'")

if __name__ == "__main__":
    run_from_arguments()
