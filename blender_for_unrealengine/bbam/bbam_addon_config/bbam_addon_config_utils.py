# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os
import json
from typing import Optional
from .bbam_addon_config_type import BBAM_AddonConfig
from .. import config

def load_addon_config_from_json(
    addon_path: str
) -> Optional[BBAM_AddonConfig]:

    # Get the path of the current addon's configuration file from `config`
    addon_manifest_name = config.addon_generate_config
    addon_manifest_path = os.path.abspath(os.path.join(addon_path, addon_manifest_name))

    # Load the manifest file data if it exists
    if os.path.isfile(addon_manifest_path):
        with open(addon_manifest_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            addon_config = BBAM_AddonConfig()
            addon_config.set_config_from_dict(data)
        return addon_config
    else:
        print(f"Error: '{addon_manifest_name}' was not found in '{addon_manifest_path}'.")
        return None

    