I recommend reading before the document How export assets from Blender.md if you have not read it: [Link](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20export%20assets%20from%20Blender.md)

# Import assets in Unreal engine
Depending on the object type, the import parameters are not the same.
- For Static mesh assets you need tick CombineMeshs
- For Skeletal mesh assets you need tick Import Morph Targets if you use Shape Keys
- The animation assets need be imported after the skeletal mesh
- For animations assets untick Import Mesh and select you Skeleton in Skeleton
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocParametersByType.jpg">

- For Alembic animations assets tick Merge Meshes
- Set ImportType on Skeletal
- Set FlipU on False and FlipV on True
- Set Scale 100,-100,100 (xyz)
- Set Rotation 90,0,0 (xyz)
Note: Alembic export and import can take a lot of time.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocParametersByType2.jpg">
Alembic example:
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocAlembicExample.gif">

# Import assets in Unreal engine with UnrealEnginePython

1. In Blender open the panel Import Script and define the location where you want to import the assets
2. Check potential errors and process the export
3. Open the panel Clipboard Copy and clic to appropriate button to easily copy the command
4. Instal UnrealEnginePython: https://github.com/20tab/UnrealEnginePython
5. In Unreal Engine open Python Console. Window > Developer Tools > Python Console
6. In Python Console run the copied command: 
	- `unreal_engine.py_exec(r'')` with your Script file location. 
	- The file ImportAssetScript.py is placed by default at the location of the blender file in folder ExportedFbx\
	
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocImportScript.jpg">
Example video: https://youtu.be/FOFBfiE5EEQ

# Import Blender camera to Unreal Sequencer with UnrealEnginePython
It is possible to import complete sequence from blender to unreal with camera cut management and animations on special tracks like Fov (FocalLength), Aperture (F-stop), and Focus Distance
The Camera cuts are generated with Markers https://docs.blender.org/manual/en/dev/animation/markers.html#bind-camera-to-marker

1. In Blender open the panel Import Script and define the location where you want to import the sequencer with his name
2. Select you scene camera and set the Export type property on "Export recursive". Now repeat the task for all the camera.
3. Check potential errors and process the export
4. Open the panel Clipboard Copy and clic to appropriate button to easily copy the command

5. Instal UnrealEnginePython: https://github.com/20tab/UnrealEnginePython
6. In Unreal Engine open Python Console. Window > Developer Tools > Python Console
7. In Python Console run the command: `unreal_engine.py_exec(r'')` with your ImportSequencerScript file location. 
	- `unreal_engine.py_exec(r'')` with your Script file location. 
	- The file ImportAssetScript.py is placed by default at the location of the blender file in folder ExportedFbx\
	- If you reimport the sequence deletes it which was imported first if no it will be imported with another name next to it

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocSequencerScriptExample.gif">
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocSequencerScript.jpg">
Example video: https://youtu.be/0PQlN-y2h2Q

# Use Unreal vania python
Note: since Rev 0.2.3 You can now use vania python but several features do not work at the moment.
1. In Blender set Use20TabScript on False in addon preferences. 
2. In Unreal enabled Pyton Editor Script Plugin, Editor Scripting Utilities and Sequencer Scripting.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocVaniaPython.jpg">
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocVaniaPythonUseCmd.jpg">
