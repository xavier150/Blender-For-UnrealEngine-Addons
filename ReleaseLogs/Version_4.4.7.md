# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.7
- New: Support Blender 5.2.
- New: "Export self only" option for object export type. (This allows to export only the object without its children.)
- Fixed: The export did not correctly rescale all objects when the hierarchy was non-linear.
    (Re-parenting was not applied correctly after duplication, so rescaling was not applied to them.)
- Fixed: Animation export produce script fail in older versions of Blender (4.3 and below).
    (This was due to the use of a new API in Blender 4.4, which is not available in older versions. "bpy.types.ActionSlot")
