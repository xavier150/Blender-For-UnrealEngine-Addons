I recommend reading before the document How export assets from Blender.md if you have not read it: [Link](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20export%20assets%20from%20Blender.md)

# Import assets in Unreal engine
Depending on the object type, the import parameters are not the same.
- For Static mesh assets you need tick CombineMeshs
- For Skeletal mesh assets you need tick Import Morph Targets if you use Shape Keys
- The animation assets need be imported after the skeletal mesh
- For animations assets untick Import Mesh and select you Skeleton in Skeleton
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocParametersByType.jpg">


# Import assets in Unreal engine with UnrealEnginePython
1. Instal UnrealEnginePython: https://github.com/20tab/UnrealEnginePython
2. In Unreal Engine open Python Console. Window > Developer Tools > Python Console
3. Found "ImportAssetScript.py" file. It is placed by default at the location of the blender file in folder ExportedFbx\Other\
4. In Python Console run the command: `unreal_engine.py_exec(r'')` with ImportAssetScript file location. For me the command is: 
`unreal_engine.py_exec(r'G:\Projet perso\Small Project\BlenderScriptWork\BlenderforUnrealEngineAddon\0.2.0\ExportedFbx\Other\ImportAssetScript.py')`
	- The all assets will be imported by default in folder ImportedFbx in Unreal Content Browser. You can change folder location in Blender with the property Unreal import location in Import Script panel.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocImportScript.jpg">
Example video: https://youtu.be/FOFBfiE5EEQ


# Import Blender camera to Unreal Sequencer with UnrealEnginePython
It is possible to import complete sequence from blender to unreal with camera cut management and animations on special tracks like Fov (FocalLength), Aperture (F-stop), and Focus Distance
The Camera cuts are generated with Markers https://docs.blender.org/manual/en/dev/animation/markers.html#bind-camera-to-marker

1. Instal UnrealEnginePython: https://github.com/20tab/UnrealEnginePython
2. In unreal engine open your level and create a new Level Sequencer
3. Right clic on your new Level Sequencer and Copy Reference 
4. In Blender open Tool panel in 3D View (T), clic to Unreal engine 4 category, go in Import Script panel and paste sequence Reference in Unreal LevelSequence Reference property
5. Select you scene camera and set the Export type property on "Export recursive". Now repeat the task for all the camera.
6. Check potential errors and process the export
7. Found "ImportSequencerScript.py" file. It is placed by default at the location of the blender file in folder ExportedFbx\Other\
8. In Unreal Engine open Python Console. Window > Developer Tools > Python Console
9. In Python Console run the command: `unreal_engine.py_exec(r'')` with ImportSequencerScript file location. For me the command is: 
`unreal_engine.py_exec(r'G:\Projet perso\Small Project\Animation\LostMoon\ExportedFbx\Other\ImportSequencerScript.py')`
	- Open your Level Sequencer, the all cameras and camera cuts are now imported in !
	- If you want reimport sequence you will need remove camera cut and all cameras from your Level Sequencer before running the script again.
	- Animations, Poses and cameras can take a long time to export. Look in blender system console for more info.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocSequencerScript.jpg">
Example video: https://youtu.be/0PQlN-y2h2Q </br>
LostMoon animation: https://youtu.be/ApY2LpKkJNQ
