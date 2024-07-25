# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

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