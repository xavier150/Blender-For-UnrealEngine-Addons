# Unreal Engine Assets Exporter - Release Log
Release Logs: https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Release-Logs

### Version 4.4.8
- New: Skeletal Mesh Socket clipboard is now ordered by socket name.
- Changed: Better UI for collision and socket in Tools panel.
- Fixed: Socket UI uses the wrong value and produces script warning in the console.
    (Case issue: bfu_socket_custom_Name -> bfu_socket_custom_name)
- Fixed: During export child objects may change their position.
    (reparenting of duplicated objects may change the object position because of inverse transform.)
- Fixed: Static Mesh Socket transforms are wrong with gltf exports.
    (I added fix for FBX export transform but gltf export should not use that fix or it will produce wrong transform.)
- Fixed: Skeletal Mesh Socket transform is wrong with fbx exports when unit scale is not 0.01.
    (The Copy Skeletal Mesh socket button doesn't apply spacing rescale)