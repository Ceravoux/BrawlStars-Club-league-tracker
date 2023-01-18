"""
Simple Official Brawl Stars API Wrapper
"""
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


from . import models as models
from .http import *