# Blender-For-UnrealEngine - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

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