# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.3
- New: Better log feedback when import fails.
- New: New buttons in collision panel create collision from selected objects and not just convert.
- New: New option to use world space for collision shapes.
- New: New option to keep original geometry when creating collision shapes.
- New: New button to select all collision objects from a selection.
- Changed: Materials on collision meshes now use the name "UE_Collision" (Before "UE4Collision").
- Changed: Check Potential Issues now also fix collision materials on collision meshes.
- Changed: Optimized the function that applies the collisions and sockets.
- Changed: New box collision algorithm that create a better fitting box.
- Fixed: For static meshes and collections assets the export path doubled the subfolder.
- Fixed: Remove all use of InterchangeGenericAssetsPipeline in Unreal Engine 4.27
- Fixed: Ensure import destination paths are correctly formatted in Unreal Engine 4.27
- Fixed: After import FBX animation using FbxImportUI, removing the extra skeletal mesh and renaming animation may fail because different naming in UE versions.
- Fixed: Non Linear Animation (NLA) assets were not visible in the animation preview bar.
- Fixed: NLA export name was wrong and used the object name instead of the NLA name.
- Fixed: When using Unreal Interchange Pipeline (5.6), importing a static mesh with collision may also adds the Blender collision material as a new slot. Removing materials at the export fix the issue.
- Fixed: When search filter is set to "Only Object and Active", Action is always exported even if "Use Actions Export" is disabled.
- Fixed: Skeletal mesh sockets position are wrong when copied from an armature with glTF export procedure.
- Fixed: Undo after set a collision or socket may crash Blender.