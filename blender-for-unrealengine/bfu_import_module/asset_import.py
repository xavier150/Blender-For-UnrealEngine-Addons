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


import os.path
from . import bps
from . import import_module_utils
from . import import_module_unreal_utils

try:  # TO DO: Found a better way to check that.
    import unreal
except ImportError:
    import unreal_engine as unreal




def ready_for_asset_import():
    if import_module_unreal_utils.is_unreal_version_greater_or_equal(4,20):  # TO DO: EditorAssetLibrary was added in witch version exactly?
        if not hasattr(unreal, 'EditorAssetLibrary'):
            message = 'WARNING: Editor Scripting Utilities should be activated.' + "\n"
            message += 'Edit > Plugin > Scripting > Editor Scripting Utilities.'
            import_module_unreal_utils.show_warning_message("Editor Scripting Utilities not activated.", message)
            return False
    return True




def ImportAsset(asset_data):


    if asset_data["asset_type"] == "StaticMesh" or asset_data["asset_type"] == "SkeletalMesh":
        if "lod" in asset_data:
            if asset_data["lod"] > 0:  # Lod should not be imported here so return if lod is not 0.
                return

    if asset_data["asset_type"] == "Alembic":
        FileType = "ABC"
    else:
        FileType = "FBX"

    def GetAdditionalData():
        if "additional_tracks_path" in asset_data:
            if asset_data["additional_tracks_path"] is not None:
                return import_module_utils.JsonLoadFile(asset_data["additional_tracks_path"])
        return None

    additional_data = GetAdditionalData()



    if asset_data["asset_type"] == "Animation" or asset_data["asset_type"] == "SkeletalMesh":
        find_asset = unreal.find_asset(asset_data["animation_skeleton_path"])
        if isinstance(find_asset, unreal.Skeleton):
            OriginSkeleton = find_asset
        elif isinstance(find_asset, unreal.SkeletalMesh):
            OriginSkeleton = find_asset.skeleton
        else:
            OriginSkeleton = None
        if OriginSkeleton:
            pass
            #print("Setting skeleton asset: " + OriginSkeleton.get_full_name())
        else:
            message = "Could not find skeleton at the path: " + asset_data["animation_skeleton_path"]
            import_module_unreal_utils.show_warning_message("Skeleton not found.", message)

    # docs.unrealengine.com/4.26/en-US/PythonAPI/class/AssetImportTask.html
    task = unreal.AssetImportTask()

    def GetStaticMeshImportData():
        if asset_data["asset_type"] == "StaticMesh":
            return task.get_editor_property('options').static_mesh_import_data
        return None

    def GetSkeletalMeshImportData():
        if asset_data["asset_type"] == "SkeletalMesh":
            return task.get_editor_property('options').skeletal_mesh_import_data
        return None

    def GetAnimationImportData():
        if asset_data["asset_type"] == "Animation":
            return task.get_editor_property('options').anim_sequence_import_data
        return None

    def GetAlembicImportData():
        if asset_data["asset_type"] == "Alembic":
            return task.get_editor_property('options')
        return None

    def GetMeshImportData():
        if asset_data["asset_type"] == "StaticMesh":
            return GetStaticMeshImportData()
        if asset_data["asset_type"] == "SkeletalMesh":
            return GetSkeletalMeshImportData()

        return None

    if asset_data["asset_type"] == "Alembic":
        task.filename = asset_data["abc_path"]
    else:
        task.filename = asset_data["fbx_path"]
    task.destination_path = os.path.normpath(asset_data["full_import_path"]).replace('\\', '/')
    task.automated = True
    # task.automated = False #Debug for show dialog
    task.save = True
    task.replace_existing = True

    if asset_data["asset_type"] == "Alembic":
        task.set_editor_property('options', unreal.AbcImportSettings())
    else:
        task.set_editor_property('options', unreal.FbxImportUI())

    # Alembic
    if GetAlembicImportData():
        GetAlembicImportData().static_mesh_settings.set_editor_property("merge_meshes", True)
        GetAlembicImportData().set_editor_property("import_type", unreal.AlembicImportType.SKELETAL)
        GetAlembicImportData().conversion_settings.set_editor_property("flip_u", False)
        GetAlembicImportData().conversion_settings.set_editor_property("flip_v", True)
        scale = asset_data["scene_unit_scale"] * asset_data["asset_global_scale"]
        ue_scale = unreal.Vector(scale * 100, scale * -100, scale * 100) # Unit scale * object scale * 100
        rotation = unreal.Vector(90, 0, 0)
        GetAlembicImportData().conversion_settings.set_editor_property("scale", ue_scale) 
        GetAlembicImportData().conversion_settings.set_editor_property("rotation", rotation)

    # Vertex color
    vertex_override_color = None
    vertex_color_import_option = None
    if additional_data:

        vertex_color_import_option = unreal.VertexColorImportOption.REPLACE  # Default
        if "vertex_color_import_option" in additional_data:
            if additional_data["vertex_color_import_option"] == "IGNORE":
                vertex_color_import_option = unreal.VertexColorImportOption.IGNORE
            elif additional_data["vertex_color_import_option"] == "OVERRIDE":
                vertex_color_import_option = unreal.VertexColorImportOption.OVERRIDE
            elif additional_data["vertex_color_import_option"] == "REPLACE":
                vertex_color_import_option = unreal.VertexColorImportOption.REPLACE

        if "vertex_override_color" in additional_data:
            vertex_override_color = unreal.LinearColor(
                additional_data["vertex_override_color"][0],
                additional_data["vertex_override_color"][1],
                additional_data["vertex_override_color"][2]
                )

    # #################################[Change]

    # unreal.FbxImportUI
    # https://docs.unrealengine.com/4.26/en-US/PythonAPI/class/FbxImportUI.html

    # Import transform
    anim_sequence_import_data = GetAnimationImportData()
    if anim_sequence_import_data:
        anim_sequence_import_data.import_translation = unreal.Vector(0, 0, 0)

    # Vertex color
    if vertex_color_import_option and GetMeshImportData():
        GetMeshImportData().set_editor_property('vertex_color_import_option', vertex_color_import_option)

    if vertex_override_color and GetMeshImportData():
        GetMeshImportData().set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

    if asset_data["asset_type"] == "Alembic":
        task.get_editor_property('options').set_editor_property('import_type', unreal.AlembicImportType.SKELETAL)

    else:
        if asset_data["asset_type"] == "Animation" or asset_data["asset_type"] == "SkeletalMesh":
            if OriginSkeleton:
                task.get_editor_property('options').set_editor_property('Skeleton', OriginSkeleton)
            else:
                if asset_data["asset_type"] == "Animation":
                    fail_reason = 'Skeleton ' + asset_data["animation_skeleton_path"] + ' Not found for ' + asset_data["asset_name"] + ' asset.'
                    return fail_reason
                else:
                    print("Skeleton is not set, a new skeleton asset will be created...")


        if asset_data["asset_type"] == "StaticMesh":
            task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_STATIC_MESH)
        elif asset_data["asset_type"] == "Animation":
            task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_ANIMATION)
        else:
            task.get_editor_property('options').set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)

        if asset_data["asset_type"] == "Animation":
            task.get_editor_property('options').set_editor_property('import_materials', False)
        else:
            task.get_editor_property('options').set_editor_property('import_materials', True)

        task.get_editor_property('options').set_editor_property('import_textures', False)

        if asset_data["asset_type"] == "Animation":

            task.get_editor_property('options').set_editor_property('import_animations', True)
            task.get_editor_property('options').set_editor_property('import_mesh', False)
            task.get_editor_property('options').set_editor_property('create_physics_asset',False)
        else:
            task.get_editor_property('options').set_editor_property('import_animations', False)
            task.get_editor_property('options').set_editor_property('import_mesh', True)
            if "create_physics_asset" in asset_data:
                task.get_editor_property('options').set_editor_property('create_physics_asset', asset_data["create_physics_asset"])

        # unreal.FbxMeshImportData

        if asset_data["asset_type"] == "StaticMesh" or asset_data["asset_type"] == "SkeletalMesh":
            if "material_search_location" in asset_data:
                # unreal.FbxTextureImportData
                if asset_data["material_search_location"] == "Local":
                    task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.LOCAL)
                if asset_data["material_search_location"] == "UnderParent":
                    task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_PARENT)
                if asset_data["material_search_location"] == "UnderRoot":
                    task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.UNDER_ROOT)
                if asset_data["material_search_location"] == "AllAssets":
                    task.get_editor_property('options').texture_import_data.set_editor_property('material_search_location', unreal.MaterialSearchLocation.ALL_ASSETS)

        if asset_data["asset_type"] == "StaticMesh":
            # unreal.FbxStaticMeshImportData
            task.get_editor_property('options').static_mesh_import_data.set_editor_property('combine_meshes', True)
            if "auto_generate_collision" in asset_data:
                task.get_editor_property('options').static_mesh_import_data.set_editor_property('auto_generate_collision', asset_data["auto_generate_collision"])
            if "static_mesh_lod_group" in asset_data:
                if asset_data["static_mesh_lod_group"]:
                    task.get_editor_property('options').static_mesh_import_data.set_editor_property('static_mesh_lod_group', asset_data["static_mesh_lod_group"])
            if "generate_lightmap_u_vs" in asset_data:
                task.get_editor_property('options').static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', asset_data["generate_lightmap_u_vs"])

        if asset_data["asset_type"] == "SkeletalMesh" or asset_data["asset_type"] == "Animation":
            # unreal.FbxSkeletalMeshImportData
            task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
            task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('convert_scene', True)
            task.get_editor_property('options').skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

    # ###############[ pre import ]################

    # Check is the file alredy exit
    if additional_data:
        if "preview_import_path" in additional_data:
            task_asset_full_path = task.destination_path+"/"+additional_data["preview_import_path"]+"."+additional_data["preview_import_path"]
            find_asset = unreal.find_asset(task_asset_full_path)
            if find_asset:

                # Vertex color

                asset_import_data = find_asset.get_editor_property('asset_import_data')
                if vertex_color_import_option:
                    asset_import_data.set_editor_property('vertex_color_import_option', vertex_color_import_option) 

                if vertex_override_color:
                    asset_import_data.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

    # ###############[ import asset ]################

    if asset_data["asset_type"] == "Animation":
        # For animation the script will import a skeletal mesh and remove after.
        # If the skeletal mesh alredy exist try to remove.


        AssetName = asset_data["asset_name"]
        AssetName = import_module_unreal_utils.ValidUnrealAssetsName(AssetName)
        AssetPath = "SkeletalMesh'"+asset_data["full_import_path"]+"/"+AssetName+"."+AssetName+"'"

        if unreal.EditorAssetLibrary.does_asset_exist(AssetPath):
            oldAsset = unreal.EditorAssetLibrary.find_asset_data(AssetPath)
            if oldAsset.asset_class == "SkeletalMesh":
                unreal.EditorAssetLibrary.delete_asset(AssetPath)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    if len(task.imported_object_paths) > 0:
        asset = unreal.find_asset(task.imported_object_paths[0])
    else:
        asset = None

    if asset is None:
        fail_reason = 'Error zero imported object for: ' + asset_data["asset_name"]
        return fail_reason

    if asset_data["asset_type"] == "Animation":
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
                fail_reason = 'animAsset ' + asset_data["asset_name"] + ' not found for after inport: ' + animAssetName
                return fail_reason

    # ###############[ Post treatment ]################
    asset_import_data = asset.get_editor_property('asset_import_data')
    if asset_data["asset_type"] == "StaticMesh":
        if "static_mesh_lod_group" in asset_data:
            if asset_data["static_mesh_lod_group"]:
                asset.set_editor_property('lod_group', asset_data["static_mesh_lod_group"])
        if "use_custom_light_map_resolution" in asset_data:
            if asset_data["use_custom_light_map_resolution"]:
                if "light_map_resolution" in asset_data:
                    asset.set_editor_property('light_map_resolution', asset_data["light_map_resolution"])
                    build_settings = unreal.EditorStaticMeshLibrary.get_lod_build_settings(asset, 0)
                    build_settings.min_lightmap_resolution = asset_data["light_map_resolution"]
                    unreal.EditorStaticMeshLibrary.set_lod_build_settings(asset, 0, build_settings)

        if "collision_trace_flag" in asset_data:
            collision_data = asset.get_editor_property('body_setup')
            if collision_data:
                if asset_data["collision_trace_flag"] == "CTF_UseDefault":
                    collision_data.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
                elif asset_data["collision_trace_flag"] == "CTF_UseSimpleAndComplex":
                    collision_data.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
                elif asset_data["collision_trace_flag"] == "CTF_UseSimpleAsComplex":
                    collision_data.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX)
                elif asset_data["collision_trace_flag"] == "CTF_UseComplexAsSimple":
                    collision_data.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)


    if asset_data["asset_type"] == "StaticMesh":
        if "generate_lightmap_u_vs" in asset_data:
            asset_import_data.set_editor_property('generate_lightmap_u_vs', asset_data["generate_lightmap_u_vs"])  # Import data
            unreal.EditorStaticMeshLibrary.set_generate_lightmap_uv(asset, asset_data["generate_lightmap_u_vs"])  # Build settings at lod

    if asset_data["asset_type"] == "SkeletalMesh":
        asset_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
        if OriginSkeleton is None:
            #Unreal create a new skeleton when no skeleton was selected, so addon rename it.
            p = task.imported_object_paths[0]
            old_skeleton_name = p.split('.')[0]+'_Skeleton.'+p.split('.')[1]+'_Skeleton'
            new_skeleton_name = asset_data["animation_skeleton_path"]
            unreal.EditorAssetLibrary.rename_asset(old_skeleton_name, new_skeleton_name)

        if "enable_skeletal_mesh_per_poly_collision" in asset_data:
            asset.set_editor_property('enable_per_poly_collision', asset_data["enable_skeletal_mesh_per_poly_collision"])
            

    # Socket
    if asset_data["asset_type"] == "SkeletalMesh":
        # Import the SkeletalMesh socket(s)
        sockets_to_add = additional_data["Sockets"]
        for socket in sockets_to_add:
            old_socket = asset.find_socket(socket["SocketName"])
            if old_socket:
                # Edit socket
                pass
                # old_socket.relative_location = socket["Location"]
                # old_socket.relative_rotation = socket["Rotation"]
                # old_socket.relative_scale = socket["Scale"]

            else:
                # Create socket
                pass
                # new_socket = unreal.SkeletalMeshSocket(asset)
                # new_socket.socket_name = socket["SocketName"]
                # new_socket.bone_name = socket["BoneName"]
                # new_socket.relative_location = socket["Location"]
                # new_socket.relative_rotation = socket["Rotation"]
                # new_socket.relative_scale = socket["Scale"]
                # NEED UNREAL ENGINE IMPLEMENTATION IN PYTHON API.
                # skeleton.add_socket(new_socket)

    # Lod
    if asset_data["asset_type"] == "StaticMesh" or asset_data["asset_type"] == "SkeletalMesh":
        if asset_data["asset_type"] == "StaticMesh":
            unreal.EditorStaticMeshLibrary.remove_lods(asset)  # Import the StaticMesh lod(s)

        if asset_data["asset_type"] == "SkeletalMesh" or asset_data["asset_type"] == "StaticMesh":

            def ImportStaticLod(lod_name, lod_number):
                if "LevelOfDetail" in additional_data:
                    if lod_name in additional_data["LevelOfDetail"]:
                        lodTask = unreal.AssetImportTask()
                        lodTask.filename = additional_data["LevelOfDetail"][lod_name]
                        destination_path = os.path.normpath(asset_data["full_import_path"]).replace('\\', '/')
                        lodTask.destination_path = destination_path
                        lodTask.automated = True
                        lodTask.replace_existing = True

                        # Set vertex color import settings to replicate base StaticMesh's behaviour
                        if asset_data["asset_type"] == "Alembic":
                            lodTask.set_editor_property('options', unreal.AbcImportSettings())
                        else:
                            lodTask.set_editor_property('options', unreal.FbxImportUI())

                        lodTask.get_editor_property('options').static_mesh_import_data.set_editor_property('vertex_color_import_option', vertex_color_import_option)
                        lodTask.get_editor_property('options').static_mesh_import_data.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

                        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([lodTask])
                        if len(lodTask.imported_object_paths) > 0:
                            lodAsset = unreal.find_asset(lodTask.imported_object_paths[0])
                            slot_replaced = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(asset, lod_number, lodAsset, 0, True)
                            unreal.EditorAssetLibrary.delete_asset(lodTask.imported_object_paths[0])

            def ImportSkeletalLod(lod_name, lod_number):
                if "LevelOfDetail" in additional_data:
                    if lod_name in additional_data["LevelOfDetail"]:
                        # Unreal python no longer support Skeletal mesh LODS import.
                        pass

            if asset_data["asset_type"] == "StaticMesh":
                ImportStaticLod("lod_1", 1)
                ImportStaticLod("lod_2", 2)
                ImportStaticLod("lod_3", 3)
                ImportStaticLod("lod_4", 4)
                ImportStaticLod("lod_5", 5)

            elif asset_data["asset_type"] == "SkeletalMesh":
                ImportSkeletalLod("lod_1", 1)
                ImportSkeletalLod("lod_2", 2)
                ImportSkeletalLod("lod_3", 3)
                ImportSkeletalLod("lod_4", 4)
                ImportSkeletalLod("lod_5", 5)

    # Vertex color
    if vertex_override_color:
        asset_import_data.set_editor_property('vertex_override_color', vertex_override_color.to_rgbe())

    if vertex_color_import_option:
        asset_import_data.set_editor_property('vertex_color_import_option', vertex_color_import_option)

    # #################################[EndChange]
    if asset_data["asset_type"] == "StaticMesh" or asset_data["asset_type"] == "SkeletalMesh":
        unreal.EditorAssetLibrary.save_loaded_asset(asset)
    return "SUCCESS", asset, asset_data["asset_type"]



def ImportAllAssets(assets_data):
    



    bfu_unreal_import_location = assets_data['bfu_unreal_import_location']
    ImportedList = []
    ImportFailList = []

    def GetAssetByType(type):
        target_assets = []
        for asset in assets_data["assets"]:
            if asset["asset_type"] == type:
                target_assets.append(asset)
        return target_assets

    def PrepareImportAsset(asset_data):
        counter = str(len(ImportedList)+1) + "/" + str(len(assets_data["assets"]))
        print("Import asset " + counter + ": ", asset_data["asset_name"])
        
        result, asset, asset_type = ImportAsset(asset_data)
        if result == "SUCCESS":
            ImportedList.append([asset, asset_data["asset_type"]])
        else:
            ImportFailList.append(result)



    # Process import
    print('========================= Import started ! =========================')
    counter = bps.utils.CounterTimer()

    # Import assets with a specific order

    for asset_data in GetAssetByType("Alembic"):
        PrepareImportAsset(asset_data)
    for asset_data in GetAssetByType("StaticMesh"):
        PrepareImportAsset(asset_data)
    for asset_data in GetAssetByType("SkeletalMesh"):
        PrepareImportAsset(asset_data)
    for asset_data in GetAssetByType("Animation"):
        PrepareImportAsset(asset_data)

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

    import_log = []
    import_log.append('Imported StaticMesh: '+str(len(StaticMesh_ImportedList)))
    import_log.append('Imported SkeletalMesh: '+str(len(SkeletalMesh_ImportedList)))
    import_log.append('Imported Alembic: '+str(len(Alembic_ImportedList)))
    import_log.append('Imported Animation: '+str(len(Animation_ImportedList)))
    import_log.append('Import failled: '+str(len(ImportFailList)))

    for import_row in import_log:
        print(import_row)
        
    for error in ImportFailList:
        print(error)

    # Select asset(s) in content browser
    PathList = []
    for asset in (StaticMesh_ImportedList + SkeletalMesh_ImportedList + Alembic_ImportedList + Animation_ImportedList):
        PathList.append(asset.get_path_name())
    unreal.EditorAssetLibrary.sync_browser_to_objects(PathList)
    print('=========================')

    if len(ImportFailList) > 0:
        message = 'Some asset(s) could not be imported.' + "\n"
    else:
        message = 'All assets imported with success!' + "\n"

    message += "Import finished in " + counter.get_str_time() + "\n"
    message += "\n"
    for import_row in import_log:
        message += import_row + "\n"

    if len(ImportFailList) > 0:
        message += "\n"
        for error in ImportFailList:
            message += error + "\n"

    title = "Import finished!"
    import_module_unreal_utils.show_simple_message(title, message)

    return True
