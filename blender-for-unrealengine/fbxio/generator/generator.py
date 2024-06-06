import os
import shutil
from . import edit_files
from . import edit_fbx_utils
from . import edit_export_fbx_bin

blender_install_folder = "C:\\Program Files\\Blender Foundation"
io_fbx = "scripts\\addons\\io_scene_fbx"
io_scene_fbx_prefix = "io_scene_fbx_"

export_fbx_files = [
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils.py',
]

export_fbx_files_with_threading = [
    'data_types.py',
    'encode_bin.py',
    'export_fbx_bin.py',
    'fbx_utils_threading.py',
    'fbx_utils.py',
]

# Get the directory of the current script
current_script_directory = os.path.dirname(os.path.abspath(__file__))
# Define the parent directory (one level up from the current script directory)
parent_directory = os.path.dirname(current_script_directory)

class FBXExporterGenerate:
    def __init__(self, version, folder, files):
        self.version = version
        self.folder = folder
        self.files = files

    def get_str_version(self):
        return str(self.version[0])+"_"+str(self.version[1])
    
    def get_folder_str_version(self):
        return str(self.version[0])+"."+str(self.version[1])
        
    def run_generate(self):
        # Create the destination folder in the parent directory
        version_as_module = self.get_str_version()
        dest_folder = os.path.join(parent_directory, io_scene_fbx_prefix+version_as_module)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        new_files = self.copy_export_files(dest_folder)
        new_files.append(self.create_init_file(dest_folder))

        for new_file in new_files:
            edit_files.add_header_to_file(new_file)
            if new_file.endswith('export_fbx_bin.py'):
                edit_export_fbx_bin.update_export_fbx_bin(new_file, self.version)
            if new_file.endswith('fbx_utils.py'):
                edit_fbx_utils.update_fbx_utils(new_file, self.version)
        return version_as_module

    def copy_export_files(self, dest_folder):
        addon_folder = os.path.join(blender_install_folder, self.folder, self.get_folder_str_version(), io_fbx)
        new_files = []
        # Verify if the source folder exists
        if not os.path.exists(addon_folder):
            print(f"Source folder does not exist: {addon_folder}")
            return

        # Copy only specified files from the source to the destination
        for file_name in self.files:
            source_file = os.path.join(addon_folder, file_name)
            destination_file = os.path.join(dest_folder, file_name)
            if os.path.exists(source_file):
                shutil.copy2(source_file, destination_file)
                new_files.append(destination_file)
            else:
                print(f"File does not exist: {source_file}")

        print(f"Copied specified FBX exporter files for Blender {self.version} to {dest_folder}")
        return new_files


    def create_init_file(self, dest_folder):
        files = self.files
        init_file_path = os.path.join(dest_folder, '__init__.py')
        with open(init_file_path, 'w') as init_file:
            # Write imports
            for file_name in files:
                module_name, _ = os.path.splitext(file_name)
                init_file.write(f"from . import {module_name}\n")
            
            init_file.write("\nimport importlib\n")
            
            # Write reloads
            for file_name in files:
                module_name, _ = os.path.splitext(file_name)
                init_file.write(f"if \"{module_name}\" in locals():\n")
                init_file.write(f"\timportlib.reload({module_name})\n")

        print(f"Created __init__.py in {dest_folder}")
        return init_file_path

def run_all_generate():
    os.system('cls' if os.name == 'nt' else 'clear')
    clean_previous_exports()

    # generated var needs to be ordered from new to older.
    generated = [] 

    generate_4_1 = FBXExporterGenerate((4, 1, 0), "Blender 4.1", export_fbx_files_with_threading)
    generated.append(generate_4_1.run_generate())

    generate_4_0 = FBXExporterGenerate((4, 0, 0), "Blender 4.0", export_fbx_files)
    generated.append(generate_4_0.run_generate())

    generate_3_6 = FBXExporterGenerate((3, 6, 0), "Blender 3.6", export_fbx_files)
    generated.append(generate_3_6.run_generate())

    generate_3_5 = FBXExporterGenerate((3, 5, 0), "Blender 3.5", export_fbx_files)
    generated.append(generate_3_5.run_generate())

    generate_3_4 = FBXExporterGenerate((3, 4, 0), "Blender 3.4", export_fbx_files)
    generated.append(generate_3_4.run_generate())

    generate_3_3 = FBXExporterGenerate((3, 3, 0), "Blender 3.3", export_fbx_files)
    generated.append(generate_3_3.run_generate())

    generate_3_2 = FBXExporterGenerate((3, 2, 0), "Blender 3.2", export_fbx_files)
    generated.append(generate_3_2.run_generate())

    generate_3_1 = FBXExporterGenerate((3, 1, 0), "Blender 3.1", export_fbx_files)
    generated.append(generate_3_1.run_generate())

    generate_2_93 = FBXExporterGenerate((2, 93, 0), "Blender 2.93", export_fbx_files)
    generated.append(generate_2_93.run_generate())

    generate_2_83 = FBXExporterGenerate((2, 83, 0), "Blender 2.83", export_fbx_files)
    generated.append(generate_2_83.run_generate())

    root_init_file = create_root_init_file(generated)
    edit_files.add_header_to_file(root_init_file)

    
def create_root_init_file(generated):
    init_file_path = os.path.join(parent_directory, '__init__.py')
    with open(init_file_path, 'w') as init_file:
        init_file.write("import bpy\n")
        init_file.write("import importlib\n")
        init_file.write("blender_version = bpy.app.version\n\n")

        # Write conditional imports
        for x, generate in enumerate(generated):
            if x == 0:
                init_file.write(f"if blender_version >= ({generate.replace('.', ',')}, 0):\n")
            else:
                init_file.write(f"elif blender_version >= ({generate.replace('.', ',')}, 0):\n")
            init_file.write(f"    from . import {io_scene_fbx_prefix}{generate} as current_fbxio \n")

        init_file.write("\n")
        
        # Write reloads
        init_file.write(f"if \"current_fbxio\" in locals():\n")
        init_file.write(f"    importlib.reload(current_fbxio)\n")

    print(f"Created root __init__.py in {parent_directory}")
    return init_file_path

def clean_previous_exports():
    for item in os.listdir(parent_directory):
        if item.startswith(io_scene_fbx_prefix):
            folder_path = os.path.join(parent_directory, item)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")


