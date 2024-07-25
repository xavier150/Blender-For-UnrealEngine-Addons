# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.6.2
(Rev 0.2.6.2 before Semantic Versioning update https://semver.org)

- New: New options for exporting animations from Proxy.
- New: Show action(s) will now also display the frames range.
- New: Option to include or not the armature name in the animation file name.
- Change: Works better with very complex rigs.
- Change: bfu_anim_action_start_frame_offset set to 1 by default for animation cycles.
- Fixed: SocketsAdd90X breaks the socket export location.
- Fixed: Modifier with non-MESH type object can make the script fail.
- Fixed: CheckArmatureMultipleRoots doesn't work correctly.
- Fixed: The export process creates an empty with Proxy Armature.
- Fixed: Proxy armature with curve in rig can break the animation.
- Fixed: Script fails with modifier on Curve or Text.