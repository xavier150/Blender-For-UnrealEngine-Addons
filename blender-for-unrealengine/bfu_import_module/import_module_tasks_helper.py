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


from . import import_module_unreal_utils
from . import import_module_tasks_class

try:
    import unreal
except ImportError:
    import unreal_engine as unreal

def task_options_default_preset(use_igap = True):
    if use_igap:
        options = unreal.InterchangeGenericAssetsPipeline()
    else:
        options = unreal.FbxImportUI()
    return options

def task_options_alembic_preset(use_igap = True):
    options =  unreal.AbcImportSettings()
    return options

def task_options_static_mesh_preset(use_igap = True):
    if use_igap:
        options = unreal.InterchangeGenericAssetsPipeline()
    else:
        options = unreal.FbxImportUI()
    return options

def task_options_skeletal_mesh_preset(use_igap = True):
    if use_igap:
        options = unreal.InterchangeGenericAssetsPipeline()
    else:
        options = unreal.FbxImportUI()
    return options

def task_options_animation_preset(use_igap = True):
    if use_igap:
        options = unreal.InterchangeGenericAssetsPipeline()
    else:
        options = unreal.FbxImportUI()
    return options



def init_options_data(itask: import_module_tasks_class.ImportTaks, asset_type):

    if asset_type == "Alembic":
        itask.get_task().set_editor_property('options', task_options_alembic_preset(itask.use_igap))

    elif asset_type == "StaticMesh":
        itask.get_task().set_editor_property('options', task_options_static_mesh_preset(itask.use_igap))

    elif asset_type == "SkeletalMesh":
        itask.get_task().set_editor_property('options', task_options_skeletal_mesh_preset(itask.use_igap))

    elif asset_type == "Animation":
        itask.get_task().set_editor_property('options', task_options_animation_preset(itask.use_igap))
        
    else:
        itask.get_task().set_editor_property('options', task_options_default_preset(itask.use_igap))