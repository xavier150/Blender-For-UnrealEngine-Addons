# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 3.0.0
(Rev 0.3.0 before Semantic Versioning update https://semver.org)

- New: Text generator for exporting Skeletal Mesh Sockets in Unreal Engine (Copy/Paste).
- New: ExportAsProxy and ExportProxyChild options removed; this is now automatic.
- New: Support for Alembic import with import scripts.
- Change: Additional files now use JSON.
- Fixed: Camera export doesn't work when any marker_sequences were created.
- Fixed: "Show Asset(s)" button causes script error when no object is selected.
- Fixed: Removed collision in export collision list causes script error.
- Fixed: Collision on exported Instanced Collections doesn't work.
- Fixed: Sequencer Import Script doesn't work on older versions of Unreal Engine because the Python version is not the same.
- Fixed: Var Manual Focus Distance (Focus Settings) doesn't work in Sequencer Import Script.
- Fixed: When using Proxy Armature with sockets, wrong bones with socket names are exported.
- Fixed: Camera export doesn't work when scene has no timeline_markers.
- Fixed: Export fails with animation when tweakmode is activated.
- Fixed: Lightmap resolution = 4 when exporting without custom light map.
- Fixed: SkeletalMesh LODs are imported as normal meshes.
- Fixed: Export directories with invalid characters cause script error.
- Fixed: Show collection popup causes script error.
- Fixed: Collection export doesn't use SubCollection.