# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.3.0
(Rev 0.2.3 before Semantic Versioning update https://semver.org)

- New: Alembic animation, Export and Import.
- New: You can now change the CollisionTraceFlag of the StaticMesh (Collision Complexity).
- New: It is now possible to choose the name of the root bone for the skeleton in addon preferences (if "Armature", UE4 will remove the root bone).
- New: You can check export_ExportOnlySelected = True to export only the selected assets groups.
- New: You can choose which Python integration to use for Import Script. (/!\ With vanilla Python integration, some features like StaticMesh LOD or SkeletalMesh Sockets integration do not work).
- New: You can choose a preset for nomenclature export properties.
- New: You can choose the Sockets scale for SkeletalMesh and StaticMesh.
- Change: All collisions are now named with two suffixes: Type_MeshName_##.
- Change: New potential errors will be detected in the potential error report (CheckArmatureMultipleRoots).
- Fixed: In 2.8, the addon can try to export removed mesh and crash.
- Fixed: In 2.8, bpy.context.scene.update() has been removed and this causes script errors.
- Fixed: In 2.8, Export sequencer causes errors (the variables of Depth of Field have been renamed).
- Fixed: Setting clipboard with encode('utf8') causes errors.
- Fixed: Sockets are not attached to bones with illegal characters (bone.001 -> bone_001).
- Fixed: Sockets are exported with an offset in AdditionalParameter.
- Fixed: Reimporting SkeletalMesh with import script can cause Unreal crash in 22.2.
- Fixed: Command bpy.ops.object.checkpotentialerror() doesn't work if not run with the button.
- Fixed: CheckVertexGroupWeight does not detect if a VertexGroup is not used by a bone.
- Fixed: In 2.8, Mesh select error vertex doesn't work well.
- Fixed: In Unreal 22.2, the sequencer with imported FBX camera doesn't have transform (now the camera uses AdditionalParameter file for import transform).