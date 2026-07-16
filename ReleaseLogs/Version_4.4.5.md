# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.5
- New: Support for Blender 5.1.
- New: New automatic fix for "Armature Child with Bone Parent" potential issue.
    When this issue is detected, you can now automatically fix it by converting the bone parent to an armature modifier.
- New: New automatic fix for "Armature Multiple Root Bones" potential issue.
    When this issue is detected, you can now automatically fix it by adding a new root bone and reparenting the existing root bones to it.
- New: New check potential issue for check number of UV maps.
- New: Native support for Unreal Engine 5.5 camera sensor offset (shift_x and shift_y).
- Fixed: Light Map UVs operator was not registered properly, causing errors when trying to use it.
- Fixed: bfu_build_nanite_mode property was using the wrong label.
    (It was labeled "Light Map" instead of "Build Nanite".)
- Fixed: Camera export produce script fail in Blender 5.0 due to changes in the Action API.
- Fixed: Camera delta_scale was not restored after export.