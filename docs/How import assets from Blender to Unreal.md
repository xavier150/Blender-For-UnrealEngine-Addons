I recommend reading [this](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20export%20assets%20from%20Blender.md) before about how to export assets from blender.

# Import assets in Unreal engine
Depending on the object type, the import parameters are not the same.
- For Static mesh assets you need tick CombineMeshs.
- For Skeletal mesh assets you need tick Import Morph Targets if you use Shape Keys.
- The animation assets should be imported after the skeletal mesh.
- For animations assets untick Import Mesh and select you Skeleton in Skeleton.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocParametersByType.jpg">

- For Alembic animations assets tick Merge Meshes.
- Set ImportType to Skeletal.
- Set FlipU to False and FlipV to True.
- Set Scale to 100,-100,100 (xyz).
- Set Rotation to 90,0,0 (xyz).<br>
Note: Alembic export and import can take a lot of time.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocParametersByType2.jpg">
Alembic example:
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocAlembicExample.gif">

# Use Unreal python impôrt scripts
2. In Unreal enable Pyton Editor Script Plugin, Editor Scripting Utilities and Sequencer Scripting.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocVaniaPython.jpg">
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocVaniaPythonUseCmd.jpg">

# Import assets in Unreal engine with python
1. In Blender open the panel Import Script and enter the location where you want to import the assets.
2. Check potential errors and process the export.
3. Open the panel Clipboard Copy and click on appropriate button to easily copy the command for import asset.
4. In Unreal Engine open Output Log. Window > Developer Tools > Output Log
5. In  Output Log run the copied command(Cmd type): 
	- `py "C:\[Folder]\ImportSequencerScript.py"` with your Script file location. 
	- The file ImportAssetScript.py is placed by default at the location of the blender file in folder ExportedFbx\
	
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocImportScript.jpg">
Example video: https://youtu.be/FOFBfiE5EEQ

# Import Blender camera to Unreal Sequencer with python
It is possible to import complete sequence from blender to unreal with camera cut management and animations on special tracks like FOV (FocalLength), Aperture (F-stop), and Focus Distance. The Camera cuts are generated with Markers https://docs.blender.org/manual/en/dev/animation/markers.html#bind-camera-to-marker

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocSequencerScriptExample.gif">

1. In Blender open the panel Import Script and define the location where you want to import the sequencer into Unreal Engine with the name.
2. Select your scene camera and set the Export type property on "Export recursive". Now repeat the task for all the camera.
3. Check potential errors and process the export.
4. Open the panel Clipboard Copy and click on appropriate button to easily copy the command for import sequencer.

5. In Unreal Engine open Output Log. Window > Developer Tools > Output Log
6. In Output Log run the command (Cmd type): 
	- `py "C:\[Folder]\ImportSequencerScript.py"` with your ImportSequencerScript file location. 
	- The file ImportAssetScript.py is placed by default at the location of the blender file in folder ExportedFbx\
7. Please note that the sequencer will be override on each import. I strongly recommend to use a separate sequencer for your cameras
	- So you can manage your assets in a sequencer and keep another sequencer to override for your cameras.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ImportAssetDocSequencerScript.jpg">
Example video: https://youtu.be/0PQlN-y2h2Q
