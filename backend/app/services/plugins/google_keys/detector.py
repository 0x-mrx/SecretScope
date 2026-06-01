import os
from app.services.plugins.base import BasePlugin

class GoogleKeysDetector(BasePlugin):
    def __init__(self):
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(plugin_dir)
