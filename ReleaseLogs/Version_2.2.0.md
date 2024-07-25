# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.2.0
(Rev 0.2.2 before Semantic Versioning update https://semver.org)

- New: Updated for Blender 2.8.
- New: You can now manage LOD (LevelOfDetail) directly in Blender (StaticMesh only for the moment).
- New: You can now export NAL animations.
- New: Two buttons to copy the command for importing assets and sequencer in Unreal.
- New: You can now create sockets for SkeletalMesh directly in Blender.
- New: Select button for potential error report. It is possible to directly select the object or vertices incriminated.
- New: All skeletal meshes are exported with the root joint named as Armature to be skipped in Unreal.
- New: For the sequencer, the camera visibility (Eye Symbol in Blender) will be used for spawned value in sequencer.
- New: Now in Unreal with the sequencer, a CameraCut will be created automatically if the Blender scene does not contain a Marker.
- New: It is possible to change the name of the import script for Unreal.
- New: Import script updated for 4.21.
- New: Choose version value removed (is now automatic).
- New: You can choose bAutoGenerateCollision for Import Script.
- Change: It is now no longer necessary to create a new sequencer in Unreal Engine for import from Blender, the script will create it itself.
- Change: The potential error report contains more details to correct the errors.
- Change: New potential errors will be detected in the potential error report (marker).
- Change: Show assets button report contains more information and is clearer.
- Change: In the Export log, the NLA types, poses, and actions are indicated as animations.
- Change: Export_pose check mark removed (now only one check mark for all animation types).
- Change: Hierarchy names are automatically updated with each collisions conversion.
- Fixed: Export action doesn't work with NLA Change.
- Fixed: Unable to fix the object that is not in a visible layer.
- Fixed: The potential error display showed some errors in duplicate.
- Fixed: Reload importlib did not work well.
- Fixed: The generated sequencer sections are sometimes offset by one frame.
- Fixed: Some files with special names do not work with Unreal import, so the name is now corrected directly at Blender export.
- Fixed: The camera cut sections are too long by 0.0001 frames.
- Fixed: UpdateNameHierarchy makes bad parent_set with the ConvertToUe4SubObj function.
- Fixed: ResetArmaturePose function doesn't work with rotation mode Euler.
- Temporary problem: Currently on Blender 2.8 the hidden objects will not be exported, use Shift+H to unhide all objects.