# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

import bpy
import fnmatch
from .. import bbpl
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_unreal_utils


def IsACollision(obj):
    '''
    Retrun True is object is an Collision.
    https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/FBX/StaticMeshes/#collision
    '''
    if obj.type == "MESH":
        cap_name = obj.name.upper()
        if cap_name.startswith("UBX_"):
            return True
        elif cap_name.startswith("UCP_"):
            return True
        elif cap_name.startswith("USP_"):
            return True
        elif cap_name.startswith("UCX_"):
            return True

    return False

def get_all_collision_objs(objs_list=None):
    # Get any collision objects from bpy.context.scene.objects or list if valid.

    if objs_list is not None:
        objs = objs_list
    else:
        objs = bpy.context.scene.objects

    collision_objs = [obj for obj in objs if (
        fnmatch.fnmatchcase(obj.name, "UBX*") or
        fnmatch.fnmatchcase(obj.name, "UCP*") or
        fnmatch.fnmatchcase(obj.name, "USP*") or
        fnmatch.fnmatchcase(obj.name, "UCX*")
        )]
    return collision_objs

def fix_export_type_on_collision(list=None):
    # Corrects bad properties

    if list is not None:
        objs = list
    else:
        objs = get_all_collision_objs()

    fixed_collisions = 0
    for obj in objs:
        if obj.bfu_export_type == "export_recursive":
            obj.bfu_export_type = "auto"
            fixed_collisions += 1
    return fixed_collisions

def fix_name_on_collision(list=None):
    # Updates hierarchy names
    if list is not None:
        objs = list
    else:
        objs = get_all_collision_objs()

    fixed_collision_names = 0
    for obj in objs:
        if fnmatch.fnmatchcase(obj.name, "UBX*"):
            update_length = update_collision_names("Box", [obj])
            fixed_collision_names += update_length
        if fnmatch.fnmatchcase(obj.name, "UCP*"):
            update_length = update_collision_names("Capsule", [obj])
            fixed_collision_names += update_length
        if fnmatch.fnmatchcase(obj.name, "USP*"):
            update_length = update_collision_names("Sphere", [obj])
            fixed_collision_names += update_length
        if fnmatch.fnmatchcase(obj.name, "UCX*"):
            update_length = update_collision_names("Convex", [obj])
            fixed_collision_names += update_length
    return fixed_collision_names
    
def update_collision_names(SubType, objList):
    # Update collision names for Unreal Engine.
    
    update_length = 0
    for obj in objList:
        ownerObj = obj.parent

        if ownerObj is not None:
            if obj != ownerObj:

                # SkeletalMesh Colider
                if obj.type == 'MESH':

                    # Set the name of the Prefix depending
                    # on the type of collision in agreement
                    # with unreal FBX Pipeline

                    if SubType == "Box":
                        prefixName = "UBX_"
                    elif SubType == "Capsule":
                        prefixName = "UCP_"
                    elif SubType == "Sphere":
                        prefixName = "USP_"
                    elif SubType == "Convex":
                        prefixName = "UCX_"

                    new_name = bfu_unreal_utils.generate_name_for_unreal_engine(prefixName+ownerObj.name, obj.name)
                    if new_name != obj.name:
                        obj.name = new_name 
                        update_length += 1
    return update_length

def Ue4SubObj_set(SubType):
    # Convect obj to Unreal Engine sub objects Collisions Shapes

    def DeselectAllWithoutActive():
        for obj in bpy.context.selected_objects:
            if obj != bpy.context.active_object:
                obj.select_set(False)

    ownerObj = bpy.context.active_object
    objList = bpy.context.selected_objects
    if ownerObj is None:
        return []

    ConvertedObjs = []

    for obj in objList:
        DeselectAllWithoutActive()
        obj.select_set(True)
        if obj != ownerObj:

            # SkeletalMesh Colider
            if obj.type == 'MESH':
                bfu_basics.ConvertToConvexHull(obj)
                obj.modifiers.clear()
                obj.data.materials.clear()
                obj.active_material_index = 0
                obj.data.materials.append(CreateCollisionMaterial())

                # Set the name of the Prefix depending on the
                # type of collision in agreement with unreal FBX Pipeline
                if SubType == "Box":
                    prefixName = "UBX_"
                elif SubType == "Capsule":
                    prefixName = "UCP_"
                elif SubType == "Sphere":
                    prefixName = "USP_"
                elif SubType == "Convex":
                    prefixName = "UCX_"

                obj.name = bfu_unreal_utils.generate_name_for_unreal_engine(prefixName+ownerObj.name, obj.name)
                obj.show_wire = True
                obj.show_transparent = True
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                ConvertedObjs.append(obj)

    DeselectAllWithoutActive()
    for obj in objList:
        obj.select_set(True)  # Resets previous selected object
    return ConvertedObjs

def CreateCollisionMaterial():
    addon_prefs = bfu_basics.GetAddonPrefs()

    mat = bpy.data.materials.get("UE4Collision")
    if mat is None:
        mat = bpy.data.materials.new(name="UE4Collision")

    mat.diffuse_color = addon_prefs.collisionColor
    mat.use_nodes = False
    if bpy.context.scene.render.engine == 'CYCLES':
        # sets up the nodes to create a transparent material
        # with GLSL mat in Cycle
        mat.use_nodes = True
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (0, 0)
        mix = nodes.new('ShaderNodeMixShader')
        mix.location = (-200, 000)
        mix.inputs[0].default_value = (0.95)
        diff = nodes.new('ShaderNodeBsdfDiffuse')
        diff.location = (-400, 100)
        diff.inputs[0].default_value = (0, 0.6, 0, 1)
        trans = nodes.new('ShaderNodeBsdfTransparent')
        trans.location = (-400, -100)
        trans.inputs[0].default_value = (0, 0.6, 0, 1)
        node_tree.links.new(diff.outputs['BSDF'], mix.inputs[1])
        node_tree.links.new(trans.outputs['BSDF'], mix.inputs[2])
        node_tree.links.new(mix.outputs['Shader'], out.inputs[0])
    return mat