
import sys
import os

sys.path.append(os.getcwd())
from web.backend.config import Config

print(f"DB URI: {Config.SQLALCHEMY_DATABASE_URI}")
