# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.2.0
(Rev 0.4.2 before Semantic Versioning update https://semver.org)

- New: The addon now includes a modified version of the Blender standard FBX I/O API, instead of using the original one. (Thanks SAM-tak!)
- New: Exported models and animations now use Unreal bones coordinate by default. (Thanks SAM-tak!)
- New: Supports exporting models and animations with the Unreal Mannequin bone structure from Blender. (Thanks SAM-tak!)
- New: Supports exporting Blender's custom property animation in a format that Unreal Engine can recognize as curve data animation. (Thanks SAM-tak!)
- New: Alembic animation supports multiple unit scales and global scale.
- New: Selection filter "Only selected" and "Only selected and active action" now filters only visible objects.
- New: Modular export (export several skeletal meshes with the same skeleton).
- New: You can enable skeletal mesh per poly collision.
- New: Camera values Min and Max FStop are updated with Aperture.
- New: Support for ArchVis cameras (use of shift).
- New: Support for custom cameras (e.g., Blueprints).
- New: Support for Spline and Curves export/import.
- Faster camera export.
- Fixed: Blender 3.5 may crash during NLA export (interacting with an NlaStripFCurves not linked to an object could lead to a crash in Blender 3.5).
- Fixed: Applying skeletal export scale with Proxy and Unit Scale not set to 0.01 could result in a script error.
- Fixed: Using "Convert Attribute to UV" can swap UV indices in the exported mesh.
- Fixed: The "Export Procedure" option is visible with static meshes.
- Fixed: Hidden objects and collections are unhidden after export when using the same name.
- Fixed: Skeletons imported with skeletal meshes use incorrect names.
- Fixed: Collection.exclude is not recovered after export when using multi view layers.
- Fixed: Camera import script doesn’t work in Unreal Engine 5.3.
- Fixed: Export collections produce UI script fail.
- Fixed: Camera FBX is not exported when bfu_export_fbx_camera == True.
- Fixed: Show Asset To Export button produces script fail.
- Fixed: Curve mesh is duplicated during export.
- Fixed: Script fail in Blender 4.0 when switching to global view.
- Fixed: UI script fail in Blender 2.9.
- Fixed: Camera scale impacts the focus distance.