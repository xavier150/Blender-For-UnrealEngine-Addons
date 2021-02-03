# This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose
# The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python
# Use this command in Unreal cmd consol: py "[ScriptLocation]\ImportSequencerScript.py"


def CheckTasks():
    import unreal
    if not hasattr(unreal, 'EditorAssetLibrary'):
        print('--------------------------------------------------')
        print('/!\ Warning: Editor Scripting Utilities should be activated.')
        print('Plugin > Scripting > Editor Scripting Utilities.')
        return False
    return True


def ImportAllAssets():

    import unreal
    import os.path
    import ast
    import json

    '''
    if int(unreal.SystemLibrary.get_engine_version()[:4][2:]) >= 26:
        import configparser as ConfigParser
    else:
        import ConfigParser
    '''

    # Prepare process import
    json_data_file = 'ImportAssetData.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(dir_path, json_data_file), "r") as json_file:
        import_assets_data = json.load(json_file)

    unreal_import_location = import_assets_data['unreal_import_location']
    ImportedList = []
    ImportFailList = []

    def GetOptionByIniFile(FileLoc, OptionName, literal=False):
        Config = ConfigParser.ConfigParser()
        Config.read(FileLoc)
        Options = []
        if Config.has_section(OptionName):
            for option in Config.options(OptionName):
                if literal:
                    Options.append(ast.literal_eval(Config.get(OptionName, option)))
                else:
                    Options.append(Config.get(OptionName, option))
        else:
            print("/!\ Option: "+OptionName+" not found in file: "+FileLoc)
        return Options

    def GetAssetByType(type: str):
        target_assets = []
        for asset in import_assets_data["assets"]:
            if asset["type"] == type:
                target_assets.append(asset)
        return target_assets

    def ImportAsset(asset_data):
        counter = str(len(ImportedList)) + "/" + str(len(import_assets_data["assets"]))
        print("Import asset " + counter + ": ", asset_data["name"])

        if asset_data["type"] == "StaticMesh" or asset_data["type"] == "SkeletalMesh":
            if asset_data["lod"] > 0:  # Lod should not be imported here.
                return

        if asset_data["type"] == "Alembic":
            FileType = "ABC"
        else:
            FileType = "FBX"

        asset_data["full_import_path"]  # AssetImportPath
        asset_data["fbx_path"]  # fbx_file_path
        asset_data["additional_tracks_path"]  # additional_track_file_path

        def ImportTask():
            # New import task
            # Property
            if asset_data["type"] == "Animation":
                OriginSkeleton = unreal.find_asset(asset_data["animation_skeleton_path"])

            task = unreal.AssetImportTask()
            task.filename = asset_data["fbx_path"]
            task.destination_path = os.path.normpath(asset_data["full_import_path"]).replace('\\','/')
            task.automated = True
            task.save = True
            task.replace_existing = True

            if asset_data["type"] == "Alembic":
                task.set_editor_property('options', unreal.AbcImportSettings())
            else:
                task.set_editor_property('options', unreal.FbxImportUI())

            # #################################[Change]
            
            # unreal.FbxImportUI
            if asset_data["type"] == "Alembic":
                task.get_editor_property('options').set_editor_property('import_type', unreal.AlembicImportType.SKELETAL)

            else:

                if asset_data["type"] == "Animation":
                    if OriginSkeleton:
                        task.get_editor_property('options').set_editor_property('Skeleton', OriginSkeleton)
                    else:
                        ImportFailList.append('Skeleton ' + asset_data["animation_skeleton_path"] + ' Not found for ' + asset_data["name"] + ' asset.')
                        return

                if asset_data["type"] == "StaticMesh":
                    task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_STATIC_MESH)
                elif asset_data["type"] == "Animation":
                    task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_ANIMATION)
                else:
                    task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)

                if asset_data["type"] == "Animation":
                    task.get_editor_property('options').set_editor_property('import_materials', False)
                else:
                    task.get_editor_property('options').set_editor_property('import_materials', True)

                task.get_editor_property('options').set_editor_property('import_textures', False)

                if asset_data["type"] == "Animation":
                    task.get_editor_property('options').set_editor_property('import_animations', True)
                    task.get_editor_property('options').set_editor_property('import_mesh', False)
                    task.get_editor_property('options').set_editor_property('create_physics_asset',False)
                else:
                    task.get_editor_property('options').set_editor_property('import_animations', False)
                    task.get_editor_property('options').set_editor_property('import_mesh', True)
                    task.get_editor_property('options').set_editor_property('create_physics_asset', asset_data["create_physics_asset"])

                # unreal.FbxMeshImportData

                if asset_data["type"] == "StaticMesh" or asset_data["type"] == "SkeletalMesh":
                    # unreal.FbxTextureImportData
                    if asset_data["material_search_location"] == "Local":
                        task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.LOCAL)
                    if asset_data["material_search_location"] == "UnderParent":
                        task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_PARENT)
                    if asset_data["material_search_location"] == "UnderRoot":
                        task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_ROOT)
                    if asset_data["material_search_location"] == "AllAssets":
                        task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.ALL_ASSETS)

                if asset_data["type"] == "StaticMesh":
                    # unreal.FbxStaticMeshImportData
                    task.get_editor_property('options').static_mesh_import_data.set_editor_property('combine_meshes', True)
                    task.get_editor_property('options').static_mesh_import_data.set_editor_property('auto_generate_collision', asset_data["auto_generate_collision"])
                    task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', asset_data["lod_group"])
                    task.get_editor_property('options').static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', asset_data["generate_lightmap_u_vs"])

                if asset_data["type"] == "SkeletalMesh" or asset_data["type"] == "Animation":
                    # unreal.FbxSkeletalMeshImportData
                    task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
                    task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('convert_scene', True)
                    task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

            # ###############[ import asset ]################

            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            if len(task.imported_object_paths) > 0:
                asset = unreal.find_asset(task.imported_object_paths[0])
            else:
                asset = None

            if asset is None:
                ImportFailList.append('Error zero imported object for: ' + asset_data["name"])
                return

            if asset_data["type"] == "Animation":
                # For animation remove the extra mesh
                p = task.imported_object_paths[0]
                if type(unreal.find_asset(p)) is not unreal.AnimSequence:
                    animAssetName = p.split('.')[0]+'_anim.'+p.split('.')[1]+'_anim'
                    animAssetNameDesiredPath = p.split('.')[0]+'.'+p.split('.')[1]
                    animAsset = unreal.find_asset(animAssetName)
                    if animAsset is not None:
                        unreal.EditorAssetLibrary.delete_asset(p)
                        unreal.EditorAssetLibrary.rename_asset(animAssetName, animAssetNameDesiredPath)
                        asset = animAsset
                    else:
                        ImportFailList.append('animAsset ' + asset_data["name"] + ' not found for after inport: ' + animAssetName)
                        return

            # ###############[ Post treatment ]################

            if asset_data["type"] == "StaticMesh":
                asset.set_editor_property('lod_group', asset_data["lod_group"])
                asset.set_editor_property('light_map_resolution', asset_data["light_map_resolution"])

                if asset_data["collision_trace_flag"] == "CTF_UseDefault":
                    asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
                elif asset_data["collision_trace_flag"] == "CTF_UseSimpleAndComplex":
                    asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
                elif asset_data["collision_trace_flag"] == "CTF_UseSimpleAsComplex":
                    asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX)
                elif asset_data["collision_trace_flag"] == "CTF_UseComplexAsSimple":
                    asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)

                if asset_data["vertex_color_import_option"] == "VCIO_Ignore":
                    asset.get_editor_property('asset_import_data').set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption.IGNORE)
                elif asset_data["vertex_color_import_option"] == "VCIO_Replace":
                    asset.get_editor_property('asset_import_data').set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption.REPLACE)

            if asset_data["type"] == "SkeletalMesh":
                asset.get_editor_property('asset_import_data').set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

            # Socket
            if asset_data["type"] == "SkeletalMesh":
                # Import the SkeletalMesh socket(s)
                sockets_to_add = GetOptionByIniFile(asset_data["additional_tracks_path"], 'Sockets', True)
                skeleton = asset.get_editor_property('skeleton')
                for socket in sockets_to_add:
                    pass
                    # Create socket
                    # new_socket = unreal.SkeletalMeshSocket('', skeleton)
                    # new_socket.SocketName = socket[0]

            # Lod
            if asset_data["type"] == "StaticMesh" or asset_data["type"] == "SkeletalMesh":
                if asset_data["type"] == "StaticMesh":
                    unreal.EditorStaticMeshLibrary.remove_lods(asset)  # Import the StaticMesh lod(s)

                if asset_data["type"] == "SkeletalMesh":
                    lods_to_add = GetOptionByIniFile(asset_data["additional_tracks_path"], 'LevelOfDetail')  # Import the SkeletalMesh lod(s)

                for x, lod in enumerate(lods_to_add):
                    if asset_data["type"] == "StaticMesh":
                        lodTask = unreal.AssetImportTask()
                        lodTask.filename = lod
                        lodTask.destination_path = os.path.normpath(asset_data["full_import_path"]).replace('\\','/')
                        lodTask.automated = True
                        lodTask.replace_existing = True
                        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])
                        lodAsset = unreal.find_asset(lodTask.imported_object_paths[0])
                        slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, x+1, lodAsset, 0, True)
                        unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])
                    elif asset_data["type"] == "SkeletalMesh":
                        pass
                        unreal.FbxMeshUtils.ImportSkeletalMeshLOD(asset, lod, x+1) # Vania unreal python dont have unreal.FbxMeshUtils.

            # #################################[EndChange]
            if asset_data["type"] == "StaticMesh" or asset_data["type"] == "SkeletalMesh":
                unreal.EditorAssetLibrary.save_loaded_asset(asset)
            ImportedList.append([asset, asset_data["type"]])

        ImportTask()


    # Process import

    print('========================= Import started ! =========================')

    # Import assets with a specific order

    for asset in GetAssetByType("Alembic"):
        ImportAsset(asset)
    for asset in GetAssetByType("StaticMesh"):
        ImportAsset(asset)
    for asset in GetAssetByType("SkeletalMesh"):
        ImportAsset(asset)
    for asset in GetAssetByType("Animation"):
        ImportAsset(asset)

    print('========================= Full import completed !  =========================')

    # import result
    StaticMesh_ImportedList = []
    SkeletalMesh_ImportedList = []
    Alembic_ImportedList = []
    Animation_ImportedList = []
    for asset in ImportedList:
        if asset[1] == 'StaticMesh':
            StaticMesh_ImportedList.append(asset[0])
        elif asset[1] == 'SkeletalMesh':
            SkeletalMesh_ImportedList.append(asset[0])
        elif asset[1] == 'Alembic':
            Alembic_ImportedList.append(asset[0])
        else:
            Animation_ImportedList.append(asset[0])

    print('Imported StaticMesh: '+str(len(StaticMesh_ImportedList)))
    print('Imported SkeletalMesh: '+str(len(SkeletalMesh_ImportedList)))
    print('Imported Alembic: '+str(len(Alembic_ImportedList)))
    print('Imported Animation: '+str(len(Animation_ImportedList)))
    print('Import failled: '+str(len(ImportFailList)))
    for error in ImportFailList:
        print(error)

    #Select asset(s) in content browser
    PathList = []
    for asset in (StaticMesh_ImportedList + SkeletalMesh_ImportedList + Alembic_ImportedList + Animation_ImportedList):
        PathList.append(asset.get_path_name())
    unreal.EditorAssetLibrary.sync_browser_to_objects(PathList)
    print('=========================')

    if len(ImportFailList) > 0:
        return 'Some asset(s) could not be imported.'
    else:
        return 'Assets imported with success !'


print("Start")

if CheckTasks():
    print(ImportAllAssets())

print("End")
