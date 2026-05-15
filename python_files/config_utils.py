import os
import sys


def get_resource_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_exe_dir():
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


TIERS = [
    "Glossa mà activa S1",
    "Glossa mà passiva S1",
    "Glossa mà activa S2",
    "Glossa mà passiva S2",
]


base_path = get_resource_path()
script_dir = get_exe_dir()

os.environ["PATH"] = script_dir + os.pathsep + os.environ.get("PATH", "")
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(script_dir)
    except Exception as e:
        print(f"Note: Could not add DLL directory: {e}")

EAF_ORIGINAL_PATH = os.path.join(script_dir, "ELAN")
EAF_TEMP_PATH = os.path.join(script_dir, "ELAN_temporary")
SUB_FILES_PATH = os.path.join(script_dir, "Subtitles")
CONFIG_PATH = os.path.join(script_dir, "config.json")
ICON_PATH = os.path.join(base_path, "logo.png")

for folder in [EAF_TEMP_PATH, SUB_FILES_PATH]:
    if not os.path.exists(folder):
        os.makedirs(folder)
