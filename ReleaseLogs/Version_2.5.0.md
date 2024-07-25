# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.5.0
(Rev 0.2.5 before Semantic Versioning update https://semver.org)

- New: Updated for Blender 2.81.
- New: Option to export currently selected Action.
- New: New button in preferences to check for updates.
- New: New option in preferences to add +90 on StaticMesh sockets (Default True).
- Change: Frames offset removed with custom time.
- Fixed: exportGlobalScale is an int, it should be a float.
- Fixed: GetActionToExport() uses too many resources.
- Fixed: Setting frames with Custom time doesn't work.
- Fixed: "Automatic Update Check" takes too much time to check (removed).
- Fixed: StaticMesh sockets import size does not display the correct value.