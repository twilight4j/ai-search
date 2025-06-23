"""
Core package for AI Search API
"""

from .config import Settings
from .search_engine import SearchEngineManager

__all__ = [
    "Settings",
    "SearchEngineManager"
]
