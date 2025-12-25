"""
Package core - exports principaux
"""
import sys
from pathlib import Path

# Ajoute le répertoire config au path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ré-export des modules
from .ai_provider import AIProvider
from .database_manager import DatabaseManager
from .data_processor import DataCleaner
from .insightbot_gpt import InsightBotGPT
#from .prompt_templates import PromptTemplates
from .prompt_templates import create_analysis_prompt, SYSTEM_PROMPT_TEMPLATE

__all__ = [
    'AIProvider',
    'DatabaseManager', 
    'DataCleaner',
    'InsightBotGPT',
    'create_analysis_prompt'
]