# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.7.4
(Rev 0.2.7.4 before Semantic Versioning update https://semver.org)

- Fixed: Animation created with Mixamo are not detected in auto.
- Fixed: With Unit Scale not at 0.01, if the armature scale is not equal to 1, the animation is wrong.
- Fixed: Animation bake doesn't work on all constraints.
- Change: New potential error: Check if the ARMATURE uses the same value on all scale axes.