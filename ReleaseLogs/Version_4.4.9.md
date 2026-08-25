# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.9
- New: Better feedback when no properties are displayed in the UI panel.
    (For example when the object is not set as exportable or for linked objects)
- Fixed: Import fail in Unreal Engine 4.27
    (Typing: old Python versions require typing.List[] instead of list[])
- Fixed: Vertex Color is not exported with the option Active Render when the active render use index 0.
    (Used "if target_index:" replaced by "if target_index is not None:")
- Fixed: Collection Static Meshes are not imported correctly in Unreal Engine.
    (Wrong asset type checking in the import script)
- Fixed: Linked objects from a same scene may not correctly exported.
    (Make Instances Real don't work if the source object is not visible in the viewport.)