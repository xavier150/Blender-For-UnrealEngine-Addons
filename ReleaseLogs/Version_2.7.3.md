# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.7.3
(Rev 0.2.7.3 before Semantic Versioning update https://semver.org)

- Fixed: Export fails if an object library has the same name as a real object.
- Fixed: With Unit Scale not at 0.01, if you export a SkeletalMesh and an animation at the same time, the animation can be wrong.
- Fixed: With Unit Scale not at 0.01, some constraints can make the animation wrong.
- Fixed: With Unit Scale not at 0.01, ShapeKeys are 100 times too big.
- Fixed: Bake Armature animation bakes only the current scene start to end frames.