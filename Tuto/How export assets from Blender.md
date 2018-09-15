# Set asset(s) to export
We will see how to define the assets to export

1. Open Tool panel in 3D View (T), clic to Unreal engine 4 category and go in Object Properties panel
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen1.jpg">
2. Select the asset you want to export and set the Export type property on "Export recursive". Now repeat the task for all the objects you want to export.
	- Each objects that has this property will export with all its children in a Fbx file. if you don't want export the child set "Not exported" Export type property to the child. else keep "Auto".
	- The center the scene of the Fbx file will be equal to the origin point location of the object in blender. The position of the object in the Blender scene does not matter.
	- For the Skeletal mesh you need set the Armature as Export recursive.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocScreen2.jpg">


# Import properties
It is possible to define parameters for importing your assets into the Object Import Properties panel, but this only works with importing via UnrealEnginePython
About UnrealEnginePython: https://github.com/20tab/UnrealEnginePython
How Import asset in Unreal Engine https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How import assets from Blender to Unreal.md


# Collisions and Sockets
It possible to create collisions and socket for your StaticMesh assets in blender.

1. Create a new mesh, it will be your collider shape. And place it to your asset. (For a socket create a Empty object)
	- An asset can contain multiple collider shapes but each collider must use a different object
2. Select your collider shape(s) or Empty object and at the last select your target asset.
3. In Collisions and Sockets panel clic on the appropriate button for the convert the selection to collider or socket (Converted collider are green are now the child of the asset) 
	- About StaticMeshes collision:	https://docs.unrealengine.com/en-us/Engine/Content/FBX/StaticMeshes#collision
	- If you want to create a capsule use 2 sphere in a same object.
	- is a  Not exported child contains collider, the collider will not exploring as the child.
	- If you change the name of the objet that contains the collider you will need clic on Check potential errors button for update hirarchy name of the all colliders.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocCollision.jpg">


# Animations
It is of course possible to export animations with your skeletal mesh but you need use Action Editor in Dope Sheet windows

1. select your SkeletalMesh and open Dope Sheet windows
2. Set Action Editor mode and create your animations on actions ( /!\ Don't forget to use fake user to not lose your animation ! )
	- You can use driver for the Morph Targer
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocAnimation.jpg">
3. Open Tool panel in 3D View (T) and clic to Unreal engine 4 category. 
4. Select your SkeletalMesh and in Animation panel Properties you can set the animations property of your skeletal mesh like Animation time, Quality, and select the animations to export.


# Nomenclature 
1. go in Nomenclature panel.
	- The nomenclature is by default defined in correlation with the UnrealEngine Pipeline but you can change it is you use another pipeline. For change nomenclature property 
	- By default the all assets are exported to the location of the blender file but you can also change this.
	- Depending on the assets you can also set a sub folder in Object Properties panel, Sub folder name property
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocNomenclatureColored.jpg">


# Export process
Now we can export all asset.

1. go in Export panel.
	- You can choose the type of object to export
2. clic on Check potential errors button
	- This will update all hirarchy name, correct the bad properties  and show the potential errors.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocPotentialErrors.jpg">
3. Now clic on the big sexy Export for UnrealEngine 4 button
	- Animations, Poses and cameras can take a long time to export.
	- Look in blender system console for more info.
	- At each new export the old files will be overwritten
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/ExportAssetDocConsoleLog.jpg">

