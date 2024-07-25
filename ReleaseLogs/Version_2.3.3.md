# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.3.3
(Rev 0.2.3d before Semantic Versioning update https://semver.org)

- Change: Export can use custom properties (used for Metadata). You can activate this in addon preferences.
- Fixed: bpy.ops.object.showasset() causes an error with SkeletalMesh animation.
- Fixed: Exporting camera causes an error with Blender 2.7 (hide for 2.7, hide_viewport for 2.8).