import os
import sys

def get_resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Example usage in your code
config_path = get_resource_path('config/vgg_transformer.yml')
weights_path = get_resource_path('config/weights/vgg_transformer.pth')

# Use config_path and weights_path in your code

app_config = {
    'OCR_MODEL_PATH': weights_path,  
    'OCR_CFG': config_path,  
    'device': 'cpu'
}
