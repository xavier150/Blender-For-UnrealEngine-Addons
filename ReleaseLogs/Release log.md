### Version 1.3.0
(Rev 0.1.3 before Semantic Versioning update https://semver.org)

- Initial release.

### Version 1.5.0
(Rev 0.1.5 before Semantic Versioning update https://semver.org)

- Keeps all user and scene settings after export.
- More export customizations.
- Exporting animation with a single frame is no longer a problem.

### Version 1.7.0
(Rev 0.1.7 before Semantic Versioning update https://semver.org)

- More export customizations.
- Fixed: Hidden objects were not exported.
- Fixed: Error if no object is active.
- Fixed: UE4Collision materials are black.
- Optimized Code.

### Version 1.8.0
(Rev 0.1.8 before Semantic Versioning update https://semver.org)

- More export customizations.
- More export feedback info.
- New button "correct bad property".
- New button "check potential error".
- Fixed: Export fail with hidden layers.
- Fixed: Wrong exported animation time.
- Fixed: ShapesKeys to MorphTargets not exported.
- Fixed: No Smoothing for skeletal mesh.

### Version 1.9.1
(Rev 0.1.9b before Semantic Versioning update https://semver.org)

- Update button "check potential error": Largest list of potential problems.
- New button "Update hierarchy names": Allows to automatically replace the name of a collision/socket by the name of its corresponding parent object, so that it will be recognized in UE4.
- New export properties for Actions: New options to precisely select the animations that need to be exported with the armature.
- New nomenclature properties: It is now possible to choose the different Asset types that must be exported.
- New FBX properties: Anim sampling Rate.
- New Assets types: Pose, AnimationSequence, and Camera.
- New button "Copy Camera Cuts to clipboard": Allows copying camera cuts from Blender and pasting them into the sequencer of Unreal Engine.
- Fixed: Not selectable objects were not exported.
- Fixed: The collision material and not transparent with GLSL mat in Cycle.
- Removed: Select panel.
- More feedback info.
- Optimized Code.
- Other small changes.

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

### Version 2.1.0
(Rev 0.2.1 before Semantic Versioning update https://semver.org)

- It is possible to choose the version of Unreal for script generation.
- The frame rate uses denominator and numerator for sequencer now.
- Fixed: Camera import sequencer does not work with Unreal 4.19.

### Version 2.2.0
(Rev 0.2.2 before Semantic Versioning update https://semver.org)

- New: Updated for Blender 2.8.
- New: You can now manage LOD (LevelOfDetail) directly in Blender (StaticMesh only for the moment).
- New: You can now export NAL animations.
- New: Two buttons to copy the command for importing assets and sequencer in Unreal.
- New: You can now create sockets for SkeletalMesh directly in Blender.
- New: Select button for potential error report. It is possible to directly select the object or vertices incriminated.
- New: All skeletal meshes are exported with the root joint named as Armature to be skipped in Unreal.
- New: For the sequencer, the camera visibility (Eye Symbol in Blender) will be used for spawned value in sequencer.
- New: Now in Unreal with the sequencer, a CameraCut will be created automatically if the Blender scene does not contain a Marker.
- New: It is possible to change the name of the import script for Unreal.
- New: Import script updated for 4.21.
- New: Choose version value removed (is now automatic).
- New: You can choose bAutoGenerateCollision for Import Script.
- Change: It is now no longer necessary to create a new sequencer in Unreal Engine for import from Blender, the script will create it itself.
- Change: The potential error report contains more details to correct the errors.
- Change: New potential errors will be detected in the potential error report (marker).
- Change: Show assets button report contains more information and is clearer.
- Change: In the Export log, the NLA types, poses, and actions are indicated as animations.
- Change: Export_pose check mark removed (now only one check mark for all animation types).
- Change: Hierarchy names are automatically updated with each collisions conversion.
- Fixed: Export action doesn't work with NLA Change.
- Fixed: Unable to fix the object that is not in a visible layer.
- Fixed: The potential error display showed some errors in duplicate.
- Fixed: Reload importlib did not work well.
- Fixed: The generated sequencer sections are sometimes offset by one frame.
- Fixed: Some files with special names do not work with Unreal import, so the name is now corrected directly at Blender export.
- Fixed: The camera cut sections are too long by 0.0001 frames.
- Fixed: UpdateNameHierarchy makes bad parent_set with the ConvertToUe4SubObj function.
- Fixed: ResetArmaturePose function doesn't work with rotation mode Euler.
- Temporary problem: Currently on Blender 2.8 the hidden objects will not be exported, use Shift+H to unhide all objects.

### Version 2.2.1
(Rev 0.2.2b before Semantic Versioning update https://semver.org)

- Change: Addon panel moved in View3D > UI > Unreal Engine 4 for Blender 2.8.
- Fixed: Select in TryToCorrectPotentialError caused an error with Blender 2.79.

### Version 2.2.2
(Rev 0.2.2c before Semantic Versioning update https://semver.org)

- Fixed: The animations have a size 100 times too small.
- Removed: All skeletal meshes are exported with the root joint named as Armature to be skipped in Unreal (this caused problems with the animations).
- Change: Hierarchy names are not automatically updated with each collisions conversion.
- Change: Hierarchy names are automatically updated with each export.

### Version 2.2.3
(Rev 0.2.2d before Semantic Versioning update https://semver.org)

- Updated class names and ID names for Blender 2.8.

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

### Version 2.3.1
(Rev 0.2.3b before Semantic Versioning update https://semver.org)

- Fixed: ImportAssetScript returns error with animation.

### Version 2.3.2
(Rev 0.2.3c before Semantic Versioning update https://semver.org)

- Change: BFU_MT_Nomenclatureresets -> BFU_MT_NomenclaturePresets.
- Change: revertExportPath is now False by default.
- Fixed: Preset export paths are wrong in Linux.

### Version 2.3.3
(Rev 0.2.3d before Semantic Versioning update https://semver.org)

- Change: Export can use custom properties (used for Metadata). You can activate this in addon preferences.
- Fixed: bpy.ops.object.showasset() causes an error with SkeletalMesh animation.
- Fixed: Exporting camera causes an error with Blender 2.7 (hide for 2.7, hide_viewport for 2.8).

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

### Version 2.4.1
(Rev 0.2.4b before Semantic Versioning update https://semver.org)

- Fixed: Button to open the last release page (GitHub) causes an error with no internet connection or when limited by proxies.

### Version 2.4.2
(Rev 0.2.4c before Semantic Versioning update https://semver.org)

- Fixed: Error with forgotten variable "originalLoc" with armature.

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

### Version 2.6.0
(Rev 0.2.6 before Semantic Versioning update https://semver.org)

- New: Option in addon preferences to correct Extrem UV Scale.
- New: You can now set the desired Skeleton root bone scale in addon preferences.
- New: You can now directly export the Blender collections.
- New: Skeleton root bone scale is now set by default to 1.
- Change: ArmatureRoot bone is auto-removed by default.
- Change: Export skeletal mesh unit size locked at 0.01.
- Fixed: Lag with Export only select option.
- Fixed: Import script doesn't set LodGroup to None if not set in Blender.
- Fixed: StaticMesh sockets add ".001" in name.
- Fixed: Linked meshes can break final export size.
- Fixed: Export action can move mesh to center.
- Fixed: RigidBody Anim Node doesn't work (Bone scale 0.01).
- Fixed: AnimDynamics Anim Node doesn't work (Bone scale 0.01).
- Fixed: CheckArmatureMultipleRoots detects non-deform bones.

### Version 2.6.1
(Rev 0.2.6.1 before Semantic Versioning update https://semver.org)

- Change: Export static mesh unit size locked at 1.0.
- Fixed: Exporting several sockets at the same time can make the script fail.
- Fixed: SocketsAdd90X doesn't use the correct rotation.

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

### Version 2.7.1
(Rev 0.2.7.1 before Semantic Versioning update https://semver.org)

- Fixed: If the "ignore NLA for actions" option is unchecked and multiple animations are exported, all exported animations will be the same one.
- Fixed: Calculated export time is not accurate with dependency cycle in rig.
- Change: Optimized export time.

### Version 2.7.2
(Rev 0.2.7.2 before Semantic Versioning update https://semver.org)

- New: Check potential error will detect if the armature has at least one deform bone.
- Change: Bake armature will bake 10 frames before and after for better animation accuracy.
- Change: The duration of the animation will be automatically corrected if it is null or negative.
- Fixed: Import script doesn't remove old LODs.
- Fixed: FocalLength doesn't use the same math from Blender to UE4.
- Fixed: Action poses are exported with a null duration (wrong for UE4).
- Fixed: If the imported animation is wrong, it causes a script error.
- Fixed: Option auto for Rescale rig will always rescale.

### Version 2.7.3
(Rev 0.2.7.3 before Semantic Versioning update https://semver.org)

- Fixed: Export fails if an object library has the same name as a real object.
- Fixed: With Unit Scale not at 0.01, if you export a SkeletalMesh and an animation at the same time, the animation can be wrong.
- Fixed: With Unit Scale not at 0.01, some constraints can make the animation wrong.
- Fixed: With Unit Scale not at 0.01, ShapeKeys are 100 times too big.
- Fixed: Bake Armature animation bakes only the current scene start to end frames.

### Version 2.7.4
(Rev 0.2.7.4 before Semantic Versioning update https://semver.org)

- Fixed: Animation created with Mixamo are not detected in auto.
- Fixed: With Unit Scale not at 0.01, if the armature scale is not equal to 1, the animation is wrong.
- Fixed: Animation bake doesn't work on all constraints.
- Change: New potential error: Check if the ARMATURE uses the same value on all scale axes.

### Version 2.7.5
(Rev 0.2.7.5 before Semantic Versioning update https://semver.org)

- HotFix: Assets import script error with 4.26, ConfigParser import changed to configparser.

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

### Version 2.9.0
(Rev 0.2.9 before Semantic Versioning update https://semver.org)

- New: You can now choose a specific Vertex Paint to use when you export.
- New: You can now choose if you use scene or armature as origin for export in SkeletalMesh animations.
- New: Manage more characters and cultures in path or file names.
- New: Camera export takes less time + new camera options in addon preferences.
- Change: The SkeletalMesh is exported with scale at 1.0.
- Change: You can use "Show Asset(s)" and "Show Action(s)" buttons to force the update of the action cache.
- Change: Remove root bone modified to Add root bone.
- Change: Auto fix the "multiple root bones" potential error when exporting.
- Fixed: Creating a new preset causes a script error.
- Fixed: Export filter "Only select and active action" doesn't work with poses.
- Fixed: The export action cache is not correctly updated.
- Fixed: In camera sequencer with some frame rates, the frame keys can be shifted.
- Fixed: Exporting SkeletalMesh without animation_data causes script failure.
- Fixed: Button "Show Asset(s)" causes script failure when the selected actor is not a SkeletalMesh.
- Fixed: Animation file with space can cause errors during import.
- Fixed: Vertex color updated only in import option when reimporting.
- Fixed: With Unit Scale not at 0.01, SkeletalMesh has a wrong scale.
- Fixed: Import NLA animation with script doesn't work.
- Fixed: With Unit Scale not at 0.01, NLA animation will not export.
- Fixed: With Unit Scale not at 0.01, Blender 2.9.1 can crash with SkeletalMesh.
- Fixed: Apply Wrong Bool Modifier causes script error.
- Fixed: Mesh with disabled Modifier causes script error.
- Fixed: Additional location in advanced properties doesn't work for the cameras.
- Fixed: Export Instanced complex Collections can break the exported mesh.
- Fixed: Camera Sequencer doesn't work in Unreal Engine 5.

### Version 3.0.0
(Rev 0.3.0 before Semantic Versioning update https://semver.org)

- New: Text generator for exporting Skeletal Mesh Sockets in Unreal Engine (Copy/Paste).
- New: ExportAsProxy and ExportProxyChild options removed; this is now automatic.
- New: Support for Alembic import with import scripts.
- Change: Additional files now use JSON.
- Fixed: Camera export doesn't work when any marker_sequences were created.
- Fixed: "Show Asset(s)" button causes script error when no object is selected.
- Fixed: Removed collision in export collision list causes script error.
- Fixed: Collision on exported Instanced Collections doesn't work.
- Fixed: Sequencer Import Script doesn't work on older versions of Unreal Engine because the Python version is not the same.
- Fixed: Var Manual Focus Distance (Focus Settings) doesn't work in Sequencer Import Script.
- Fixed: When using Proxy Armature with sockets, wrong bones with socket names are exported.
- Fixed: Camera export doesn't work when scene has no timeline_markers.
- Fixed: Export fails with animation when tweakmode is activated.
- Fixed: Lightmap resolution = 4 when exporting without custom light map.
- Fixed: SkeletalMesh LODs are imported as normal meshes.
- Fixed: Export directories with invalid characters cause script error.
- Fixed: Show collection popup causes script error.
- Fixed: Collection export doesn't use SubCollection.

### Version 3.1.0
(Rev 0.3.1 before Semantic Versioning update https://semver.org)

- New: Generated import script compatible with Python 3.9 (Unreal Engine 5).
- New: Text generator for exporting camera in Unreal Engine (Copy/Paste).
- New potential errors in the check: If you use Parent Bone to parent your mesh to your armature, the import will fail.
- You can now use Force Static Mesh and Export Deform Only options with proxy armatures.
- Naming asset updated for Unreal Engine 5.
- Fixed: GetObjExportDir removes ":" in path.
- Fixed: GetExportFullpath removes ":" in path.
- Fixed: Remove the active object if an exported collection contains a single object.
- Fixed: With Unit Scale not at 0.01, and Proxy use, animation export will fail.
- Fixed: With Unit Scale not at 0.01, and Proxy, ShapeKeysCurve scale is wrong.
- Fixed: Export camera can cause axis flipping.
- Fixed: NLA export fails when using inter frame.
- Fixed: NLA export ignores animated influence on actions.
- Fixed: Import script doesn't work with Unreal Engine 5.
- Fixed: Export doesn't work with animation from Proxy since Blender 3.2.2.

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

### Version 4.1.0
(Rev 0.4.1 before Semantic Versioning update https://semver.org)

- UI updated.
- Updated Export Button Name.
- New options to set start/end animation time with NLA.
- Fixed: ConvertGeometryNodeAttributeToUV fails after Blender 3.5.
- Fixed: Geometry To UV, Correct Extrem UV, Vertex Color, Sockets Transform, and Name don't apply on child objects.
- Fixed: Export using AutoProRig fails.

### Version 4.2.0
(Rev 0.4.2 before Semantic Versioning update https://semver.org)

- New: The addon now includes a modified version of the Blender standard FBX I/O API, instead of using the original one. (Thanks SAM-tak!)
- New: Exported models and animations now use Unreal bones coordinate by default. (Thanks SAM-tak!)
- New: Supports exporting models and animations with the Unreal Mannequin bone structure from Blender. (Thanks SAM-tak!)
- New: Supports exporting Blender's custom property animation in a format that Unreal Engine can recognize as curve data animation. (Thanks SAM-tak!)
- New: Alembic animation supports multiple unit scales and global scale.
- New: Selection filter "Only selected" and "Only selected and active action" now filters only visible objects.
- New: Modular export (export several skeletal meshes with the same skeleton).
- New: You can enable skeletal mesh per poly collision.
- New: Camera values Min and Max FStop are updated with Aperture.
- New: Support for ArchVis cameras (use of shift).
- New: Support for custom cameras (e.g., Blueprints).
- New: Support for Spline and Curves export/import.
- Faster camera export.
- Fixed: Blender 3.5 may crash during NLA export (interacting with an NlaStripFCurves not linked to an object could lead to a crash in Blender 3.5).
- Fixed: Applying skeletal export scale with Proxy and Unit Scale not set to 0.01 could result in a script error.
- Fixed: Using "Convert Attribute to UV" can swap UV indices in the exported mesh.
- Fixed: The "Export Procedure" option is visible with static meshes.
- Fixed: Hidden objects and collections are unhidden after export when using the same name.
- Fixed: Skeletons imported with skeletal meshes use incorrect names.
- Fixed: Collection.exclude is not recovered after export when using multi view layers.
- Fixed: Camera import script doesn’t work in Unreal Engine 5.3.
- Fixed: Export collections produce UI script fail.
- Fixed: Camera FBX is not exported when bfu_export_fbx_camera == True.
- Fixed: Show Asset To Export button produces script fail.
- Fixed: Curve mesh is duplicated during export.
- Fixed: Script fail in Blender 4.0 when switching to global view.
- Fixed: UI script fail in Blender 2.9.
- Fixed: Camera scale impacts the focus distance.

### Version 4.3.0
(Rev 0.4.3 before Semantic Versioning update https://semver.org)

- New: Update for Blender 4.2.
- New: Orthographic camera support for copy/paste cameras.
- New: Disable render simplify during export to not lose subdivisions and mesh optimizations.
- New: Potential error and auto-fix for frame rate denominator and numerator.
- New: Option to set use_space_transform at export.
- New: Button to fix extreme UV scales in Tools > UV Map.
- New: New materials option for importing FBX files into Unreal.
- New: New options to create subfolders with the object name for Alembic and SkeletalMesh (used to avoid asset conflicts during export).
- New: Support for color types in Vertex Colors export.
- New: FBX Addon generator (for custom edits on the FBX Addon).
- New: Better FBX management for older versions.
- Change: "Convert Attribute to UV" is False by default.
- Change: Updated panel names to avoid confusion with other add-on panels in the Unreal Engine tab.
- Fixed: Import sequencer script fails for Unreal 5.0 and older versions (SequencerBindingProxy renamed to MovieSceneBindingProxy).
- Fixed: Import sequencer script fails if the camera is not a cinematic camera.
- Fixed: Import sequencer script fails if custom camera class is not found.
- Fixed: Imported camera sequencer does not have the same name in the level scene.
- Fixed: Armature child objects with inverse parent lost their transform positions if rescaled during export.
- Fixed: With Unit Scale not at 0.01, shape keys that are not location context are rescaled.
- Fixed: When rescaling the rig at export, all the drivers that were set were gone.
- Fixed: Camera scale does not use display size in camera data.
- Fixed: Check Potential Errors does not fix Hierarchy names with Sockets and Collisions.
- Fixed: Default export file paths are wrong.
- Fixed: Addon export checks "Convert Attribute to UV" and its "Attribute name" on the wrong object.
- Fixed: custom_export_name option does not work.

### Version 4.3.1

- New: Update versioning to use Semantic Versioning 2.0.0 (https://semver.org).
- Fixed: Export applies modifiers that are hidden in the viewport.
- Fixed: Addon fails to get path when installed in custom script directories.
- Fixed: Addon fails to get version and path when installed as an extension (default in Blender 4.2).
