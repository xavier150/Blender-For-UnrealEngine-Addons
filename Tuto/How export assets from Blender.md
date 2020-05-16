# Prepare asset(s) to export
We will see how to prepare the assets to export.

1. Open the Tool panel in 3D View (T), enlarge it, open Unreal engine 4 main panel and go to the Object Properties panel.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen1.jpg">

2. Select the asset you want to export and set the Export type property to "Export recursive". Now repeat the task for all the objects you want to export:
	- Each object having this property will export with all its children in a Fbx file. If you don't want to export the child set "Not exported" for Export type in Object Properties of the child, or else keep "Auto".
	- By default the center of the scene of the Fbx file will be equal to the origin point location of the object in blender. So the position of the object in the Blender scene does not matter. go in 'Advanced object properties panel' for change this. [Example video](https://youtu.be/rbW5NcyNoK0)
	- For a Skeletal mesh you need to set the Export type for Armature as Export recursive.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen2.jpg">

3. In the export panel click on the Export for UnrealEngine 4 button.

# Export collection like a StaticMesh
Exporting with collection will only export your collection like a StaticMesh.

1. Open the Tool panel in 3D View (T), enlarge it, open Unreal engine 4 main panel and go to the Collection Properties panel.
2. Click on the update button then select the collections that you want to export.
3. In the export panel click on the Export for UnrealEngine 4 button.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocExportCollection.jpg">



# Import properties
It is possible to define parameters for importing your assets in Unreal Engine in the Object Import Properties panel. This works only with importing via UnrealEnginePython.
About UnrealEnginePython: https://github.com/20tab/UnrealEnginePython </br>
How to import assets in Unreal Engine [Doc](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md)


# Collisions and Sockets
It possible to create collisions (StaticMesh) and sockets (Static/SkeletalMesh) for your Assets directly in blender.

1. Create a new mesh, it will be your collider shape (For a socket create a Empty object). 
	- An asset can contain multiple collider shapes but each collider must use a different object.
2. Select your collider Shape(s) or Empty(s) and at the end select the owner object.
	- For the SkeletalMesh select the Empty(s) then the owner bone in PoseMode.
3. Open Collisions and Sockets panel and click on the appropriate button to convert the selection to either collider or socket (Converted collider are green are now the child of the asset). 
	- About StaticMeshes collision:	https://docs.unrealengine.com/en-us/Engine/Content/FBX/StaticMeshes#collision.
	- If you want to create a capsule use 2 sphere in a same object. <img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocCollisionCapsule.gif">
	- If a "Not exported" child contains a collider, the collider will not be exported as the child.
	- If you change the name of the object that contains the collider you will need to click on the Check potential errors button to update hierarchy name of all the colliders.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocCollision.jpg">


# Level of details
This works only on StaticMesh with importing via UnrealEnginePython.
1. Select the asset you want to export and set the Export type property to "Export recursive". 
2. Now repeat the task for all LODs but also check the box "Export as lod?".
3. Select your main asset and open the panel Object Import Properties.
4. Set LOD1, LOD2, [...] to your desired LODs.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocLods.jpg"> 


# Animations
It is of course possible to export animations with your skeletal. You can use the Action Editor in the Dope Sheet window to have multiple animations in one scene or use the NonLinearAnimation.

For the Action:
1. Select your SkeletalMesh and open the Animation Properties panel (Do not forget to set the Armature as Export recursive).
2. Inside the Dope Sheet window select Action Editor mode and create your animations on actions ( /!\ Don't forget to use fake user to not lose your animation ! )
	- You can use driver for the Morph Target.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocAction.jpg"> 

3. In the Animation panel Properties you can set the animations property of your skeletal mesh like Animation time, Quality, and select the animations to export. 

Note if your animation is not a cycle set 'Offset at start frame' on 0
'Offset at start frame' are set on 1 by default because in the animation cycles, unreal will play the first and the last frame so twice the same.


With a offset of 0 in Unreal I have this:
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocActionOffsetCycle0.gif">

With a offset of 1 in Unreal I have this:
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocActionOffsetCycle1.gif"> 


For the NLA:
1. Select your SkeletalMesh and open Animation Properties panel (Do not forget to set the Armature as "Export recursive")
2. In Animation panel Properties you can set the animations property of your skeletal mesh like Animation time, Quality.
3. If you just want the NLAnimation set Action to export as Not exported and check the box Export Nla with your desired name.

# Export animation with Proxys (In next version)
If you want export the animations of a Skeletal Mesh with Proxys you should set 'Export recursive' on the proxy. Tick 'The armature is a Proxy ?' and select the child proxy.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocActionWithProxyV2.jpg"> 


# Alembic animation
Alembic export and import can take a lot of time.
1. Select the asset you want to export (Armature with child or Mesh).
2. Set the Export type property to "Export recursive".
3. Check the box Export as "Alembic animation".
4. Don't forget to check the box Alembic animation(s) in Asset types to export. Make sure that the animation was played at least once for baked cache. You can also use the command "bpy.ops.ptcache.bake_all()" to bake the physics. 
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocAlembic.jpg">


# Change export transform
You can set specific transform options at export in the Advanced object properties panel. Example video: https://youtu.be/rbW5NcyNoK0


# Material
Materials are not imported, you must create them in Unreal Engine.
1. Create your material in Unreal Engine .
2. Create a basic material in Blender with the same name.
3. If you use the import script set the Material Search Location with your desired search location.
4. If you don't use the import script, you need to set the Material > Search Location in Unreal with your desired location when you import.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocMaterial.jpg">


# Skeleton & Root bone
Blender exports the armature like a root bone. To remove this bone check the box "Remove root bone" in Addon Preferences.
If you don't want to remove it you can set the desired root bone name. If the name used is "Armature", Unreal Engine will remove the root bone. You can set the root bone scale too.
If you modify this you will have to import the animation.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocSkeletonTree.jpg">

Sine v0.2.6.1 the Unit scale will not change the scale of the exported mesh in Unreal.
If you working with unit scale at 0.01 I recommend using version 2.5 https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/tag/v.0.2.5
I will add a  options for change this in v0.2.7. 
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocUnitScale.jpg">

Sine v0.2.7 the addon are adapted to the all workflows. You can work with Unreal unit scale: 0.01 with Blender Unit scale: 1.00 or custom unit scale depending on your production. Example files: MySkeleton_BlenderSize.blend MySkeleton_UnrealSize.blend
This is automatically managed by the addon but if you need you can choose the how the rig need be scaled at the export.
Note: if you want to optimize the export time I recomande to use the Unreal unit scale at 0.01


# UV
You can correct extreme UV for better quality in Unreal Engine.
This is useful if you use UVProject Modifier in Blender.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocUVcorrected.jpg">


# Nomenclature 
The nomenclature is by default defined in correlation with the Unreal Engine Pipeline but you can change it if you use another pipeline.
By default all assets are exported to the location of the blender(.blend) which can be changed if you want. 
Depending on the assets you can also set a sub folder in Object Properties panel > Sub folder.
The nomenclature also contains the name of the script and additional file.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocNomenclatureColored.jpg">

# Addon Preferences
Don't forget to look in Addon Preferences.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocPreferences.jpg">

# Export process
Now we can export all assets.

1. Open the Export panel.
	- You can choose the type of object to export.
2. Click on Check potential errors button.
	- This will update all hierarchy name, correct the bad properties and show the potential errors.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocPotentialErrors.jpg">
3. Now click on the Export for UnrealEngine 4 button.
	- Animations, Poses and cameras can take a long time to export.
	- See in the blender system console for more info.
	- At each new export the old files will be overwritten.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocConsoleLog.jpg">
4. The files are placed by default at the location of the blender(.blend) file in the folder ExportedFbx.

# Import process
Read this doc: [How to import assets from Blender to Unreal](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md).

