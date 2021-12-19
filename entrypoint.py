import os

from app import create_app

# Get the configuration file from the settings module
# that should be used for this environment
settings_module = os.getenv('APP_SETTINGS_MODULE')

# Create the app with the given settings
app = create_app(settings_module)