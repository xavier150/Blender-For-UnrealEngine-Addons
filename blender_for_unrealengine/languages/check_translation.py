# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

def find_translations_dir() -> Optional[Path]:
    """Find the translations folder"""
    script_dir = Path(__file__).parent
    possible_dirs = [
        script_dir / "local_list",
        script_dir.parent / "local_list",
    ]
    
    for dir_path in possible_dirs:
        if dir_path.exists() and dir_path.is_dir():
            return dir_path

    return None

def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Load a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def check_translation_files():
    """Check consistency of translation files"""
    translations_dir = find_translations_dir()
    if not translations_dir:
        return
    
    source_file = translations_dir / "en_US.json"
    source_data = load_json_file(source_file)
    if not source_data:
        return
    
    source_keys = set(source_data.keys())
    source_originals: Dict[str, Any] = {}
    for key, value in source_data.items():
        if isinstance(value, list) and len(value) >= 2:  # type: ignore
            source_originals[key] = value[0]
    
    errors_found = False
    
    for file_name in ["fr_FR.json", "ru_RU.json", "zh_HANS.json"]:
        file_path = translations_dir / file_name
        translation_data = load_json_file(file_path)
        if not translation_data:
            continue
        
        translation_keys = set(translation_data.keys())
        
        # Check for missing keys
        missing_keys = source_keys - translation_keys
        if missing_keys:
            errors_found = True
            print(f"{file_name}: Missing {len(missing_keys)} keys")
        
        # Check for extra keys
        extra_keys = translation_keys - source_keys
        if extra_keys:
            errors_found = True
            print(f"{file_name}: Extra {len(extra_keys)} keys")
        
        # Check that original texts match
        original_mismatch: List[str] = []
        for key in translation_keys & source_keys:
            if (key in source_originals and isinstance(translation_data[key], list) 
                and len(translation_data[key]) >= 2):
                source_original = source_originals[key]
                translation_original = translation_data[key][0]
                if source_original != translation_original:
                    original_mismatch.append(key)
        
        if original_mismatch:
            errors_found = True
            print(f"{file_name}: {len(original_mismatch)} mismatched originals")
    
    if errors_found:
        print("Inconsistencies found in translation files")
    else:
        print("All translation files are consistent")

def generate_missing_keys_template():
    """Generate a template for missing keys"""
    translations_dir = find_translations_dir()
    if not translations_dir:
        return
    
    source_file = translations_dir / "en_US.json"
    source_data = load_json_file(source_file)
    if not source_data:
        return
    
    for file_name in ["fr_FR.json", "ru_RU.json", "zh_HANS.json"]:
        file_path = translations_dir / file_name
        translation_data = load_json_file(file_path)
        if not translation_data:
            continue
        
        source_keys = set(source_data.keys())
        translation_keys = set(translation_data.keys())
        missing_keys = source_keys - translation_keys
        
        if missing_keys:
            template_file = translations_dir / f"missing_keys_{file_name}"
            template_data = {}
            for key in sorted(missing_keys):
                if key in source_data:
                    original_text = source_data[key][0]
                    template_data[key] = [original_text, "TODO: Translate"]
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)
            print(f"Generated: {template_file.name}")

if __name__ == "__main__":
    check_translation_files()
    generate_missing_keys_template()