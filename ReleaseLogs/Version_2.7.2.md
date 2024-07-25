# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.7.2
(Rev 0.2.7.2 before Semantic Versioning update https://semver.org)

- New: Check potential error will detect if the armature has at least one deform bone.
- Change: Bake armature will bake 10 frames before and after for better animation accuracy.
- Change: The duration of the animation will be automatically corrected if it is null or negative.
- Fixed: Import script doesn't remove old LODs.
- Fixed: FocalLength doesn't use the same math from Blender to UE4.
- Fixed: Action poses are exported with a null duration (wrong for UE4).
- Fixed: If the imported animation is wrong, it causes a script error.
- Fixed: Option auto for Rescale rig will always rescale.