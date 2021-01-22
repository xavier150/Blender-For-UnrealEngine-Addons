import bpy
import json
import os
from os import listdir
from os.path import isfile, join

dictionary = {}
current_language = ""


def UpdateDict(local):
    # Try to found lang file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lang_path = os.path.join(dir_path, "local_list")
    onlyfiles = [f for f in listdir(lang_path) if isfile(join(lang_path, f))]

    for file in onlyfiles:
        if file == local+".json":
            with open(os.path.join(lang_path, file)) as json_file:
                data = json.load(json_file)
                for key, value in data['dictionary'].items():
                    dictionary[key] = value


def InitLanguages(locale):
    dictionary.clear()
    UpdateDict("en_US")  # Get base lang
    UpdateDict(locale)  # Update base lang with local lang if file exist
    current_language = locale


def CheckCurrentLanguage():
    from bpy.app.translations import locale  # Change with language
    if current_language != locale:
        InitLanguages(locale)


def t(phrase: str):
    """
    Translate the give phrase into Blender’s current language.
    """
    CheckCurrentLanguage()

    try:
        return dictionary[phrase]

    except KeyError:
        print("Error, in languages text ID not found: " + phrase)
        return phrase
