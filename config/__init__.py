from os import getenv
from os.path import abspath, dirname


# Define app's directory
BASE_DIR = dirname(dirname(abspath(__file__)))

# Secret Key
SECRET_KEY = getenv("SECRET_KEY")

# App environments
APP_ENV_LOCAL = 'local'
APP_ENV_TESTING = 'testing'
APP_ENV_DEVELOPMENT = 'development'
APP_ENV_STAGING = 'staging'
APP_ENV_PRODUCTION = 'production'
APP_ENV = ''