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
import configparser
from math import degrees

if "bpy" in locals():
    import importlib
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_write_utils" in locals():
        importlib.reload(bfu_write_utils)

from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_write_utils
from .bfu_write_utils import *


def GetFBXImportType(assetType):

    if assetType == "StaticMesh":
        return "FBXIT_STATIC_MESH"
    else:
        if GetIsAnimation(assetType):
            return "FBXIT_ANIMATION"
        else:
            return "FBXIT_SKELETAL_MESH"


def WriteImportPythonHeader():
    GetImportSequencerScriptCommand()
    scene = bpy.context.scene

    # Import
    ImportScript = "import os.path" + "\n"
    ImportScript += "import ConfigParser" + "\n"

    ImportScript += "import ast" + "\n"
    ImportScript += "import unreal" + "\n"
    ImportScript += "\n"
    ImportScript += "\n"

    # Prepare var and def
    ImportScript += "#Prepare var and def" + "\n"
    ImportScript += "unrealImportLocation = r'/Game/" + scene.unreal_import_location + "'" + "\n"
    ImportScript += "ImportedList = []" + "\n"
    ImportScript += "ImportFailList = []" + "\n"
    ImportScript += "\n"

    return ImportScript


def WriteImportPythonDef():

    ImportScript = ""
    ImportScript += "def GetOptionByIniFile(FileLoc, OptionName, literal = False):" + "\n"
    ImportScript += "\t" + "Config = ConfigParser.ConfigParser()" + "\n"

    ImportScript += "\t" + "Config.read(FileLoc)" + "\n"
    ImportScript += "\t" + "Options = []" + "\n"
    ImportScript += "\t" + 'if Config.has_section(OptionName):' + "\n"
    ImportScript += "\t\t" + 'for option in Config.options(OptionName):' + "\n"
    ImportScript += "\t\t\t" + 'if (literal == True):' + "\n"
    ImportScript += "\t\t\t\t" + 'Options.append(ast.literal_eval(Config.get(OptionName, option)))' + "\n"
    ImportScript += "\t\t\t" + 'else:' + "\n"
    ImportScript += "\t\t\t\t" + 'Options.append(Config.get(OptionName, option))' + "\n"
    ImportScript += "\t" + 'else:' + "\n"
    ImportScript += "\t\t" + 'print("/!\ Option: "+OptionName+" not found in file: "+FileLoc)' + "\n"
    ImportScript += "\t" + "return Options" + "\n"
    ImportScript += "\n"
    ImportScript += "\n"

    return ImportScript

def WriteImportPythonFooter():

    #import result
    ImportScript = ""
    ImportScript += "print('========================= Full import completed !  =========================')" + "\n"
    ImportScript += "\n"
    ImportScript += "StaticMesh_ImportedList = []" + "\n"
    ImportScript += "SkeletalMesh_ImportedList = []" + "\n"
    ImportScript += "Alembic_ImportedList = []" + "\n"
    ImportScript += "Animation_ImportedList = []" + "\n"
    ImportScript += "for asset in ImportedList:" + "\n"
    ImportScript += "\t" + "if asset[1] == 'StaticMesh':" + "\n"
    ImportScript += "\t\t" + "StaticMesh_ImportedList.append(asset[0])" + "\n"
    ImportScript += "\t" + "elif asset[1] == 'SkeletalMesh':" + "\n"
    ImportScript += "\t\t" + "SkeletalMesh_ImportedList.append(asset[0])" + "\n"
    ImportScript += "\t" + "elif asset[1] == 'Alembic':" + "\n"
    ImportScript += "\t\t" + "Alembic_ImportedList.append(asset[0])" + "\n"
    ImportScript += "\t" + "else:" + "\n"
    ImportScript += "\t\t" + "Animation_ImportedList.append(asset[0])" + "\n"
    ImportScript += "\n"
    ImportScript += "print('Imported StaticMesh: '+str(len(StaticMesh_ImportedList)))" + "\n"
    ImportScript += "print('Imported SkeletalMesh: '+str(len(SkeletalMesh_ImportedList)))" + "\n"
    ImportScript += "print('Imported Alembic: '+str(len(Alembic_ImportedList)))" + "\n"
    ImportScript += "print('Imported Animation: '+str(len(Animation_ImportedList)))" + "\n"
    ImportScript += "print('Import failled: '+str(len(ImportFailList)))" + "\n"
    ImportScript += "for error in ImportFailList:" + "\n"
    ImportScript += "\t" + "print(error)" + "\n"
    ImportScript += "\n"

    ImportScript += "#Select asset(s) in content browser" + "\n"
    ImportScript += "PathList = []" + "\n"
    ImportScript += "for asset in (StaticMesh_ImportedList + SkeletalMesh_ImportedList + Alembic_ImportedList + Animation_ImportedList):" + "\n"
    ImportScript += "\t" + "PathList.append(asset.get_path_name())" + "\n"
    ImportScript += "unreal.EditorAssetLibrary.sync_browser_to_objects(PathList)" + "\n"
    ImportScript += "\n"

    ImportScript += "print('=========================')" + "\n"
    return ImportScript


def WriteOneAssetTaskDef(asset):
    scene = bpy.context.scene
    ImportScript = ""
    ImportScript += "\n"
    if (asset.object.ExportAsLod == False and
        (asset.assetType == "StaticMesh"
        or asset.assetType == "SkeletalMesh"
        or asset.assetType == "Alembic"
        or GetIsAnimation(asset.assetType))
        ):
        pass
    else:
        return ImportScript

    if asset.assetType == "Alembic":
        FileType = "ABC"
    else:
        FileType = "FBX"

    obj = asset.object
    if GetIsAnimation(asset.assetType):
        AssetRelatifImportPath = os.path.join(obj.exportFolderName, scene.anim_subfolder_name)
    else:
        AssetRelatifImportPath = obj.exportFolderName
    FilePath = (os.path.join(asset.exportPath, asset.assetName))
    AdditionalParameterLoc = (os.path.join(asset.exportPath, GetObjExportFileName(asset.object,"_AdditionalParameter.ini")))


    assetUseName = asset.assetName[:-4].replace(' ','_').replace('-','_')
    ImportScript += "def CreateTask_"+ assetUseName + "():" + "\n"
    ################[ New import task ]################
    ImportScript += "\t" + "################[ Import "+obj.name+" as "+asset.assetType+" type ]################" + "\n"
    ImportScript += "\t" + "print('================[ New import task : "+obj.name+" as "+asset.assetType+" type ]================')" + "\n"


    ##################################[Change]

    #Property
    ImportScript += "\t" + "FilePath = os.path.join(r'"+FilePath+"')" + "\n"
    ImportScript += "\t" + "AdditionalParameterLoc = os.path.join(r'"+AdditionalParameterLoc+"')" + "\n"
    ImportScript += "\t" + "AssetImportPath = (os.path.join(unrealImportLocation, r'"+AssetRelatifImportPath+r"').replace('\\','/')).rstrip('/')" + "\n"

    if GetIsAnimation(asset.assetType):
        if(obj.UseTargetCustomSkeletonName):
            customName = obj.TargetCustomSkeletonName
            SkeletonName = customName+"."+customName
        else:
            SkeletonName = scene.skeletal_prefix_export_name+obj.name+"_Skeleton."+scene.skeletal_prefix_export_name+obj.name+"_Skeleton"
        SkeletonLoc = os.path.join(obj.exportFolderName,SkeletonName)
        ImportScript += "\t" + "SkeletonLocation = os.path.join(unrealImportLocation, r'" + SkeletonLoc + r"').replace('\\','/')" + "\n"

        ImportScript += "\t" + "OriginSkeleton = unreal.find_asset(SkeletonLocation)" + "\n"


    #ImportTask

    ImportScript += "\t" + "task = unreal.AssetImportTask()" + "\n"
    ImportScript += "\t" + "task.filename = FilePath" + "\n"
    ImportScript += "\t" + r"task.destination_path = os.path.normpath(AssetImportPath).replace('\\','/')" + "\n"
    ImportScript += "\t" + "task.automated = True" + "\n"
    ImportScript += "\t" + "task.save = True" + "\n"
    ImportScript += "\t" + "task.replace_existing = True" + "\n"
    if FileType == "FBX":
        ImportScript += "\t" + "task.set_editor_property('options', unreal.FbxImportUI())" + "\n"
    if FileType == "ABC":
        ImportScript += "\t" + "task.set_editor_property('options', unreal.AbcImportSettings())" + "\n"


    # unreal.FbxImportUI
    if FileType == "FBX":
        if GetIsAnimation(asset.assetType):
            ImportScript += "\t" + "if OriginSkeleton:" + "\n"

            ImportScript += "\t\t" + "task.get_editor_property('options').set_editor_property('Skeleton', OriginSkeleton)" + "\n"
            ImportScript += "\t" + "else:" + "\n"

            ImportScript += "\t\t" + "ImportFailList.append('Skeleton \"'+SkeletonLocation+'\" Not found for \""+obj.name+"\" asset ')" + "\n"
            ImportScript += "\t\t" + "return" + "\n"

        ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType."+GetFBXImportType(asset.assetType)+")" + "\n"

        if GetIsAnimation(asset.assetType):
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_materials', False)" + "\n"
        else:
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_materials', True)" + "\n"
        ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_textures', False)" + "\n"

        if GetIsAnimation(asset.assetType):
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_animations', True)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_mesh', False)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('create_physics_asset',False)" + "\n"
        else:
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_animations', False)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_mesh', True)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('create_physics_asset', " + str(obj.CreatePhysicsAsset) + ")" + "\n"

        # unreal.FbxMeshImportData
        if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":
            # unreal.FbxTextureImportData

            if obj.MaterialSearchLocation == "Local": python_MaterialSearchLocation = "LOCAL"
            if obj.MaterialSearchLocation == "UnderParent": python_MaterialSearchLocation = "UNDER_PARENT"
            if obj.MaterialSearchLocation == "UnderRoot": python_MaterialSearchLocation = "UNDER_ROOT"
            if obj.MaterialSearchLocation == "AllAssets": python_MaterialSearchLocation = "ALL_ASSETS"
            ImportScript += "\t" + "task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation." + python_MaterialSearchLocation +")"+ "\n"

        if asset.assetType == "StaticMesh":
            # unreal.FbxStaticMeshImportData

            ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('combine_meshes', True)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('auto_generate_collision', "+ str(obj.AutoGenerateCollision) +")"+ "\n"
            if (obj.UseStaticMeshLODGroup == True):
                ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', '" + obj.StaticMeshLODGroup +"')"+ "\n"
            else:
                ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', 'None')"+ "\n"
            ImportScript += "\t" + "task.get_editor_property('options').static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', " + str(obj.GenerateLightmapUVs) +")"+ "\n"


        if asset.assetType == "SkeletalMesh" or GetIsAnimation(asset.assetType):
            # unreal.FbxSkeletalMeshImportData
            ImportScript += "\t" + "task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('convert_scene', True)" + "\n"
            ImportScript += "\t" + "task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)" + "\n"

    if FileType == "ABC":

        ImportScript += "\t" + "task.get_editor_property('options').set_editor_property('import_type', unreal.AlembicImportType.SKELETAL)" + "\n"



    ################[ import asset ]################
    ImportScript += "\t" + "print('================[ import asset : "+obj.name+" ]================')" + "\n"

    ImportScript += "\t" + "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])" + "\n"
    ImportScript += "\t" + "if len(task.imported_object_paths) > 0:" + "\n"
    ImportScript += "\t\t" + "asset = unreal.find_asset(task.imported_object_paths[0])" + "\n"
    ImportScript += "\t" + "else:" + "\n"
    ImportScript += "\t\t" + "asset = None" + "\n"

    ImportScript += "\t" + "if asset == None:" + "\n"
    ImportScript += "\t\t" + "ImportFailList.append('Error zero imported object for \""+obj.name+"\" ')" + "\n"
    ImportScript += "\t\t" + "return" + "\n"

    if asset.assetType == "Action" or asset.assetType == "Pose" or asset.assetType == "NlAnim":
        #Remove extra mesh
        ImportScript += "\t" + "# For animation remove the extra mesh" + "\n"

        ImportScript += "\t" + "p = task.imported_object_paths[0]" + "\n"
        ImportScript += "\t" + "if type(unreal.find_asset(p)) is not unreal.AnimSequence:" + "\n"
        ImportScript += "\t\t" + "animAssetName = p.split('.')[0]+'_anim.'+p.split('.')[1]+'_anim'" + "\n"
        ImportScript += "\t\t" + "animAssetNameDesiredPath = p.split('.')[0]+'.'+p.split('.')[1]" + "\n"
        ImportScript += "\t\t" + "animAsset = unreal.find_asset(animAssetName)" + "\n"
        ImportScript += "\t\t" + "if animAsset is not None:" + "\n"
        ImportScript += "\t\t\t" + "unreal.EditorAssetLibrary.delete_asset(p)" + "\n"
        ImportScript += "\t\t\t" + "unreal.EditorAssetLibrary.rename_asset(animAssetName, animAssetNameDesiredPath)" + "\n"
        ImportScript += "\t\t\t" + "asset = animAsset" + "\n"
        ImportScript += "\t\t" + "else:" + "\n"
        ImportScript += "\t\t\t" + "ImportFailList.append('animAsset \""+obj.name+"\" not found for after inport: '+animAssetName)" + "\n"
        ImportScript += "\t\t\t" + "return" + "\n"


    ################[ Post treatment ]################
    ImportScript += "\t" + "print('========================= Imports of "+obj.name+" completed ! Post treatment started...	=========================')" + "\n"


    if asset.assetType == "StaticMesh":

        if (obj.UseStaticMeshLODGroup == True):
            ImportScript += "\t" "asset.set_editor_property('lod_group', '" + obj.StaticMeshLODGroup + "')" + "\n"
        else:
            ImportScript += "\t" "asset.set_editor_property('lod_group', 'None')" + "\n"
        if (ExportCompuntedLightMapValue(obj) == True):
            ImportScript += "\t" "asset.set_editor_property('light_map_resolution', " + str(GetCompuntedLightMap(obj)) + ")" +"\n"
        if obj.CollisionTraceFlag == "CTF_UseDefault": python_CollisionTraceFlag = "CTF_USE_DEFAULT"
        if obj.CollisionTraceFlag == "CTF_UseSimpleAndComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AND_COMPLEX"
        if obj.CollisionTraceFlag == "CTF_UseSimpleAsComplex": python_CollisionTraceFlag = "CTF_USE_SIMPLE_AS_COMPLEX"
        if obj.CollisionTraceFlag == "CTF_UseComplexAsSimple": python_CollisionTraceFlag = "CTF_USE_COMPLEX_AS_SIMPLE"
        ImportScript += "\t" + "asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag." + python_CollisionTraceFlag + ") " + "\n"

        if obj.VertexColorImportOption == "VCIO_Ignore" : python_VertexColorImportOption = "IGNORE"
        if obj.VertexColorImportOption == "VCIO_Replace" : python_VertexColorImportOption = "REPLACE"
        ImportScript += "\t" + "asset.get_editor_property('asset_import_data').set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption." + python_VertexColorImportOption + ") " + "\n"

    if asset.assetType == "SkeletalMesh":

        ImportScript += "\t" + "asset.get_editor_property('asset_import_data').set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS) " + "\n"

    #Socket
    if asset.assetType == "SkeletalMesh":

        ImportScript += "\n\t" + "#Import the SkeletalMesh socket(s)" + "\n" #Import the SkeletalMesh  Socket(s)
        ImportScript += "\t" + "sockets_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'Sockets', True)" + "\n"

        ImportScript += "\t" + "skeleton = asset.get_editor_property('skeleton')" + "\n"
        ImportScript += "\t" + "for socket in sockets_to_add:" + "\n"

        #Create socket
        ImportScript += "\t\t" + "pass" + "\n"
        #ImportScript += "\t\t" + "#Create socket" + "\n"
        #ImportScript += "\t\t" + "new_socket = unreal.SkeletalMeshSocket('', skeleton)" + "\n"
        #ImportScript += "\t\t" + "new_socket.SocketName = socket[0]" + "\n"

    #Lod
    if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":
        if asset.assetType == "StaticMesh":
            ImportScript += "\n\t" + "#Import the StaticMesh lod(s)" + "\n" #Import the StaticMesh lod(s)
            ImportScript += "\t" + "unreal.EditorStaticMeshLibrary.remove_lods(asset)" + "\n"

        if asset.assetType == "SkeletalMesh":
            ImportScript += "\n\t" + "#Import the SkeletalMesh lod(s)" + "\n" #Import the SkeletalMesh  lod(s)

        ImportScript += "\t" + "lods_to_add = GetOptionByIniFile(AdditionalParameterLoc, 'LevelOfDetail')" + "\n"
        ImportScript += "\t" + "for x, lod in enumerate(lods_to_add):" + "\n"


        if asset.assetType == "StaticMesh":

            ImportScript += "\t\t" + "lodTask = unreal.AssetImportTask()" + "\n"
            ImportScript += "\t\t" + "lodTask.filename = lod" + "\n"
            ImportScript += "\t\t" + r"lodTask.destination_path = os.path.normpath(AssetImportPath).replace('\\','/')" + "\n"
            ImportScript += "\t\t" + "lodTask.automated = True" + "\n"
            ImportScript += "\t\t" + "lodTask.replace_existing = True" + "\n"
            ImportScript += "\t\t" + "unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])" + "\n"
            ImportScript += "\t\t" + "lodAsset = unreal.find_asset(lodTask.imported_object_paths[0])" + "\n"
            ImportScript += "\t\t" + "slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, x+1, lodAsset, 0, True)" + "\n"
            ImportScript += "\t\t" + "unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])" + "\n"
        elif asset.assetType == "SkeletalMesh":

            ImportScript += "\t\t" + "pass" + "\n"
            #ImportScript += "\t\t" + "unreal.FbxMeshUtils.ImportSkeletalMeshLOD(asset, lod, x+1)" + "\n" #Vania unreal python dont have unreal.FbxMeshUtils.
        else:
            ImportScript += "\t\t" + "pass" + "\n"


    ##################################[EndChange]


    ImportScript += "\t" + "print('========================= Post treatment of "+obj.name+" completed !	 =========================')" + "\n"

    if asset.assetType == "StaticMesh" or asset.assetType == "SkeletalMesh":
        ImportScript += "\t" + "unreal.EditorAssetLibrary.save_loaded_asset(asset)" + "\n"

    ImportScript += "\t" + "ImportedList.append([asset, '" + asset.assetType + "'])" + "\n"
    ImportScript += "CreateTask_"+assetUseName + "()" + "\n"
    ImportScript += "\n"
    ImportScript += "\n"
    ImportScript += "\n"

    return ImportScript

def WriteImportAssetScript():
    #Generate a script for import assets in Ue4
    scene = bpy.context.scene

    ImportScript = WriteImportPythonHeader()
    ImportScript += WriteImportPythonDef()

    #Process import
    ImportScript += "#Process import" + "\n"
    ImportScript += "print('========================= Import started ! =========================')" + "\n"
    ImportScript += "\n"
    ImportScript += "\n"
    ImportScript += "\n"


    def WriteImportMultiTask(desiredTaskType):

        ImportScript = ""
        ImportScript += "\n"
        ImportScript += "'''" + "\n"
        emptyChar = ""
        hashtagChar = ""
        for u in range(0, len(desiredTaskType)):
            emptyChar+= " "
            hashtagChar+= "#"
        ImportScript += "<###############################"+ hashtagChar +"#####################################>" + "\n"
        ImportScript += "<#############################	 "+ emptyChar +"		#############################>" + "\n"
        ImportScript += "<############################	 "+ emptyChar +"		 ############################>" + "\n"
        ImportScript += "<############################	 "+desiredTaskType+" tasks	 ############################>" + "\n"
        ImportScript += "<############################	 "+ emptyChar +"		 ############################>" + "\n"
        ImportScript += "<#############################	 "+ emptyChar +"		#############################>" + "\n"
        ImportScript += "<###############################"+ hashtagChar +"#####################################>" + "\n"
        ImportScript += "'''" + "\n"
        ImportScript += "\n"

        ImportScript += desiredTaskType+"_TasksList = []" + "\n"
        ImportScript += desiredTaskType+"_PreImportPath = []" + "\n"
        ImportScript += "print('========================= Creating "+desiredTaskType+" tasks... =========================')" + "\n"

        for asset in scene.UnrealExportedAssetsList:
            if desiredTaskType == asset.assetType or (GetIsAnimation(asset.assetType) and desiredTaskType == "Animation" ):
                ImportScript += WriteOneAssetTaskDef(asset)


        ImportScript += "\n"



        return ImportScript

    def ExsitTypeInExportedAssets(desiredTaskType):
        #Cree un groupe de tache uniquement si il trouve des taches a faire si non return
        for asset in scene.UnrealExportedAssetsList:
            if asset.assetType == desiredTaskType:
                return True
            if GetIsAnimation(asset.assetType) and desiredTaskType == "Animation":
                return True
        return False

    #Deffini la priorité d'import des objects
    if ExsitTypeInExportedAssets("Alembic"):
        ImportScript += WriteImportMultiTask("Alembic")
    if ExsitTypeInExportedAssets("StaticMesh"):
        ImportScript += WriteImportMultiTask("StaticMesh")
    if ExsitTypeInExportedAssets("SkeletalMesh"):
        ImportScript += WriteImportMultiTask("SkeletalMesh")
    if ExsitTypeInExportedAssets("Animation"):
        ImportScript += WriteImportMultiTask("Animation")

    ImportScript += WriteImportPythonFooter()

    ImportScript += "if len(ImportFailList) == 0:" + "\n"
    ImportScript += "\t" + "return 'Assets imported with success !' " + "\n"
    ImportScript += "else:" + "\n"
    ImportScript += "\t" + "return 'Some asset(s) could not be imported.' " + "\n"

    #-------------------------------------

    CheckScript = ""

    CheckScript += "import unreal" + "\n"

    CheckScript += "if hasattr(unreal, 'EditorAssetLibrary') == False:" + "\n"
    CheckScript += "\t" + "print('--------------------------------------------------\\n /!\ Warning: Editor Scripting Utilities should be activated.\\n Plugin > Scripting > Editor Scripting Utilities.')" + "\n"
    CheckScript += "\t" + "return False" + "\n"

    CheckScript += "return True" + "\n"

    #-------------------------------------

    OutImportScript = ""
    OutImportScript += WriteImportPythonHeadComment(False)

    OutImportScript += "def CheckTasks():" + "\n"
    OutImportScript += bfu_utils.AddFrontEachLine(CheckScript, "\t")

    OutImportScript += "def ImportAllAssets():" + "\n"
    OutImportScript += bfu_utils.AddFrontEachLine(ImportScript, "\t")

    OutImportScript += "if CheckTasks() == True:" + "\n"
    OutImportScript += "\t" + "print(ImportAllAssets())" + "\n"


    return OutImportScript