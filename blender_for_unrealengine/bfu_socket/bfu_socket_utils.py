# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
import math
import mathutils
from typing import List, Any, Dict, Tuple
from .bfu_socket_types import SocketType
from . import bfu_socket_props
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_unreal_utils
from .. import bfu_export_control
from .. import bfu_addon_prefs
from .. import bfu_skeletal_mesh
from ..bfu_skeletal_mesh.bfu_export_procedure import BFU_SkeletonExportProcedure



def is_a_socket(obj: bpy.types.Object) -> bool:
    '''
    Retrun True is object is an Socket.
    https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/FBX/StaticMeshes/#sockets
    '''
    prefix_list: List[str] = SocketType.get_prefix_list()

    if obj.data is None and obj.type == 'EMPTY':
        if obj.name.startswith(tuple(prefix_list)):
            return True
    return False

def get_socket_desired_children(target_obj: bpy.types.Object) -> List[bpy.types.Object]:
    sockets: List[bpy.types.Object] = []
    for obj in bfu_utils.get_export_desired_childs(target_obj):
        if is_a_socket(obj):
            sockets.append(obj)

    return sockets

def set_sockets_export_name(socket: bpy.types.Object) -> str:
    '''
    Get the current socket custom name
    '''
    if bfu_socket_props.get_object_use_socket_custom_Name(socket):
        return bfu_socket_props.get_object_socket_custom_Name(socket)
    return socket.name[7:]

def get_skeletal_mesh_socket_data(obj: bpy.types.Object) -> List[Dict[str, Any]]:

    if not isinstance(obj.data, bpy.types.Armature):
        return []

    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    sockets: List[bpy.types.Object] = []

    for socket in get_socket_desired_children(obj):
        sockets.append(socket)

    socket_data: List[Dict[str, Any]] = []
    # config.set('Sockets', '; SocketName, BoneName, Location, Rotation, Scale')

    for socket in sockets:
        socket_parent = socket.parent

        if socket_parent is None:
            print("Socket ", socket.name, " parent is None!")
            break
        if not isinstance(socket_parent.data, bpy.types.Armature):
            print("Socket parent", socket_parent.name, " parent is not an Armature!")
            break

        if bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_object_export_deform_only(socket_parent):
            b = bfu_basics.get_first_deform_bone_parent(socket_parent.data.bones[socket.parent_bone])
        else:
            b = socket_parent.data.bones[socket.parent_bone]

        bbpl.anim_utils.reset_armature_pose(socket_parent)
        # GetRelativePosition
        bml: mathutils.Matrix = b.matrix_local  # Bone
        am: mathutils.Matrix = socket_parent.matrix_world  # Armature
        em: mathutils.Matrix = socket.matrix_world  # Socket
        
        
        object_export_procedure: BFU_SkeletonExportProcedure = bfu_skeletal_mesh.bfu_export_procedure.get_object_export_procedure(obj)

        # Calculate relative matrix depending on the export procedure
        if object_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_GLTF.value:
            RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
            RelativeMatrix = mathutils.Matrix.Rotation(math.radians(90), 4, 'X') @ RelativeMatrix
        elif object_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_FBX.value:
            RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
        elif object_export_procedure.value == BFU_SkeletonExportProcedure.CUSTOM_FBX_EXPORT.value:
            RelativeMatrix = (bml.inverted() @ am.inverted() @ em)
            RelativeMatrix = mathutils.Matrix.Rotation(math.radians(90), 4, 'Y') @ RelativeMatrix
            RelativeMatrix = mathutils.Matrix.Rotation(math.radians(-90), 4, 'Z') @ RelativeMatrix
        else:
            raise ValueError("Unknown export procedure")
        
        # Decompose matrix
        t = RelativeMatrix.to_translation()
        r = RelativeMatrix.to_euler()
        s = socket.scale*addon_prefs.skeletal_sockets_imported_size

        # Convert to array for Json and apply final change of axis
        if object_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_GLTF.value:
            array_location: List[float] = [t[0]*100, t[1]*-100, t[2]*100]
            array_rotation: List[float] = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]
            array_scale: List[float] = [s[0], s[1], s[2]]
        elif object_export_procedure.value == BFU_SkeletonExportProcedure.STANDARD_FBX.value:
            array_location: List[float] = [t[0], t[1]*-1, t[2]]
            array_rotation: List[float] = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]
            array_scale: List[float] = [s[0], s[1], s[2]]
        elif object_export_procedure.value == BFU_SkeletonExportProcedure.CUSTOM_FBX_EXPORT.value:
            array_location: List[float] = [t[0], t[1]*-1, t[2]]
            array_rotation: List[float] = [math.degrees(r[0]), math.degrees(r[1])*-1, math.degrees(r[2])*-1]
            array_scale = [s[0], s[1], s[2]]
        else:
            raise ValueError("Unknown export procedure")



        MySocket: Dict[str, Any] = {}
        MySocket["SocketName"] = set_sockets_export_name(socket)
        MySocket["BoneName"] = b.name.replace('.', '_')
        MySocket["Location"] = array_location
        MySocket["Rotation"] = array_rotation
        MySocket["Scale"] = array_scale
        socket_data.append(MySocket)

    return socket_data

def get_all_scene_socket_objs() -> List[bpy.types.Object]:
    # Get any socket objects from bpy.context.scene.objects or List if valid.
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    
    objs = scene.objects
    prefix_list: List[str] = SocketType.get_prefix_list()

    socket_objs: List[bpy.types.Object] = []
    for obj in objs:
        if obj.data is None and obj.type == 'EMPTY':
            if obj.name.startswith(tuple(prefix_list)):
                socket_objs.append(obj)
    
    return socket_objs

def fix_scene_socket_export_type() -> int:
    # Corrects bad properties
    objs = get_all_scene_socket_objs()
    return fix_socket_export_type(objs)

def fix_socket_export_type(obj_list: List[bpy.types.Object]) -> int:
    # Corrects bad properties
    fixed_sockets = 0
    for obj in obj_list:
        if bfu_export_control.bfu_export_control_utils.is_export_self(obj):
            bfu_export_control.bfu_export_control_utils.set_auto(obj)
            fixed_sockets += 1
    return fixed_sockets

def fix_scene_socket_names() -> int:
    # Updates hierarchy names
    objs: List[bpy.types.Object] = get_all_scene_socket_objs()
    return fix_socket_names(objs)

def fix_socket_names(obj_List: List[bpy.types.Object]) -> int:
    fixed_socket_names: int = 0
    for obj in obj_List:
        for member in SocketType:
            if obj.name.startswith(member.get_unreal_engine_prefix()):
                update_length = update_socket_names(member, [obj])
                fixed_socket_names += update_length

    return fixed_socket_names

def update_socket_names(socket_type: SocketType, objList: List[bpy.types.Object]) -> int:
    # Update socket names for Unreal Engine.

    update_length: int = 0
    for obj in objList:
        ownerObj = obj.parent

        if ownerObj is not None:
            if obj != ownerObj:
                if obj.data is None and obj.type == 'EMPTY':
                    # StaticMesh Socket
                    if socket_type.value == SocketType.STATIC_SOCKET.value:
                        if ownerObj.type == 'MESH':
                            if not is_a_socket(obj):
                                new_name = bfu_unreal_utils.generate_name_for_unreal_engine("SOCKET_"+obj.name, obj.name)
                                if new_name != obj.name:
                                    obj.name = new_name 
                                    update_length += 1

                    # SkeletalMesh Socket
                    if socket_type.value == SocketType.SKELETAL_SOCKET.value:
                        if ownerObj.type == 'ARMATURE':
                            if not is_a_socket(obj):
                                new_name = bfu_unreal_utils.generate_name_for_unreal_engine("SOCKET_"+obj.name, obj.name)
                                if new_name != obj.name:
                                    obj.name = new_name 
                                    update_length += 1
    return update_length

def fix_scene_sockets() -> Tuple[int, int]:
    objs: List[bpy.types.Object] = get_all_scene_socket_objs()
    fixed_sockets_export = fix_socket_export_type(objs)
    fixed_socket_names = fix_socket_names(objs)
    return fixed_sockets_export, fixed_socket_names

def convert_to_unrealengine_socket(
    socket_owner: bpy.types.Object, 
    objs_to_convert: List[bpy.types.Object], 
    socket_type: SocketType
) -> List[bpy.types.Object]:
    # Convert objects to Unreal Engine Sockets

    def deselect_all_except_active() -> None:
        if bpy.context.selected_objects:
            for obj in bpy.context.selected_objects:
                if obj != bpy.context.active_object:
                    obj.select_set(False)

    converted_objs: List[bpy.types.Object] = []

    for obj in objs_to_convert:
        deselect_all_except_active()
        obj.select_set(True)
        if obj != socket_owner:
            if obj.data is None and obj.type == 'EMPTY':

                # StaticMesh Socket
                if socket_type.value == SocketType.STATIC_SOCKET.value:
                    if isinstance(socket_owner.data, bpy.types.Mesh):
                        if is_a_socket(obj):
                            # Update the name if needed
                            obj.name = bfu_unreal_utils.generate_name_for_unreal_engine(obj.name, obj.name)
                        else:
                            # Set a new name using the owner name as reference
                            obj.name = bfu_unreal_utils.generate_name_for_unreal_engine("SOCKET_"+socket_owner.name, obj.name)
                        bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)
                        converted_objs.append(obj)

                # SkeletalMesh Socket
                if socket_type.value == SocketType.SKELETAL_SOCKET.value:
                    if isinstance(socket_owner.data, bpy.types.Armature):
                        if is_a_socket(obj):
                            # Update the name if needed
                            obj.name = bfu_unreal_utils.generate_name_for_unreal_engine(obj.name, obj.name)
                        else:
                            # Set a new name using the owner name as reference
                            obj.name = bfu_unreal_utils.generate_name_for_unreal_engine("SOCKET_"+socket_owner.name, obj.name)
                        bpy.ops.object.parent_set(type='BONE',keep_transform=True)
                        converted_objs.append(obj)

    deselect_all_except_active()
    for obj in objs_to_convert:
        obj.select_set(True)  # Resets previous selected object
    return converted_objs

def convert_select_to_unrealengine_socket(socket_type: SocketType) -> List[bpy.types.Object]:
    # Convert selected objects to Unreal Engine Sockets

    if bpy.context.selected_objects is None:
        print("No selected objects found!")
        return []
    if bpy.context.active_object is None:
        print("No active object found!")
        return []
    if len(bpy.context.selected_objects) < 2:
        print("Please select two objects. (Active object is the owner of the collision)")
        return []
    
    # Convert sequence to list.
    return convert_to_unrealengine_socket(bpy.context.active_object, list(bpy.context.selected_objects), socket_type)

def get_import_skeletal_mesh_socket_script_command(obj: bpy.types.Object) -> str:

    if obj and isinstance(obj.data, bpy.types.Armature):
        sockets = get_skeletal_mesh_socket_data(obj)
        t = "SocketCopyPasteBuffer" + "\n"
        t += "NumSockets=" + str(len(sockets)) + "\n"
        t += "IsOnSkeleton=1" + "\n"
        for socket in sockets:
            t += "Begin Object Class=/Script/Engine.SkeletalMeshSocket" + "\n"
            t += "\t" + 'SocketName="' + socket["SocketName"] + '"' + "\n"
            t += "\t" + 'BoneName="' + socket["BoneName"] + '"' + "\n"
            loc = socket["Location"]
            r = socket["Rotation"]
            s = socket["Scale"]
            t += "\t" + 'RelativeLocation=' + "(X="+str(loc[0])+",Y="+str(loc[1])+",Z="+str(loc[2])+")" + "\n"
            t += "\t" + 'RelativeRotation=' + "(Pitch="+str(r[1])+",Yaw="+str(r[2])+",Roll="+str(r[0])+")" + "\n"
            t += "\t" + 'RelativeScale=' + "(X="+str(s[0])+",Y="+str(s[1])+",Z="+str(s[2])+")" + "\n"
            t += "End Object" + "\n"
        return t
    return "Please select an armature."