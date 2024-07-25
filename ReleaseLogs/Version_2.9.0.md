# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.9.0
(Rev 0.2.9 before Semantic Versioning update https://semver.org)

- New: You can now choose a specific Vertex Paint to use when you export.
- New: You can now choose if you use scene or armature as origin for export in SkeletalMesh animations.
- New: Manage more characters and cultures in path or file names.
- New: Camera export takes less time + new camera options in addon preferences.
- Change: The SkeletalMesh is exported with scale at 1.0.
- Change: You can use "Show Asset(s)" and "Show Action(s)" buttons to force the update of the action cache.
- Change: Remove root bone modified to Add root bone.
- Change: Auto fix the "multiple root bones" potential error when exporting.
- Fixed: Creating a new preset causes a script error.
- Fixed: Export filter "Only select and active action" doesn't work with poses.
- Fixed: The export action cache is not correctly updated.
- Fixed: In camera sequencer with some frame rates, the frame keys can be shifted.
- Fixed: Exporting SkeletalMesh without animation_data causes script failure.
- Fixed: Button "Show Asset(s)" causes script failure when the selected actor is not a SkeletalMesh.
- Fixed: Animation file with space can cause errors during import.
- Fixed: Vertex color updated only in import option when reimporting.
- Fixed: With Unit Scale not at 0.01, SkeletalMesh has a wrong scale.
- Fixed: Import NLA animation with script doesn't work.
- Fixed: With Unit Scale not at 0.01, NLA animation will not export.
- Fixed: With Unit Scale not at 0.01, Blender 2.9.1 can crash with SkeletalMesh.
- Fixed: Apply Wrong Bool Modifier causes script error.
- Fixed: Mesh with disabled Modifier causes script error.
- Fixed: Additional location in advanced properties doesn't work for the cameras.
- Fixed: Export Instanced complex Collections can break the exported mesh.
- Fixed: Camera Sequencer doesn't work in Unreal Engine 5.