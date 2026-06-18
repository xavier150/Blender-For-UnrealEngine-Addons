# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.6
- New: Support Unreal Engine 5.8.
- New: New preset apply operator to apply a preset to selected objects.
- Fixed: Import script fail in Unreal Engine 5.0 due to InterchangePipeline typing.
- Fixed: Import script set but don't apply LOD Group to Static Meshes in older Unreal Engine version.
    (This is due to a bug on older version that is now fixed.)
- Fixed: Alembic import produce script fail.
- Fixed: When Blender enum value matches not enum in a property the export can produce script fail.
    (Enum will now return a default value instead)
- Fixed: When the export fails because of the internal exporter, the addon will detect it and indicate it in the console.
- Fixed: Modular Skeleton Export don't use the sub folder in the export path.