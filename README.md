# Blender For Unreal Engine
This Add-on allows you to export content created with Blender to Unreal Engine 4. StaticMeshs, SkeletalMeshs, Animations (NLA and Actions), Collisions and Sockets, Alembic animations, Camera and sequencer [...]
</br>It works with Blender 2.7, 2.8, 2.9 and work for UE4, UE5!

Videos:
- [How Import Blender assets to Unreal Engine](https://youtu.be/2ehb2Ih3Nbg)
- [How Import Blender camera to Unreal Sequencer](https://youtu.be/Xx_9MQu2EkM)
- [Teaser](https://youtu.be/YLOZZIlhgaM)

# How it works and Documentation
Working on object packs for Unreal Engine 4 can be tedious with Blender. That's why I created the Add-on: "Blender for UnrealEngine". It simplifies the method of exporting from Blender to Unreal Engine 4 by allowing you to export all the assets of a scene at the same time. It even automatically distributes them in a proper tree structure in correlation with the Unreal Engine 4 pipeline!

Sockets and collision shapes are created directly in Blender.
You can precisely choose which animations need to be exported.
It includes a error checker to prevent potential problems and generate python scripts that can be used in Unreal Engine 4 to import the Camera Objects and Animations from your Blender project to a Level Sequence in Unreal Engine 4. All Camera Objects and their animations will import as Camera Actors.

You can see the tutorials and documentation here: [Wiki page](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki)

# Download and installation
1. Download addon:

|Version|Blender Version|Download URL|
|---|---|---|
|0.2.9 Preview 2 |Blender 2.8 / 2.9|[Download](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/tag/vp0.2.9.2)|
|0.2.8|Blender 2.8 / 2.9|[Download](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/tag/v0.2.8)|
|v0.2.3d|Blender 2.7|[Download](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/tag/v.0.2.3d)|

Or previous versions: [Releases page](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases)

2. Open User Preferences (Ctrl+Alt+U) and under Add-ons, click Install from File. Then navigate to the .zip file you downloaded and select it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/docs/InstallationScreen1.jpg" width="600">
3. It should now appear in the window and you can tick the checkbox in the upper right to enable it.
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/docs/InstallationScreen2.jpg" width="600">
If you would like to have the Add-on enabled every time you start Blender, click Save User Settings at the bottom of the user settings window

4. You can found the addons in the right side panel (N)
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/docs/InstallationScreen3.jpg" width="600">

# Download and installation from dev Branch
1. Switch Branch to Dev
2. 
<img src="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/blob/master/docs/SwitchBranchToDev.jpg">

3. Download source file as Zip file.
4. Extract "blender-for-unrealengine" folder
5. Compress "blender-for-unrealengine" as new Zip file.
6. Install the new zip file in Blender.
[Download and installation](#download-and-installation)

# Other
About the next versions: [Trello page](https://trello.com/b/32g729kg/blender-for-unreal-engine-addon) </br>
If you want support: [Support page](https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Support) <3
