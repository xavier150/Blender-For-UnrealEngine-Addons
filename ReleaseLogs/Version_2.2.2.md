# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.2.2
(Rev 0.2.2c before Semantic Versioning update https://semver.org)

- Fixed: The animations have a size 100 times too small.
- Removed: All skeletal meshes are exported with the root joint named as Armature to be skipped in Unreal (this caused problems with the animations).
- Change: Hierarchy names are not automatically updated with each collisions conversion.
- Change: Hierarchy names are automatically updated with each export.