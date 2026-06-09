# Linux Setup
### Create environment for linux
``` bash
mkdir -p ~/venvs
python3 -m venv ~/venvs/blender_for_unrealengine
source ~/venvs/blender_for_unrealengine/bin/activate
```

### Install fake bpy module (Blender API)
``` bash
cd ~/venvs/blender_for_unrealengine/bin
python -m pip install --upgrade pip
python -m pip install fake-bpy-module-latest
python -m pip install --upgrade fake-bpy-module-latest
```

### Install Unreal Engine Python API
- Open Unreal Engine
- Edit → Project Settings → Plugins → Python
- Enable Developer Mode in Python -> Advanced
- Restart Unreal Engine (This will generate the Python API stubs in `<UnrealProjectPath>/Intermediate/PythonStub/unreal.py`)
- Copy the generated stubs from `<UnrealProjectPath>/Intermediate/PythonStub/unreal.py` to `~/venvs/blender_for_unrealengine/Lib/site-packages`

### Set VSode Python interpreter
In VSCode, press `Ctrl+Shift+P`, then select `Python: Select Interpreter`, 
and choose the interpreter located at `~/venvs/blender_for_unrealengine/bin/python`.


# Windows Setup
### Create environment for windows
Open PowerShell 7 and run the following commands:
``` bash
py -m venv C:\venvs\blender_for_unrealengine
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
C:\venvs\blender_for_unrealengine\Scripts\Activate.ps1
```

### Install fake bpy module (Blender API)
``` bash
cd C:\venvs\blender_for_unrealengine\Scripts
python.exe -m pip install --upgrade pip
python.exe -m pip install fake-bpy-module-latest
python.exe -m pip install --upgrade fake-bpy-module-latest
```

### Install Unreal Engine Python API
- Open Unreal Engine
- Edit → Project Settings → Plugins → Python
- Enable Developer Mode in Python -> Advanced
- Restart Unreal Engine (This will generate the Python API stubs in `<UnrealProjectPath>\Intermediate\PythonStub\unreal.py`)
- Copy the generated stubs from `<UnrealProjectPath>\Intermediate\PythonStub\unreal.py` to `C:\venvs\blender_for_unrealengine\Lib\site-packages`


### Set VSode Python interpreter
In VSCode, press `Ctrl+Shift+P`, then select `Python: Select Interpreter`, 
and choose the interpreter located at `C:\venvs\blender_for_unrealengine\Scripts\python.exe`.
`Ctrl+Shift+P` -> Python: Restart Language Server.

# Best Practices
- Follow the official Blender best practices for addon development:
"Blender best_practice": "https://docs.blender.org/api/current/info_best_practice.html"

# Copilot Guidelines
- Always write comments in English
- Follow PEP8
- Follow strict typing
- Prefer Pathlib over os.walk / os.path
- for bpy.types.Object don't check type with `obj.type == 'MESH'` use `isinstance(obj.data, bpy.types.Mesh)`