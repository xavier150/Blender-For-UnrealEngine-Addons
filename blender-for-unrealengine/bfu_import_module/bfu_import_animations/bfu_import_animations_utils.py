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

from .. import import_module_unreal_utils
from .. import import_module_tasks_class

try:
    import unreal
except ImportError:
    import unreal_engine as unreal



def apply_post_import_assets_changes(itask: import_module_tasks_class.ImportTaks, asset_data):
    if itask.use_interchange:
        apply_interchange_post_import(itask, asset_data)
    else:
        apply_fbxui_post_import(itask, asset_data)

def apply_interchange_post_import(itask: import_module_tasks_class.ImportTaks, asset_data):
    # When Import FBX animation using the Interchange it create Anim_0_Root and Root_MorphAnim_0. 
    # I'm not sure if that a bug... So remove I Root_MorphAnim_0 or other animations and I rename Anim_0_Root.
    asset_paths_to_remove = []
    main_anim_path = None
    for imported_asset in itask.GetImportedAssets():
        if type(imported_asset) is unreal.AnimSequence:
            anim_asset_path = imported_asset.get_path_name()
            path = anim_asset_path.rsplit('/', 1)[0]
            name = anim_asset_path.rsplit('/', 1)[1]
            if name == "Anim_0_Root.Anim_0_Root":
                main_anim_path = imported_asset.get_path_name()
            else:
                asset_paths_to_remove.append(imported_asset.get_path_name())

    # Remove wrong animation assets
    for asset_path in asset_paths_to_remove:
        unreal.EditorAssetLibrary.delete_asset(asset_path)
    
    # Rename correct animation asset
    if main_anim_path:
        anim_asset_path = imported_asset.get_path_name()
        path = anim_asset_path.rsplit('/', 1)[0]
        name = anim_asset_path.rsplit('/', 1)[1]
        new_anim_path = path + "/" + asset_data["asset_name"] + "." + asset_data["asset_name"]
        unreal.EditorAssetLibrary.rename_asset(main_anim_path, new_anim_path)
    else:
        fail_reason = 'animAsset ' + asset_data["asset_name"] + ' not found for after inport: ' + main_anim_path
        return fail_reason, None

def apply_fbxui_post_import(itask: import_module_tasks_class.ImportTaks, asset_data):
    # When Import FBX animation using FbxImportUI it create a skeletal mesh and the animation at this side. 
    # I'm not sure if that a bug too... So remove the extra mesh
    if itask.GetImportedAnimSequenceAsset() is None:
        # If Imported Anim Sequence is None it maybe imported the asset as Skeletal Mesh.
        skeleta_mesh_assset = itask.GetImportedSkeletalMeshAsset()
        if skeleta_mesh_assset:
            # If Imported as Skeletal Mesh Search the real Anim Sequence
            path = skeleta_mesh_assset.get_path_name()
            animAssetName = path.split('.')[0]+'_anim.'+path.split('.')[1]+'_anim'
            animAssetNameDesiredPath = path.split('.')[0]+'.'+path.split('.')[1]
            animAsset = unreal.find_asset(animAssetName)
            if animAsset is not None:
                # Remove the imported skeletal mesh and rename te anim sequence with his correct name.
                unreal.EditorAssetLibrary.delete_asset(path)
                unreal.EditorAssetLibrary.rename_asset(animAssetName, animAssetNameDesiredPath)
            else:
                fail_reason = 'animAsset ' + asset_data["asset_name"] + ' not found for after inport: ' + animAssetName
                return fail_reason, None