# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.8.0
(Rev 0.2.8 before Semantic Versioning update https://semver.org)

- New: Better UI and optimized.
- New: Auto-Rig Pro support (needed for converting armature during the export).
- New: You can now choose the preview collision color.
- New: You can set a light map resolution depending on the surface area.
- New: New button to update light map resolution depending on the surface area.
- New: You can now use `../` to go up one directory in folder names.
- New: You can now set Socket name in object property if needed.
- New: You can now set skeleton name to use for import script (Proxy use).
- New: You can now set the desired export name directly for each object.
- New: More options for action names.
- New: Camera Sensor Width and Height are now added in additional tracks.
- New: Cached animation to export in UI for better optimization.
- New: Skeleton search mode for import animation with a specific skeleton.
- New: Option to export only selected objects and active actions.
- New: Option to export collections with subfolders.
- Change: New potential error: Check if the unit scale is equal to 0.01 (You can disable this potential error in addon preferences).
- Change: Better check and potential error info for Armature.
- Change: Some potential errors can have a button to the documentation.
- Change: Potential error (inherit_scale = False) bone removed.
- Change: 20 Tab Python integration is now not supported.
- Change: Better import script for Assets.
- Change: Better import script for Sequencer.
- Change: Asset export now uses JSON open data.
- Change: Camera export now uses JSON open data.
- Change: Camera export optimized.
- Change: Simple other changes in property values and texts.
- Change: Return to the user mode (OBJECT, EDIT, [...]) after the export.
- Change: Import Script values are now saved with Nomenclature Presets.
- Change: "Include armature in animation file name" option moved to Animation Properties Panel.
- Change: Clean illegal char, you can now use complex asset names without problems.
- Fixed: Export fails if the object contains shape keys and modifiers.
- Fixed: Export fails if UserMode not set.
- Fixed: Create PhysicsAsset option in SkeletalMesh always creates PhysicsAsset.
- Fixed: Useless data created by the export are not removed.
- Fixed: Potential error (multiple root bones) doesn't count bones correctly.
- Fixed: With Unit Scale not at 0.01, F-Curve modifiers are 100 times too small.
- Fixed: Focal length in additional tracks is not updated.
- Fixed: Sequencer import script error with 4.26, ConfigParser import changed to configparser.
- Fixed: Assets import script error with 4.26, ConfigParser import changed to configparser.
- Fixed: Camera cut in imported sequencer was not visible in other sequencers (CameraBindingID).
- Fixed: If armature name contains illegal characters, in Unreal the Skeletal Mesh is not found by Anim assets.
- Fixed: Fix potential error with popup can cause script errors.
- Fixed: FBX export crashes in Blender 2.8 when unused data is removed before export.
- Fixed: Socket object with lowercase characters are not updated during export (Custom name and +90X).
- Fixed: Select Vertex in potential error causes a script error if the model is hidden.
- Fixed: In Check potential error, create UV Project causes an error in Blender 2.9.
- Fixed: Alembic export causes an error if a face consists of more than 4 vertices.
- Fixed: Hard-coded Windows path doesn't work on Linux.
- Fixed: Some collisions and sockets can be exported with the wrong name (wrong rename after duplicate during export).
- Fixed: Vertex color is imported only with a reimport.
- Fixed: (Re-)Import of Generate Lightmap UVs option not updated.