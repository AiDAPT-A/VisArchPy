import os
import json

def init():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    default_settings_file = os.path.join(current_dir, "../default-settings.json")
    with open(default_settings_file, "r") as f:
        default_settings = json.load(f)

    return default_settings
