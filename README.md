# Blender For Unreal Engine
This Add-on allows you to export content created with Blender to Unreal Engine 4. StaticMeshs, SkeletalMeshs, Animations (NLA and Actions), Collisions and Sockets, Alembic animations, Camera and sequencer [...]
</br>Video: https://youtu.be/YLOZZIlhgaM
</br>It works with Blender 2.8, 2.9 and earlier versions. 
# How it works and Documentation
Working on object packs for Unreal Engine 4 can be tedious with Blender. That's why I created the Add-on: "Blender for UnrealEngine". It simplifies the method of exporting from Blender to Unreal Engine 4 by allowing you to export all the assets of a scene at the same time. It even automatically distributes them in a proper tree structure in correlation with the Unreal Engine 4 pipeline!

Sockets and collision shapes are created directly in Blender.
You can precisely choose which animations need to be exported.
It includes a error checker to prevent potential problems and generate python scripts that can be used in Unreal Engine 4 to import the Camera Objects and Animations from your Blender project to a Level Sequence in Unreal Engine 4. All Camera Objects and their animations will import as Camera Actors.

You can see the tutorials and documentation here:
  - [How export assets from blender](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20export%20assets%20from%20Blender.md) </br>
  - [How import assets from Blender to Unreal](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/How%20import%20assets%20from%20Blender%20to%20Unreal.md)
   - [Potential Error with Blender export to Unreal] https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/Potential%20Error%20with%20Blender%20export%20to%20Unreal.md

# Download and installation
1. Download addon :
- [Rev 0.2.7.4 for Blender 2.8](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/download/v0.2.7.4/blender-for-unrealengine_2.8.zip) 
- [Rev 0.2.3d for Blender 2.7](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/download/v.0.2.3d/blender-for-unrealengine_2.7.zip)

Or previous versions : [Releases page](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases)

2. Open User Preferences (Ctrl+Alt+U) and under Add-ons, click Install from File. Then navigate to the .zip file you downloaded and select it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/InstallationScreen1.jpg" width="600">
3. It should now appear in the window and you can tick the checkbox in the upper right to enable it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/InstallationScreen2.jpg" width="600">
If you would like to have the Add-on enabled every time you start Blender, click Save User Settings at the bottom of the user settings window

4. You can found the addons in the right side panel (N)
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/Tuto/InstallationScreen3.jpg" width="600">

# Download and installation from sources
1. Download source file as Zip file.
2. Extract "blender-for-unrealengine - 2.8" folder
3. Rename "blender-for-unrealengine - 2.8" to "blender-for-unrealengine"
3. Compress "blender-for-unrealengine" as new Zip file.
4. Install the new zip file in Blender.
[Download and installation](#download-and-installation)

# Other
About the next version: [Trello](https://trello.com/b/32g729kg/blender-for-unreal-engine-addon) </br>
If you want support me you can buy the addon on [gumroad](https://gumroad.com/l/blenderforunreal) or [blendermarket](https://blendermarket.com/products/blender-for-unreal-engine)
