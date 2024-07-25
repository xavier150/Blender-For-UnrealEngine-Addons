# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.7.0
(Rev 0.2.7 before Semantic Versioning update https://semver.org)

- New: Button for correcting Extrem UV in UV menu.
- New: VertexColorImportOption (Vania Python import for the moment).
- New: Option to choose how to rescale the SkeletalMesh depending on the Unit Scale.
- New: Option to choose how to rescale the sockets depending on the Unit Scale.
- New: Option to choose if export action should ignore Nonlinear Animation layer(s).
- New: Import LODs are now functional with Vania Python Import.
- New: Import script updated for 4.25.
- Change: StaticMesh and SkeletalMesh are automatically rescaled depending on the Unit Scale (Fix from 0.2.6).
- Change: Camera and sockets are automatically rescaled depending on the Unit Scale.
- Change: With Vania Python import, the SkeletalMesh imported with the animation will be automatically deleted.
- Change: Vania Python import will check if the plugin is activated.
- Change: New check if the FBX format plugin is activated.
- Change: Nonlinear Animation layer(s) are now by default not ignored.
- Fixed: Export camera causes script failure.
- Fixed: Import script doesn't work if a folder in the path contains "'".
- Fixed: Objects are not exported if bpy.context.object.hide_select = True.
- Fixed: Objects are not exported if bpy.context.object.hide_viewport = True.
- Fixed: Exporting while in local view mode produces bugs.
- Fixed: Since v0.26, workflow with 0.01 can be broken.
- Fixed: If armature is named "Armature", the export will change its name to "ArmatureRoot".