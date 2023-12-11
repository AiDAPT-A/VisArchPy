import os

def init():
    default_settings_file = os.path.join(current_dir, "../default-settings.json")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(default_settings_file, "r") as f:
        global default_settings 
        dafault_settings = json.load(f)
