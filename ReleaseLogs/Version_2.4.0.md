# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 2.4.0
(Rev 0.2.4 before Semantic Versioning update https://semver.org)

- New: Button to open documentation.
- New: Button to open the last release page (GitHub).
- New: You can choose to export with scene origin or object origin.
- New: You can choose to export with scene rotation or object rotation.
- New: You can add additional location to asset for export.
- New: You can add additional rotation to asset for export.
- New: You can choose bone axis with SkeletalMesh.
- New: Export now uses a copy of the mesh to apply modifier, instance groups, and collections.
- New: You can choose presets for object global properties.
- Change: AddOneAdditionalFramesAtTheEnd replaced by bfu_anim_action_start_frame_offset and bfu_anim_action_end_frame_offset.
- Change: Export can use MetaData. You can activate this in addon preferences.
- Change: It is now possible not to write the additional parameters (.ini files).
- Change: Import script syncs the UE4 Content Browser to the imported asset (Vania Python only).
- Fixed: Invalid syntax in ImportAssetScript.py if asset name uses "-".
- Fixed: CollisionTraceFlag can't be set if UseStaticMeshLODGroup is False.
- Fixed: Export recursive object can be wrongly placed to the scene center if it is a child of another object.