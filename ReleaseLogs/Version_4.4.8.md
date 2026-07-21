# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.8
Fixed: Socket UI use the wrong value and produice script warning in the console.
    (Case issue: bfu_socket_custom_Name -> bfu_socket_custom_name)
Fixed: Durring export child objects may change their position.
    (reparenting of duplicated objects may change the object position because of inverse transform.)
