# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.3.0
(Rev 0.4.3 before Semantic Versioning update https://semver.org)

- New: Update for Blender 4.2.
- New: Orthographic camera support for copy/paste cameras.
- New: Disable render simplify during export to not lose subdivisions and mesh optimizations.
- New: Potential error and auto-fix for frame rate denominator and numerator.
- New: Option to set use_space_transform at export.
- New: Button to fix extreme UV scales in Tools > UV Map.
- New: New materials option for importing FBX files into Unreal.
- New: New options to create subfolders with the object name for Alembic and SkeletalMesh (used to avoid asset conflicts during export).
- New: Support for color types in Vertex Colors export.
- New: FBX Addon generator (for custom edits on the FBX Addon).
- New: Better FBX management for older versions.
- Change: "Convert Attribute to UV" is False by default.
- Change: Updated panel names to avoid confusion with other add-on panels in the Unreal Engine tab.
- Fixed: Import sequencer script fails for Unreal 5.0 and older versions (SequencerBindingProxy renamed to MovieSceneBindingProxy).
- Fixed: Import sequencer script fails if the camera is not a cinematic camera.
- Fixed: Import sequencer script fails if custom camera class is not found.
- Fixed: Imported camera sequencer does not have the same name in the level scene.
- Fixed: Armature child objects with inverse parent lost their transform positions if rescaled during export.
- Fixed: With Unit Scale not at 0.01, shape keys that are not location context are rescaled.
- Fixed: When rescaling the rig at export, all the drivers that were set were gone.
- Fixed: Camera scale does not use display size in camera data.
- Fixed: Check Potential Errors does not fix Hierarchy names with Sockets and Collisions.
- Fixed: Default export file paths are wrong.
- Fixed: Addon export checks "Convert Attribute to UV" and its "Attribute name" on the wrong object.
- Fixed: custom_export_name option does not work.