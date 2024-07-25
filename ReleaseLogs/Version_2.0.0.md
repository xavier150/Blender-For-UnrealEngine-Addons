# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.0.0
(Rev 0.2.0 before Semantic Versioning update https://semver.org)

- New script generator for importing assets into Unreal.
- New script generator for importing sequencer into Unreal.
- New export log.
- Now the animation can be exported without having to export the skeletal mesh with it.
- Now the export quality of animations is managed directly in the object with SampleAnimForExport and SimplifyAnimForExport properties.
- Update button "check potential error": Largest list of potential problems.
- "Correct bad properties" and "update hierarchy" buttons were included in "check potential error" button.
- "Check potential error" button was moved to the export panel.
- Potential error(s) are now displayed in a popup.
- Optimized Code. (Multiple files)
- Optimized UI.
- ExportCameraPacked removed (the cameras in pack have been removed because they pose too many problems for the definition of the parameters between each camera).
- Now the cameras are exported with additional tracks: FOV (FocalLength), Aperture (F-stop), and Focus Distance.
- It is now possible to force the duration of an animation according to the scene or custom value.
- Copy/Paste CameraCut code text has been removed.
- "Export (FBX property)" panel is now named "Nomenclature".
- New data in Nomenclature panel.
- Fixed: Bad file name caused script failure. Now the not allowed characters are deleted in the filename during export.
- Fixed: Objects without animation_data caused script failure.
- Fixed: The camera was exported with a size 100 times too large. Now a temporary size is applied during export on delta_scale.
- Fixed: Sockets can have custom names and a temporary size is applied during export on delta_scale.
- Fixed: Pose-type animations were exported with the wrong prefix.
- Fixed: The Force StaticMesh option did not work.
- Other small changes.