import bpy
import json
import os
from os import listdir
from os.path import isfile, join

tooltips_dictionary = {}
interface_dictionary = {}
new_data_dictionary = {}
current_language = ""


def UpdateDict(local, tooltips=True, interface=True, new_data=True):
    # Try to found lang file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lang_path = os.path.join(dir_path, "local_list")
    onlyfiles = [f for f in listdir(lang_path) if isfile(join(lang_path, f))]

    for file in onlyfiles:
        if file == local+".json":
            with open(os.path.join(lang_path, file)) as json_file:
                data = json.load(json_file)

                if tooltips:
                    for key, value in data['tooltips'].items():
                        tooltips_dictionary[key] = value

                if interface:
                    for key, value in data['interface'].items():
                        interface_dictionary[key] = value

                if new_data:
                    for key, value in data['new_data'].items():
                        new_data_dictionary[key] = value


def InitLanguages(locale):
    prefs = bpy.context.preferences
    view = prefs.view

    tooltips_dictionary.clear()
    interface_dictionary.clear()
    new_data_dictionary.clear()

    UpdateDict("en_US")  # Get base lang
    # Update base lang with local lang if file exist
    UpdateDict(locale, view.use_translate_tooltips, view.use_translate_interface, view.use_translate_new_dataname)
    current_language = locale


def CheckCurrentLanguage():
    from bpy.app.translations import locale  # Change with language
    if current_language != locale:
        InitLanguages(locale)

# Translate function


def Translate_Tooltips(phrase: str):
    """
    Translate the give phrase into Blender’s current language.
    """
    CheckCurrentLanguage()

    if phrase in tooltips_dictionary:
        return tooltips_dictionary[phrase]
    else:
        print("Error, in languages text ID not found: " + phrase)
        return phrase


def Translate_Interface(phrase: str):
    """
    Translate the give phrase into Blender’s current language.
    """
    CheckCurrentLanguage()

    if phrase in interface_dictionary:
        return interface_dictionary[phrase]
    else:
        print("Error, in languages text ID not found: " + phrase)
        return phrase


def Translate_NewData(phrase: str):
    """
    Translate the give phrase into Blender’s current language.
    """
    CheckCurrentLanguage()

    if phrase in new_data_dictionary:
        return new_data_dictionary[phrase]
    else:
        print("Error, in languages text ID not found: " + phrase)
        return phrase


def tt(phrase: str):
    return Translate_Tooltips(phrase)


def ti(phrase: str):
    return Translate_Interface(phrase)


def td(phrase: str):
    return Translate_NewData(phrase)
