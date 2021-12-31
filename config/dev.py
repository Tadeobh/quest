from config import *
from os import getenv

# Set the App Enviroment to Development
APP_ENV = APP_ENV_DEVELOPMENT

# Database configuration
QUEST_DB_URI = getenv("MONGODB_URI")
QUEST_DB_NAME = "test_quest"