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

# ----------------------------------------------
#  This addons allows to easily export several objects at the same time in .fbx
#  for use in unreal engine 4 by removing the usual constraints
#  while respecting UE4 naming conventions and a clean tree structure.
#  It also contains a small toolkit for collisions and sockets
#  xavierloux.com
# ----------------------------------------------


import bpy
import json
import time
import copy
import mathutils


class SavedObject():

    def __init__(self, obj):
        if obj:
            self.name = obj.name
            self.select = obj.select_get()
            self.hide_select = obj.hide_select
            self.hide_viewport = obj.hide_viewport


class SavedBones():

    def __init__(self, bone):
        if bone:
            self.name = bone.name
            self.select = bone.select
            self.hide = bone.hide


class SavedCollection():

    def __init__(self, col):
        if col:
            self.name = col.name
            self.hide_select = col.hide_select
            self.hide_viewport = col.hide_viewport


class SavedViewLayerChildren():

    def __init__(self, vlayer, childCol):
        if childCol:
            self.vlayer_name = vlayer.name
            self.name = childCol.name
            self.exclude = childCol.exclude
            self.hide_viewport = childCol.hide_viewport


class UserSceneSave():

    def __init__(self):

        # Select
        self.user_active = None
        self.user_active_name = None
        self.user_bone_active = None
        self.user_bone_active_name = None
        self.user_selected = []

        # Stats
        self.user_mode = None
        self.use_simplify = False

        # Data
        self.objects = []
        self.object_bones = []
        self.collections = []
        self.view_layers_children = []
        self.action_names = []
        self.collection_names = []

    def SaveCurrentScene(self):
        # Save data (This can take time)

        c = bpy.context
        # Select
        self.user_active = c.active_object  # Save current active object
        if self.user_active:
            self.user_active_name = self.user_active.name
        self.user_selected = c.selected_objects  # Save current selected objects

        # Stats
        if self.user_active:
            if bpy.ops.object.mode_set.poll():
                self.user_mode = self.user_active.mode  # Save current mode
        self.use_simplify = bpy.context.scene.render.use_simplify

        # Data
        for obj in bpy.data.objects:
            self.objects.append(SavedObject(obj))
        for col in bpy.data.collections:
            self.collections.append(SavedCollection(col))
        for vlayer in c.scene.view_layers:
            for childCol in vlayer.layer_collection.children:
                self.view_layers_children.append(SavedViewLayerChildren(vlayer, childCol))
        for action in bpy.data.actions:
            self.action_names.append(action.name)
        for collection in bpy.data.collections:
            self.collection_names.append(collection.name)

        # Data for armature
        if self.user_active:
            if self.user_active.type == "ARMATURE":
                if self.user_active.data.bones.active:
                    self.user_bone_active = self.user_active.data.bones.active
                    self.user_bone_active_name = self.user_active.data.bones.active.name
                for bone in self.user_active.data.bones:
                    self.object_bones.append(SavedBones(bone))

    def ResetSelectByRef(self):
        safeModeSet(bpy.ops.object, "OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:  # Resets previous selected object if still exist
            if obj in self.user_selected:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = self.user_active

        self.ResetModeAtSave()
        self.ResetBonesSelectByName()

    def ResetSelectByName(self):
        safeModeSet(bpy.ops.object, "OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        for obj in self.objects:  # Resets previous selected object if still exist
            if obj.select:
                if obj.name in bpy.data.objects:
                    bpy.data.objects[obj.name].select_set(True)

        if self.user_active_name:
            if self.user_active_name in bpy.data.objects:
                bpy.context.view_layer.objects.active = bpy.data.objects[self.user_active_name]

        self.ResetModeAtSave()
        self.ResetBonesSelectByName()

    def ResetBonesSelectByName(self):
        # Work only in pose mode!
        if len(self.object_bones) > 0:
            if self.user_active:
                if bpy.ops.object.mode_set.poll():
                    if self.user_active.mode == "POSE":
                        bpy.ops.pose.select_all(action='DESELECT')
                        for bone in self.object_bones:
                            if bone.select:
                                if bone.name in self.user_active.data.bones:
                                    self.user_active.data.bones[bone.name].select = True

                        if self.user_bone_active_name is not None:
                            if self.user_bone_active_name in self.user_active.data.bones:
                                new_active = self.user_active.data.bones[self.user_bone_active_name]
                                self.user_active.data.bones.active = new_active

    def ResetModeAtSave(self):
        if self.user_mode:
            if bpy.ops.object:
                safeModeSet(bpy.ops.object, self.user_mode)

    def ResetSceneAtSave(self):
        scene = bpy.context.scene
        self.ResetModeAtSave()

        bpy.context.scene.render.use_simplify = self.use_simplify

        # Reset hide and select (bpy.data.objects)
        for obj in self.objects:
            if obj.name in bpy.data.objects:
                if bpy.data.objects[obj.name].hide_select != obj.hide_select:
                    bpy.data.objects[obj.name].hide_select = obj.hide_select
                if bpy.data.objects[obj.name].hide_viewport != obj.hide_viewport:
                    bpy.data.objects[obj.name].hide_viewport = obj.hide_viewport
            else:
                print("/!\\ "+obj.name+" not found in bpy.data.objects")

        # Reset hide and select (bpy.data.collections)
        for col in self.collections:
            if col.name in bpy.data.collections:
                if bpy.data.collections[col.name].hide_select != col.hide_select:
                    bpy.data.collections[col.name].hide_select = col.hide_select
                if bpy.data.collections[col.name].hide_viewport != col.hide_viewport:
                    bpy.data.collections[col.name].hide_viewport = col.hide_viewport
            else:
                print("/!\\ "+col.name+" not found in bpy.data.collections")

        # Reset hide in and viewport (collections from view_layers)
        for childCol in self.view_layers_children:
            if childCol.vlayer_name in scene.view_layers:
                view_layer = scene.view_layers[childCol.vlayer_name]
                if childCol.name in view_layer.layer_collection.children:
                    layer_col_children = view_layer.layer_collection.children[childCol.name]

                    if layer_col_children.exclude != childCol.exclude:
                        layer_col_children.exclude = childCol.exclude
                    if layer_col_children.hide_viewport != childCol.hide_viewport:
                        layer_col_children.hide_viewport = childCol.hide_viewport


class UserArmatureDataSave():

    def __init__(self, armature):

        # Select
        self.armature = armature

        # Stats
        # Data
        use_mirror_x = False

    def SaveCurrentArmature(self):
        # Save data (This can take time)
        if self.armature is None:
            return
        # Select
        # Stats
        # Data
        self.use_mirror_x = self.armature.data.use_mirror_x

    def ResetArmatureAtSave(self):
        if self.armature is None:
            return

        scene = bpy.context.scene
        # Select
        # Stats
        # Data
        self.armature.data.use_mirror_x = self.use_mirror_x


def modeSetOnTarget(target_object=None, target_mode='OBJECT'):
    # Exit current mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if target_object:
        target_object.select_set(state=True)
        bpy.context.view_layer.objects.active = target_object

    # Enter new mode
    bpy.ops.object.mode_set(mode=target_mode)
    return True



def safeModeSet(obj=None, target_mode='OBJECT'):

    if obj:
        target = obj
    else:
        target = bpy.ops.object

    print("Start switch on mode {target_mode} on {target.name}")
    bpy.ops.object.mode_set(mode=target_mode)

    return True


    '''
    if target.mode != target_mode:
        if bpy.ops.object.mode_set.poll():
            # Switch object before change target mode
            if target_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode=target_mode)
            print("End switch on mode.")
            return True
        print("Fail switch on mode.")
        raise TypeError("Fail switch on mode.")
        return False
    print("End switch on mode.")
    return False
    '''


class counterTimer():

    def __init__(self):
        self.start = time.perf_counter()

    def ResetTime(self):
        self.start = time.perf_counter()

    def GetTime(self):
        return time.perf_counter()-self.start


def jsonList(string):
    if string is None:
        return []
    if string == "":
        return []

    jdata = json.loads(string)
    List = []
    for d in jdata:
        # for value in d.iteritems():
        List.append(d)
    return List


def clearDriverVar(d):
    for var in d.variables:
        d.variables.remove(var)


def updateBoneRotMode(armature, boneName, rotation_mode):
    armature.pose.bones[boneName].rotation_mode = rotation_mode


def GetControlerToSwitch(Bones):
    # Fk and Ik copntroler
    controlerList = []
    for bone in Bones:
        for item in list(bone.items()):
            if item[0] == "IkBlend":
                controlerList.append(bone)
    return controlerList


def GetVisualBonePos(obj, Bone):
    matrix_Pose = obj.matrix_world @ Bone.matrix
    loc = matrix_Pose @ mathutils.Vector((0, 0, 0))
    rot = matrix_Pose.to_euler()
    scale = Bone.scale
    return((loc, rot, scale))


def GetVisualBonesPosPacked(obj, TargetBones):
    PositionList = []
    for bone in TargetBones:
        loc = GetVisualBonePos(obj, bone)[0]
        rot = GetVisualBonePos(obj, bone)[1]
        scale = GetVisualBonePos(obj, bone)[2]
        PositionList.append((bone.name, loc, rot, scale))
    return PositionList


def ApplyRealMatrixWorldBones(bone, obj, matrix):
    for cons in bone.constraints:
        if cons.type == "CHILD_OF":
            if not cons.mute:
                if cons.target is not None:
                    Child = cons.inverse_matrix
                    if cons.target.type == "ARMATURE":
                        par = obj.matrix_world @ obj.pose.bones[cons.subtarget].matrix
                    else:
                        par = cons.target.matrix_world
                    bone.matrix = obj.matrix_world.inverted() @ (Child.inverted() @ par.inverted() @ matrix)
                    return
    bone.matrix = obj.matrix_world.inverted() @ matrix


def SetVisualBonePos(obj, Bone, loc, rot, scale, UseLoc, UseRot, UseScale):
    # Save
    BaseLoc = copy.deepcopy(Bone.location)
    BaseScale = copy.deepcopy(Bone.scale)
    RotModeBase = copy.deepcopy(Bone.rotation_mode)
    # Bone.rotation_mode = 'XYZ'
    BaseRot = copy.deepcopy(Bone.rotation_euler)
    # ApplyPos
    mat_loc = mathutils.Matrix.Translation(loc)
    mat_rot = rot.to_matrix().to_4x4()
    matrix = mat_loc @ mat_rot
    ApplyRealMatrixWorldBones(Bone, obj, matrix)
    Bone.scale = scale
    # ResetNotDesiredValue
    if not UseLoc:
        Bone.location = BaseLoc
    if not UseRot:
        Bone.rotation_euler = BaseRot
    if not UseScale:
        Bone.scale = BaseScale
    # Bone.rotation_mode = RotModeBase


def FindItemInListByName(item, list):
    for TargetItem in list:
        if TargetItem.name == item:
            return TargetItem
    return None


def SetVisualBonesPosPacked(obj, TargetBones, PositionList, UseLoc, UseRot, UseScale):

    for pl in PositionList:
        TargetBone = FindItemInListByName(pl[0], TargetBones)
        if TargetBone is not None:
            loc = mathutils.Vector(pl[1])
            rot = mathutils.Euler(pl[2], 'XYZ')
            scale = mathutils.Vector(pl[3])
            SetVisualBonePos(obj, TargetBone, loc, rot, scale, UseLoc, UseRot, UseScale)


def GetDirectControledBonesBySwitch(armature, controlerBone):
    # Recuperre uniquement les os qui sont directement controler
    bones = []

    def GetIfTarget(targets):
        for target in targets:
            if target.data_path.split('"')[3] == "IkBlend":
                if target.data_path.split('"')[1] == controlerBone.name:
                    return True

        return False
    if armature.animation_data is not None:
        for driver in armature.animation_data.drivers:
            if '"].constraints["' in driver.data_path and "IkBlend" in driver.driver.expression:
                for var in driver.driver.variables:
                    if GetIfTarget(var.targets):
                        bones.append(armature.pose.bones[driver.data_path.split('"')[1]])
    return bones


def GetControledBonesBySwitch(armature, controlerBone):
    def GetRecursifParent(MaxIndex, Bones):
        if MaxIndex > len(Bones):
            Bones.append(Bones[-1].parent)
            return GetRecursifParent(MaxIndex, Bones)
        else:
            return Bones
    # Recuperre tout les os qui sont controler directement ou indeirectement
    bones = GetDirectControledBonesBySwitch(armature, controlerBone)
    returnBone = bones.copy()
    for bone in bones:
        for const in bone.constraints:
            if const.type == "IK":
                returnBone += GetRecursifParent(const.chain_count-1, [bone.parent])

    return returnBone


def getSafeCollection(collection_name):
    # Found or create collection.
    if collection_name in bpy.data.collections:
        myCol = bpy.data.collections[collection_name]
    else:
        myCol = bpy.data.collections.new(collection_name)
    return myCol


def getRecursiveLayerCollection(layer_collection):
    # Get all recursive childs of a object

    all_childs = []
    for child in layer_collection.children:
        all_childs.append(child)
        all_childs += getRecursiveLayerCollection(child)
    return all_childs


def setCollectionExclude(collection, exclude):
    scene = bpy.context.scene
    for vl in scene.view_layers:
        for layer in getRecursiveLayerCollection(vl.layer_collection):
            if layer.collection == collection:
                layer.exclude = exclude


def getRigCollection(armature, col_type="RIG"):
    rig_col = getSafeCollection(armature.users_collection[0].name)

    if col_type == "RIG":
        return rig_col
    elif col_type == "SHAPE":
        shape_Col = getSafeCollection(armature.name+"_RigShapes")
        if shape_Col.name not in rig_col.children:
            rig_col.children.link(shape_Col)
        return shape_Col
    elif col_type == "CURVE":
        shape_Col = getSafeCollection(armature.name+"_RigCurves")
        if shape_Col.name not in rig_col.children:
            rig_col.children.link(shape_Col)
        return shape_Col
    elif col_type == "CAMERA":
        shape_Col = getSafeCollection(armature.name+"_RigCameras")
        if shape_Col.name not in rig_col.children:
            rig_col.children.link(shape_Col)
        return shape_Col
    else:
        print("In getRigCollection() "+col_type+" not found!")


def getVertexColors(obj):
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes
    else:
        return obj.data.vertex_colors


def getVertexColors_RenderColorIndex(obj):
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.render_color_index
    else:
        for index, vertex_color in enumerate(obj.data.vertex_colors):
            if vertex_color.active_render:
                return index


def getVertexColor_ActiveColorIndex(obj):
    if bpy.app.version >= (3, 2, 0):
        return obj.data.color_attributes.active_color_index
    else:
        return obj.data.vertex_colors.active_index


def getLayerCollectionsRecursive(layer_collection):
    layer_collections = []
    layer_collections.append(layer_collection)  # Add curent
    for child_col in layer_collection.children:
        layer_collections.extend(getLayerCollectionsRecursive(child_col))  # Add childs recursive

    return layer_collections
