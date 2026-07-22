# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.8
New: Skeletal Mesh Socket clipboard are now ordered by socket name.
Changed: Better UI for collision and socket in Tools panel.
Fixed: Socket UI use the wrong value and produice script warning in the console.
    (Case issue: bfu_socket_custom_Name -> bfu_socket_custom_name)
Fixed: Durring export child objects may change their position.
    (reparenting of duplicated objects may change the object position because of inverse transform.)
Fixed: Static Mesh Socket transforms is wrong with gltf exports.
    (I added fix for FBX export transform but gltf export should not use that fix or it will produce wrong transform.)
Fixed: Skeletal Mesh Socket transform is wrong with fbx exports when unit scale is not 0.01.
    (The Copy Skeletal Mesh socket button don't apply spacing rescale)