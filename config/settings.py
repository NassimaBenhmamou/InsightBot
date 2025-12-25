"""settings.py - Configuration avec support model_config.yaml"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
# CORRECTION ICI : utiliser pydantic.v1
from pydantic.v1 import BaseSettings

# Ajouter le répertoire parent au path pour permettre les imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

class Settings(BaseSettings):
    _model_config: Dict[str, Any] = {}
    # Chemins
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_DIR: Path = DATA_DIR / "database"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    LOGS_DIR: Path = BASE_DIR / "logs"
    SRC_DIR: Path = BASE_DIR / "src"
    CORE_DIR: Path = SRC_DIR / "core"
    
    # Mode IA
    AI_MODE: str = "hybrid"
    PRIMARY_AI_PROVIDER: str = "gemini"
    FALLBACK_AI_PROVIDER: str = "ollama"
    
    # Clés API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Configuration Ollama (peut être override par model_config.yaml)
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_MODEL: str = "qwen2.5-coder:latest"
    
    # Hyperparamètres par défaut (peuvent être override)
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.1
    TOP_P: float = 0.9
    
    # Base de données
    DATABASE_PATH: str = str(DATABASE_DIR / "insightbot.db")
    MAX_SQL_RETRIES: int = 3
    SQL_QUERY_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(LOGS_DIR / "insightbot.log")
    
    # Application
    APP_NAME: str = "InsightBot AI"
    APP_VERSION: str = "2.2.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuration modèle YAML
    MODEL_CONFIG_PATH: Path = CORE_DIR / "model_config.yaml"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_config_data = self._load_model_config()
        self._ensure_directories()
     
    
    def _ensure_directories(self):
        """Crée les répertoires nécessaires"""
        directories = [
            self.DATA_DIR,
            self.DATABASE_DIR,
            self.PROCESSED_DIR,
            self.LOGS_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    # def _load_model_config(self) -> Dict[str, Any]:
    #     """Charge la configuration des modèles depuis YAML"""
    #     try:
    #         if self.MODEL_CONFIG_PATH.exists():
    #             with open(self.MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
    #                 config = yaml.safe_load(f)
                
    #             # Fusionner avec les valeurs par défaut
    #             if config and "general" in config:
    #                 general = config["general"]
    #                 self.MAX_TOKENS = general.get("default_max_tokens", self.MAX_TOKENS)
    #                 self.TEMPERATURE = general.get("default_temperature", self.TEMPERATURE)
    #                 self.TOP_P = general.get("default_top_p", self.TOP_P)
                
    #             return config or {}
    #     except Exception as e:
    #         print(f"⚠️ Erreur chargement model_config.yaml: {e}")
        
    #     return {}

    def _load_model_config(self) -> Dict[str, Any]:
        """Charge la configuration des modèles depuis YAML et met à jour les paramètres"""
        try:
            if self.MODEL_CONFIG_PATH.exists():
                with open(self.MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                # On stocke la config brute dans l'attribut privé
                self._model_config = config 
                
                # Mise à jour dynamique des hyperparamètres depuis la section "general"
                if "general" in config:
                    gen = config["general"]
                    # On utilise .get(clé, valeur_par_défaut) pour ne pas écraser si absent
                    self.MAX_TOKENS = gen.get("default_max_tokens", self.MAX_TOKENS)
                    self.TEMPERATURE = gen.get("default_temperature", self.TEMPERATURE)
                    self.TOP_P = gen.get("default_top_p", self.TOP_P)
                    
                    # Optionnel : log de confirmation si DEBUG est True
                    if self.DEBUG:
                        print(f"📊 Configuration YAML appliquée : Tokens={self.MAX_TOKENS}, Temp={self.TEMPERATURE}")
                
                return config
            else:
                print(f"ℹ️ Fichier config non trouvé à : {self.MODEL_CONFIG_PATH}. Utilisation des valeurs par défaut.")
                
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de model_config.yaml: {e}")
        
        return {}
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Configuration IA avec merge model_config.yaml"""
        config = {
            "mode": self.AI_MODE,
            "primary_provider": self.PRIMARY_AI_PROVIDER,
            "fallback_provider": self.FALLBACK_AI_PROVIDER,
            "gemini_api_key": self.GEMINI_API_KEY,
            "openai_api_key": self.OPENAI_API_KEY,
            "ollama_host": self.OLLAMA_HOST,
            "ollama_timeout": self.OLLAMA_TIMEOUT,
            "ollama_model": self.OLLAMA_MODEL,
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
            "top_p": self.TOP_P,
            "model_config": self._model_config,
            "ollama_fallback_models": self.get_ollama_fallback_models()
        }
        
        return config
    
    def get_ollama_fallback_models(self) -> List[str]:
        """Retourne la liste des modèles Ollama configurés"""
        models = []
        if self._model_config and "models" in self._model_config:
            # Trier par priorité
            sorted_models = sorted(
                self._model_config["models"].items(),
                key=lambda x: x[1].get("priority", 999)
            )
            models = [model_name for model_name, _ in sorted_models]
        
        return models
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Récupère la configuration spécifique d'un modèle"""
        if self._model_config and "models" in self._model_config:
            return self._model_config["models"].get(model_name, {})
        return {}
    
    def get_general_config(self) -> Dict[str, Any]:
        """Récupère la configuration générale"""
        if self._model_config and "general" in self._model_config:
            return self._model_config["general"]
        return {}
    
    def get_switching_config(self) -> Dict[str, Any]:
        """Récupère la configuration de basculement"""
        if self._model_config and "switching" in self._model_config:
            return self._model_config["switching"]
        return {}
    
    def get_timeouts_config(self) -> Dict[str, Any]:
        """Récupère la configuration des timeouts"""
        if self._model_config and "timeouts" in self._model_config:
            return self._model_config["timeouts"]
        return {}

settings = Settings()