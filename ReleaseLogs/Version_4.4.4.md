# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.4
- New: Support for Blender 5.0.
- New: Better feedback when an action or collection is missing due to library override.
- Change: Better support with Blender 4.4+ action slots.
- Fixed: All lods are exported with the same name, so the last lod become the lod 0 and the mesh don't have any lods.
- Fixed: After export, the mode is not restored correctly.
- Fixed: Custom FBX exporter don't load in Blender 2.80 to 2.82.
- Fixed: Update Action List button cached already cached actions from library files. The the action list contains doubled items.
- Fixed: When export a skeletal mesh with modular parts set in a linked object, the export produce a script fail.
- Fixed: pose_position of armature is not reset after export when exporting as a skeletal mesh from a library file.
- Fixed: bone constraints are not reset after export when exporting as a skeletal mesh from a library file in Blender 3.6.