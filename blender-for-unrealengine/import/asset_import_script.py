# This script was generated with the addons Blender for UnrealEngine : https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# It will import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation and Pose
# The script must be used in Unreal Engine Editor with Python plugins : https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python
# Use this command in Unreal cmd consol: py "[ScriptLocation]\ImportSequencerScript.py"


def CheckTasks():
    import unreal
    if hasattr(unreal, 'EditorAssetLibrary') == False:
        print('--------------------------------------------------')
        print('/!\ Warning: Editor Scripting Utilities should be activated.')
        print('Plugin > Scripting > Editor Scripting Utilities.')
        return False
    if hasattr(unreal.MovieSceneSequence, 'set_display_rate') == False:
        print('--------------------------------------------------')
        print('/!\ Warning: Editor Scripting Utilities should be activated.')
        print('Plugin > Scripting > Sequencer Scripting.')
        return False
    return True


def CreateSequencer():

    #Process import
    print('========================= Import started ! =========================')

print("Start")

if CheckTasks():
    print(CreateSequencer())

print("End")
