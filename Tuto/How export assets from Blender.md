# Set asset(s) to export
We will see how to define the assets to export

1. Open Tool panel in 3D View (T), enlarge it, open to Unreal engine 4 main panel and go in Object Properties panel
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen1.jpg">

2. Select the asset you want to export and set the Export type property on "Export recursive". Now repeat the task for all the objects you want to export.
	- Each objects that has this property will export with all its children in a Fbx file. if you don't want export the child set "Not exported" Export type property to the child. else keep "Auto".
	- The center the scene of the Fbx file will be equal to the origin point location of the object in blender. The position of the object in the Blender scene does not matter.
	- For the Skeletal mesh you need set the Armature as Export recursive.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen2.jpg">


# Import properties
It is possible to define parameters for importing your assets into the Object Import Properties panel. This works only with importing via UnrealEnginePython
About UnrealEnginePython: https://github.com/20tab/UnrealEnginePython </br>
How import assets in Unreal Engine [Doc](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md)


# Collisions and Sockets
It possible to create collisions (StaticMesh) and sockets (Static/SkeletalMesh) for your Assets directly in blender.

1. Create a new mesh, it will be your collider shape. (For a socket create a Empty object) And place it to your asset. 
	- An asset can contain multiple collider shapes but each collider must use a different object
2. Select your collider shape(s) or Empty(s) at the last select the owner object.
	- For the SkeletalMesh select the Empty(s) then the owner bone in PoseMode.
3. Open Collisions and Sockets panel and clic on the appropriate button for the convert the selection to collider or socket (Converted collider are green are now the child of the asset) 
	- About StaticMeshes collision:	https://docs.unrealengine.com/en-us/Engine/Content/FBX/StaticMeshes#collision
	- If you want to create a capsule use 2 sphere in a same object. <img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocCollisionCapsule.gif">
	- is a  Not exported child contains collider, the collider will not exploring as the child.
	- If you change the name of the objet that contains the collider you will need clic on Check potential errors button for update hirarchy name of the all colliders.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocCollision.jpg">


# Level of details
This works only on StaticMesh with importing via UnrealEnginePython
1. Select the asset you want to export and set the Export type property on "Export recursive". 
2. Now repeat the task for all Lod but also check the case "Export as lod?"
3. Select your main asset and open the panel Object Import Properties
4. Set LOD1, Lod2, [...] to your desired Lods
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocLods.jpg"> 


# Animations
It is of course possible to export animations with your skeletal. You can use the use Action Editor in Dope Sheet windows to have multiple animations in one scene or use the NonLinearAnimation

For the Action:
1. select your SkeletalMesh and open Open Animation Properties panel (Do not forget to set the Armature as Export recursive)
2. Dope Sheet windows and set Action Editor mode and create your animations on actions ( /!\ Don't forget to use fake user to not lose your animation ! )
	- You can use driver for the Morph Targer
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocAction.jpg"> 
3. In Animation panel Properties you can set the animations property of your skeletal mesh like Animation time, Quality, and select the animations to export.

For the NLA:
1. select your SkeletalMesh and open Open Animation Properties panel (Do not forget to set the Armature as Export recursive)
2. In Animation panel Properties you can set the animations property of your skeletal mesh like Animation time, Quality.
3. If you just want the NLAnimation set Action to export as Not exported and check the box Export Nla with your desired name

# Alembic 
Alembic export and import can take a lot of time.
1. Select the asset you want to export (Armature with child or Mesh) 
2. Set the Export type property on "Export recursive"
3. check ExportAsAlembic
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocAlembic.jpg">

# Marterial
Materials are not imported, you must create them in Unreal Engine
1. Create your material in Unreal Engine 
2. Create a basic material in Blender with the same name
3. If you use the import script set the Material Search Location with your desired search location
4. If you d'ont use the import script you need when you import the Material Search Location in Material > Search Location, with your desired search location
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocMaterial.jpg">


# Nomenclature 
The nomenclature is by default defined in correlation with the UnrealEngine Pipeline but you can change it is you use another pipeline.
By default the all assets are exported to the location of the blender file but you can also change this. 
Depending on the assets you can also set a sub folder in Object Properties panel > Sub folder.
The nomenclature also contains the name of the script and additional file.

<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocNomenclatureColored.jpg">

# Export process
Now we can export all asset.

1. Open the Export panel.
	- You can choose the type of object to export
2. clic on Check potential errors button
	- This will update all hirarchy name, correct the bad properties  and show the potential errors.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocPotentialErrors.jpg">
3. Now clic on the Export for UnrealEngine 4 button
	- Animations, Poses and cameras can take a long time to export.
	- Look in blender system console for more info.
	- At each new export the old files will be overwritten
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocConsoleLog.jpg">
4. The files are placed by default at the location of the blender file in folder ExportedFbx

# Import process
Read this doc: [How import assets from Blender to Unreal](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md)

