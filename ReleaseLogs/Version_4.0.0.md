# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.0.0
(Rev 0.4.0 before Semantic Versioning update https://semver.org)

- UI updated.
- Full addon refactoring.
- New Feature: Ability to specify skeleton asset for SkeletalMesh (Thanks to Salireths!).
- New Feature: Ability to specify which module (plugin) to import (Thanks to Salireths!).
- New Feature: SkeletalMesh now supports Armature from constraints.
- New Feature: Support for exporting UV from Geometry Node.
- Fixed: Axis flipping on camera animation can now be disabled.
- Corrected: Extreme UV Scale option moved from addon preferences to object settings.
- Added support for NearClippingPlane in camera export.
- Fixed: Vertex Colors refactored into generic Color Attributes and no longer supported by the addon.
- Fixed: Vertex colors would always be replaced (Thanks to ScrapIO!).
- Fixed: Mesh LODs did not import vertex color information (Thanks to ScrapIO!).
- Fixed: Skeleton detection used the wrong prefix.
- Fixed: Copying Cine Cameras returned Regular Cameras.
- Fixed: Crashes when pasting via "Copy Regular Cameras".
- Fixed: Convert to collision only worked if parent was a Mesh.
- Fixed: StaticSocketsAdd90X option broke non-uniform scale sockets.
- Fixed: Collection static mesh did not use Sub Folder Name.
- Fixed: Socket transformations were not applied to Collection static mesh.
- Fixed: Some collections remained hidden during export and exported files were incorrect.