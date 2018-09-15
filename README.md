# Blender For Unreal Engine
This addons allows you to export content created with Blender to Unreal Engine 4
Addons page: http://xavierloux.com/creation/view/?creation=blender-for-unrealengine-addons
GitHub page: https://github.com/xavier150/Blender-For-UnrealEngine-Addons

# How it works
Working on object packs for Unreal Engine 4 can be complicated with Blender. That's why I created the Addons "Blender for UnrealEngine". It simplifies the procedure of the export, allows to export all the Assets of a scene at the same time, distributed them in a proper tree structure in correlation with the UnrealEngine Pipeline.

- No need to place the object in the center of the scene in different layers to see something. Objects will export using their own origin - point as origin instead of the scene.
- It is possible to choose for each object how it should be exported.
- About SkeletalMesh it is possible to choose precisely the different animations that need to be exported.
- The addon also allows you to add Collisions Shapes and Socket to your StaticMesh directly in Blender
- Also includes a potential error checker to avoid problems with exporting.
- This Addon was created for Unreal Engine 4, but it also works for any other game engine that handles fbx files. The nomenclature being - - modifiable you can use any naming convention for organizing your assets.
- You can also choose which type of assets should be exported.

You can see tuto and doc here:
How export assets from blender: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20export%20assets%20from%20Blender.md
How import assets from Blender to Unreal: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md


I recommend reading before the document How export assets from Blender.md if you have not read it: 
# Installation
1. Download the latest release https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases
2. Open User Preferences (Ctrl+Alt+U) and under Add-ons, click Install from File. Then navigate to the file you downloaded and select it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/InstallationScreen1.jpg" width="600">
3. It should now appear in the window and you can tick the checkbox in the upper right to enable it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/InstallationScreen2.jpg" width="600">
If you would like to have the add-on enabled every time you start Blender, click Save User Settings at the bottom.
