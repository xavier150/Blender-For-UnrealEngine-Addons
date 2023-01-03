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
import time
import math

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_export_get_info" in locals():
        importlib.reload(bfu_export_get_info)

from .. import bfu_write_text
from .. import bfu_basics
from ..bfu_basics import *
from .. import bfu_utils
from ..bfu_utils import *
from ..bbpl import utils

from . import bfu_export_get_info
from .bfu_export_get_info import *

dup_temp_name = "BFU_Temp"  # DuplicateTemporarilyNameForUe4Export
Export_temp_preFix = "_ESO_Temp"  # _ExportSubObject_TempName


def GetExportFullpath(dirpath, filename):
    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    return os.path.join(absdirpath, filename)


def ApplyProxyData(obj):

    # Apply proxy data if needed.
    if GetExportProxyChild(obj) is not None:

        def ReasignProxySkeleton(newArmature, oldArmature):
            for select in bpy.context.selected_objects:
                if select.type == "CURVE":
                    for mod in select.modifiers:
                        if mod.type == "HOOK":
                            if mod.object == oldArmature:
                                matrix_inverse = mod.matrix_inverse.copy()
                                mod.object = newArmature
                                mod.matrix_inverse = matrix_inverse

                else:
                    for mod in select.modifiers:
                        if mod.type == 'ARMATURE':
                            if mod.object == oldArmature:
                                mod.object = newArmature

            for bone in newArmature.pose.bones:
                for cons in bone.constraints:
                    if hasattr(cons, 'target'):
                        if cons.target == oldArmature:
                            cons.target = newArmature
                        else:
                            ChildProxyName = (
                                cons.target.name +
                                "_UEProxyChild"
                            )
                            if ChildProxyName in bpy.data.objects:
                                cons.target = bpy.data.objects[ChildProxyName]

        # Get old armature in selected objects
        OldProxyChildArmature = None
        for selectedObj in bpy.context.selected_objects:
            if selectedObj != obj:
                if selectedObj.type == "ARMATURE":
                    OldProxyChildArmature = selectedObj

        # Reasing parent + add to remove
        if OldProxyChildArmature is not None:
            ToRemove = []
            ToRemove.append(OldProxyChildArmature)
            for selectedObj in bpy.context.selected_objects:
                if selectedObj != obj:
                    if selectedObj.parent == OldProxyChildArmature:
                        # Reasing parent and keep position
                        SavedPos = selectedObj.matrix_world.copy()
                        selectedObj.name += "_UEProxyChild"
                        selectedObj.parent = obj
                        selectedObj.matrix_world = SavedPos
                    else:
                        ToRemove.append(selectedObj)
            ReasignProxySkeleton(obj, OldProxyChildArmature)
            SavedSelect = GetCurrentSelection()
            RemovedObjects = CleanDeleteObjects(ToRemove)
            SavedSelect.RemoveFromListByName(RemovedObjects)
            SetCurrentSelection(SavedSelect)


def BakeArmatureAnimation(armature, frame_start, frame_end):
    # Change to pose mode
    SavedSelect = GetCurrentSelection()
    bpy.ops.object.select_all(action='DESELECT')
    SelectSpecificObject(armature)
    bpy.ops.nla.bake(
        frame_start=frame_start-10,
        frame_end=frame_end+10,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        use_current_action=False,
        bake_types={'POSE'}
        )
    bpy.ops.object.select_all(action='DESELECT')
    SetCurrentSelection(SavedSelect)


def DuplicateSelectForExport(new_name="duplicated Obj"):
    # Note: Need look for a optimized duplicate, This is too long

    scene = bpy.context.scene

    class DuplicateData():
        def __init__(self):
            self.data_to_remove = []
            self.origin_select = None
            self.duplicate_select = None

        def SetOriginSelect(self):
            select = UserSelectSave()
            select.SaveCurrentSelect()
            self.origin_select = select

        def SetDuplicateSelect(self):
            select = UserSelectSave()
            select.SaveCurrentSelect()
            self.duplicate_select = select

    class DelegateOldData():
        # contain a data to remove and function for remove

        def __init__(self, data_name, data_type):
            self.data_name = data_name
            self.data_type = data_type

        def RemoveData(self):
            RemoveUselessSpecificData(self.data_name, self.data_type)

    duplicate_data = DuplicateData()
    duplicate_data.SetOriginSelect()
    for user_selected in duplicate_data.origin_select.user_selecteds:
        if user_selected:
            SaveObjCurrentName(user_selected)
            if user_selected.type == "ARMATURE":
                SetObjProxyData(user_selected)

    data_to_remove = []

    # Save action befor export
    actionNames = []
    for action in bpy.data.actions:
        actionNames.append(action.name)

    bpy.ops.object.duplicate()

    # Save the name for found after "Make Instances Real"
    currentSelectNames = []
    for currentSelectName in bpy.context.selected_objects:
        currentSelectNames.append(currentSelectName.name)

    for objSelect in currentSelectNames:
        if objSelect not in bpy.context.selected_objects:
            bpy.data.objects[objSelect].select_set(True)

    # Make sigle user and clean useless data.
    for objScene in bpy.context.selected_objects:
        if objScene.data is not None:
            oldData = objScene.data.name
            objScene.data = objScene.data.copy()
            data_to_remove.append(DelegateOldData(oldData, objScene.type))

    # Clean create actions by duplication
    for action in bpy.data.actions:
        if action.name not in actionNames:
            bpy.data.actions.remove(action)

    duplicate_data.SetDuplicateSelect()

    return duplicate_data


def SetDuplicateNameForExport(duplicate_data, origin_prefix="or_"):
    for user_selected in duplicate_data.origin_select.user_selecteds:
        user_selected.name = origin_prefix+user_selected.name

    for user_selected in duplicate_data.duplicate_select.user_selecteds:
        user_selected.name = GetObjOriginName(user_selected)


def ResetDuplicateNameAfterExport(duplicate_data):
    for user_selected in duplicate_data.origin_select.user_selecteds:
        user_selected.name = GetObjOriginName(user_selected)
        ClearObjOriginNameVar(user_selected)


def MakeSelectVisualReal():
    select = UserSelectSave()
    select.SaveCurrentSelect()

    # Save object list
    previous_objects = []
    for obj in bpy.data.objects:
        previous_objects.append(obj)

    # Visual Transform Apply
    bpy.ops.object.visual_transform_apply()

    # Make Instances Real
    bpy.ops.object.duplicates_make_real(
        use_base_parent=True,
        use_hierarchy=True
        )

    select.ResetSelectByName()

    # Select the new objects
    for obj in bpy.data.objects:
        if obj not in previous_objects:
            obj.select_set(True)


def SetSocketsExportTransform(obj):
    # Set socket scale for Unreal

    addon_prefs = GetAddonPrefs()
    for socket in GetSocketDesiredChild(obj):
        if GetShouldRescaleSocket():
            socket.delta_scale *= GetRescaleSocketFactor()

        if addon_prefs.staticSocketsAdd90X:
            savedScale = socket.scale.copy()
            savedLocation = socket.location.copy()
            AddMat = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
            socket.matrix_world = socket.matrix_world @ AddMat
            socket.scale = savedScale
            socket.location = savedLocation


# Main asset


class PrepareExportName():
    def __init__(self, obj, is_armature):
        # Rename temporarily the assets
        if obj:

            self.target_object = obj
            self.is_armature = is_armature
            self.old_asset_name = ""
            self.new_asset_name = ""

            scene = bpy.context.scene
            if self.is_armature:
                self.new_asset_name = GetDesiredExportArmatureName(obj)
            else:
                self.new_asset_name = obj.name  # Keep the same name

    def SetExportName(self):

        '''
        Set the name of the asset for export
        '''

        scene = bpy.context.scene
        obj = self.target_object
        if obj.name != self.new_asset_name:
            self.old_asset_name = obj.name
            # Avoid same name for two assets
            if self.new_asset_name in scene.objects:
                confli_asset = scene.objects[self.new_asset_name]
                confli_asset.name = dup_temp_name
            obj.name = self.new_asset_name

    def ResetNames(self):
        '''
        Reset names after export
        '''

        scene = bpy.context.scene
        if self.old_asset_name != "":
            obj = self.target_object
            obj.name = self.old_asset_name

            if dup_temp_name in scene.objects:
                armature = scene.objects[dup_temp_name]
                armature.name = self.new_asset_name

        pass

# Sockets and Collisons


# Sockets


def TryToApplyCustomSocketsName(obj):
    '''
    Try to apply the custom SocketName
    '''

    scene = bpy.context.scene

    for socket in GetSocketDesiredChild(obj):
        if socket.usesocketcustomName:
            if socket.socketcustomName not in scene.objects:
                socket.name = "SOCKET_"+socket.socketcustomName
            else:
                print(
                    'Can\'t rename socket "' +
                    socket.name +
                    '" to "'+socket.socketcustomName +
                    '".'
                    )


# UVs

def ConvertGeometryNodeAttributeToUV(obj):
    #obj = bpy.context.active_object  # Debug
    if obj.convert_geometry_node_attribute_to_uv:
        attrib_name = obj.convert_geometry_node_attribute_to_uv_name

        # I need apply the geometry modifier for get the data.
        # So this work only when I do export of the duplicate object.

        if hasattr(obj.data, "attributes"):  # Cuves has not attributes.
            if attrib_name in obj.data.attributes:
            #if True == True:

                # TO DO: Bad why to do this. Need found a way to convert without using ops.
                obj.data.attributes.active = obj.data.attributes[attrib_name]
                SavedSelect = GetCurrentSelection()
                SelectSpecificObject(obj)
                bpy.ops.geometry.attribute_convert(mode='UV_MAP')
                SetCurrentSelection(SavedSelect)
                return

                attrib = obj.data.attributes[attrib_name]

                new_uv = obj.data.uv_layers.new(name=attrib_name)
                uv_coords = []

                attrib.data  # TO DO: I don't understand why attrib.data is egal at zero just after a duplicate.
                print('XXXXXXXXXXXX')
                print(type(attrib.data))
                print('XXXXXXXXXXXX')
                print(dir(attrib.data))
                print('XXXXXXXXXXXX')
                print(attrib.data.values())
                print('XXXXXXXXXXXX')
                attrib_data = []
                attrib.data.foreach_get('vector', attrib_data)
                print(attrib_data)

                for fv_attrib in attrib.data:  # FloatVectorAttributeValue
                    uv_coords.append(fv_attrib.vector)
                uv_coords.append(attrib.data[0])

                for loop in obj.data.loops:
                    new_uv.data[loop.index].uv[0] = uv_coords[loop.index][0]
                    new_uv.data[loop.index].uv[1] = uv_coords[loop.index][1]

                obj.data.attributes.remove(attrib_name)

def CorrectExtremUVAtExport(obj):
    if obj.correct_extrem_uv_scale:
        SavedSelect = GetCurrentSelection()
        if GoToMeshEditMode():
            CorrectExtremeUV(2)
            SafeModeSet('OBJECT')
            SetCurrentSelection(SavedSelect)
            return True
    return False

# Vertex Color


def SetVertexColorForUnrealExport(parent):

    objs = GetExportDesiredChilds(parent)
    objs.append(parent)

    for obj in objs:
        if obj.type == "MESH":
            vced = VertexColorExportData(obj, parent)
            if vced.export_type == "REPLACE":

                vertex_colors = utils.getVertexColors(obj)

                # Save the previous target
                obj.data["BFU_PreviousTargetIndex"] = vertex_colors.active_index

                # Ser the vertex color for export
                vertex_colors.active_index = vced.index


def ClearVertexColorForUnrealExport(parent):

    objs = GetExportDesiredChilds(parent)
    objs.append(parent)
    for obj in objs:
        if obj.type == "MESH":
            if "BFU_PreviousTargetIndex" in obj.data:
                del obj.data["BFU_PreviousTargetIndex"]


def GetShouldRescaleRig(obj):
    # This will return if the rig should be rescale.

    if obj.bfu_export_procedure == "auto-rig-pro":
        return False

    addon_prefs = GetAddonPrefs()
    if addon_prefs.rescaleFullRigAtExport == "auto":
        if math.isclose(
            bpy.context.scene.unit_settings.scale_length,
                0.01,
                rel_tol=1e-5,
                ):

            return False  # False because that useless to rescale at 1 :v
        else:
            return True
    if addon_prefs.rescaleFullRigAtExport == "custom_rescale":
        return True
    if addon_prefs.rescaleFullRigAtExport == "dont_rescale":
        return False
    return False


def GetRescaleRigFactor():
    # This will return the rescale factor.

    addon_prefs = GetAddonPrefs()
    if addon_prefs.rescaleFullRigAtExport == "auto":
        return 100 * bpy.context.scene.unit_settings.scale_length
    else:
        return addon_prefs.newRigScale  # rigRescaleFactor


def GetShouldRescaleSocket():
    # This will return if the socket should be rescale.

    addon_prefs = GetAddonPrefs()
    if addon_prefs.rescaleSocketsAtExport == "auto":
        if bpy.context.scene.unit_settings.scale_length == 0.01:
            return False  # False because that useless to rescale at 1 :v
        else:
            return True
    if addon_prefs.rescaleSocketsAtExport == "custom_rescale":
        return True
    if addon_prefs.rescaleSocketsAtExport == "dont_rescale":
        return False
    return False


def GetRescaleSocketFactor():
    # This will return the rescale factor.

    addon_prefs = GetAddonPrefs()
    if addon_prefs.rescaleSocketsAtExport == "auto":
        return 1/(100*bpy.context.scene.unit_settings.scale_length)
    else:
        return addon_prefs.staticSocketsImportedSize


def ExportAutoProRig(
        filepath,
        use_selection=True,
        export_rig_name="root",
        bake_anim=True,
        anim_export_name_string="",
        mesh_smooth_type="OFF",
        arp_simplify_fac=0.0
        ):

    bpy.context.scene.arp_engine_type = 'unreal'
    bpy.context.scene.arp_export_rig_type = 'mped'  # types: 'humanoid', 'mped'
    bpy.context.scene.arp_ge_sel_only = use_selection

    # Rig
    bpy.context.scene.arp_export_twist = False
    bpy.context.scene.arp_export_noparent = False
    bpy.context.scene.arp_units_x100 = True
    bpy.context.scene.arp_ue_root_motion = True

    # Anim
    bpy.context.scene.arp_bake_actions = bake_anim
    bpy.context.scene.arp_export_name_actions = True
    bpy.context.scene.arp_export_name_string = anim_export_name_string
    bpy.context.scene.arp_simplify_fac = arp_simplify_fac

    # Misc
    bpy.context.scene.arp_mesh_smooth_type = mesh_smooth_type
    bpy.context.scene.arp_use_tspace = False
    bpy.context.scene.arp_fix_fbx_matrix = False
    bpy.context.scene.arp_fix_fbx_rot = False
    bpy.context.scene.arp_init_fbx_rot = False
    bpy.context.scene.arp_bone_axis_primary_export = 'Y'
    bpy.context.scene.arp_bone_axis_secondary_export = 'X'
    bpy.context.scene.arp_export_rig_name = export_rig_name

    # export it
    print("Start AutoProRig Export")
    bpy.ops.id.arp_export_fbx_panel(filepath=filepath)


def ExportSingleAdditionalTrackCamera(dirpath, filename, obj):
    # Export additional camera track for ue4
    # FocalLength
    # FocusDistance
    # Aperture

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    AdditionalTrack = bfu_write_text.WriteCameraAnimationTracks(obj)
    return bfu_write_text.ExportSingleJson(
        AdditionalTrack,
        absdirpath,
        filename
        )


def ExportAdditionalParameter(dirpath, unreal_exported_asset):
    # Export additional parameter from static and skeletal mesh track for ue4
    # SocketsList

    filename = unreal_exported_asset.GetFilename("_AdditionalTrack.json")

    absdirpath = bpy.path.abspath(dirpath)
    VerifiDirs(absdirpath)
    AdditionalTrack = bfu_write_text.WriteSingleMeshAdditionalParameter(unreal_exported_asset)
    return bfu_write_text.ExportSingleJson(
        AdditionalTrack,
        absdirpath,
        filename
        )
