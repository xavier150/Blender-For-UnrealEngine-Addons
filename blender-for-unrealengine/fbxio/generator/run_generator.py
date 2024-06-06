import os
import shutil

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

    def run_generate(self):
        # Create the destination folder in the parent directory
        version_as_module = self.version.replace(".", "_")
        dest_folder = os.path.join(parent_directory, io_scene_fbx_prefix+version_as_module)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        self.copy_export_files(dest_folder)
        self.create_init_file(dest_folder)
        return version_as_module

    def copy_export_files(self, dest_folder):
        addon_folder = os.path.join(blender_install_folder, self.folder, self.version, io_fbx)

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
            else:
                print(f"File does not exist: {source_file}")

        print(f"Copied specified FBX exporter files for Blender {self.version} to {dest_folder}")

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

def run_all_generate():
    os.system('cls' if os.name == 'nt' else 'clear')
    clean_previous_exports()

    # generated var needs to be ordered from new to older.
    generated = [] 

    generate_4_1 = FBXExporterGenerate("4.1", "Blender 4.1", export_fbx_files_with_threading)
    generated.append(generate_4_1.run_generate())
    '''

    generate_4_0 = FBXExporterGenerate("4.0", "Blender 4.0", export_fbx_files)
    generated.append(generate_4_0.run_generate())

    generate_3_6 = FBXExporterGenerate("3.6", "Blender 3.6", export_fbx_files)
    generated.append(generate_3_6.run_generate())

    generate_3_5 = FBXExporterGenerate("3.5", "Blender 3.5", export_fbx_files)
    generated.append(generate_3_5.run_generate())

    generate_3_4 = FBXExporterGenerate("3.4", "Blender 3.4", export_fbx_files)
    generated.append(generate_3_4.run_generate())

    generate_3_3 = FBXExporterGenerate("3.3", "Blender 3.3", export_fbx_files)
    generated.append(generate_3_3.run_generate())

    generate_3_2 = FBXExporterGenerate("3.2", "Blender 3.2", export_fbx_files)
    generated.append(generate_3_2.run_generate())

    generate_3_1 = FBXExporterGenerate("3.1", "Blender 3.1", export_fbx_files)
    generated.append(generate_3_1.run_generate())

    generate_2_93 = FBXExporterGenerate("2.93", "Blender 2.93", export_fbx_files)
    generated.append(generate_2_93.run_generate())

    generate_2_83 = FBXExporterGenerate("2.83", "Blender 2.83", export_fbx_files)
    generated.append(generate_2_83.run_generate())
    '''

    create_root_init_file(generated)

    
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

def clean_previous_exports():
    for item in os.listdir(parent_directory):
        if item.startswith(io_scene_fbx_prefix):
            folder_path = os.path.join(parent_directory, item)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")



if __name__ == "__main__":
    run_all_generate()