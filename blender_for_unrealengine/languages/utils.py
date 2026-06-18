# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from . import config
from .. import bpl

def construct_translations_dict() -> Optional[Dict[str, Dict[Tuple[Optional[str], str], str]]]:
    translations_dict: Optional[Dict[str, Dict[Tuple[Optional[str], str], str]]] = {
        "fr_FR": {
            ("ui.welcome", "Hello World"): "Bonjour le monde",
            ("ui.welcome2", "Hello World"): "Bonjour le monde2",
            (None, "My Tool"): "Mon outil",
        },
        "es_ES": {
            ("ui.welcome", "Hello World"): "Hola mundo",
            (None, "My Tool"): "Mi herramienta",
        }
    }

    # Try to found lang files
    lang_path = Path(__file__).parent / config.languages_folder
    onlyfiles = [f for f in lang_path.iterdir() if f.is_file()]

    # Json files need to be order this way: 
    # key: [original, translation]

    for file in onlyfiles:
        if file.name.endswith(".json"):
            try:
                with open(file, encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    blender_data = {}
                    for key in data:
                        original = data[key][0]
                        translation = data[key][1]
                        blender_data[(key, original)] = translation

                    translations_dict[file.stem] = blender_data
            except Exception as e:
                text = f"Error loading language file {file.name}: {e}"
                red_text = bpl.color_set.red(text)
                print(red_text)
                continue
    return translations_dict
