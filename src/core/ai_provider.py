"""ai_provider.py - Fournisseur IA hybride avec auto-fallback robuste"""

import json
import re
import time
import logging
from typing import Dict, List, Any, Optional
import requests
import yaml
from datetime import datetime
# Par :
try:
    import google.generativeai as genai
    # Garder pour compatibilité
except ImportError:
    try:
        # Essayer la nouvelle API
        import google.genai as genai
    except ImportError:
        genai = None
        print("⚠️ Google AI API non disponible")
import openai
import sys
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION DES CHEMINS - CORRIGÉ
# ============================================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # src/core → src → InsightBot

# Ajouter au path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    # Essayer d'abord d'importer depuis config.settings
    from config.settings import settings
    print(f"✅ Settings importé depuis config.settings")
    
except ImportError as e:
    print(f"⚠️ Import échoué via config.settings: {e}")
    
    # Alternative: importer directement si le module existe
    try:
        # Ajouter config au path
        config_dir = project_root / "config"
        if str(config_dir) not in sys.path:
            sys.path.insert(0, str(config_dir))
        
        from settings import settings
        print(f"✅ Settings importé directement depuis {config_dir}")
        
    except ImportError as e2:
        print(f"⚠️ Import direct échoué: {e2}")
        
        # Charger directement depuis le YAML
        model_config_path = project_root / "src" / "core" / "model_config.yaml"
        if model_config_path.exists():
            with open(model_config_path, 'r', encoding='utf-8') as f:
                model_config = yaml.safe_load(f)
            print("✅ Model config chargé directement depuis YAML")
        else:
            model_config = {}
            print("⚠️ model_config.yaml non trouvé")
        
        # Créer settings factice avec valeurs du .env
        class SimpleSettings:
            AI_MODE = os.getenv("AI_MODE", "hybrid")
            PRIMARY_AI_PROVIDER = os.getenv("PRIMARY_AI_PROVIDER", "gemini")
            FALLBACK_AI_PROVIDER = os.getenv("FALLBACK_AI_PROVIDER", "ollama")
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
            OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest")
            MAX_TOKENS = 2000
            TEMPERATURE = 0.1
            TOP_P = 0.9
            
            def get_ai_config(self):
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
                    "top_p": self.TOP_P
                }
                
                # Ajouter la configuration des modèles si disponible
                if hasattr(self, 'model_config') and self.model_config:
                    config["model_config"] = self.model_config
                
                return config
        
        settings = SimpleSettings()
        settings.model_config = model_config
        print("✅ Settings factices créés avec variables d'environnement")

# ============================================================================
# VÉRIFICATION DE LA CONFIGURATION
# ============================================================================

print(f"📊 Configuration chargée:")
print(f"  Mode IA: {getattr(settings, 'AI_MODE', 'inconnu')}")
print(f"  Primary: {getattr(settings, 'PRIMARY_AI_PROVIDER', 'inconnu')}")
print(f"  Fallback: {getattr(settings, 'FALLBACK_AI_PROVIDER', 'inconnu')}")
print(f"  Gemini API Key: {'✅ Présente' if getattr(settings, 'GEMINI_API_KEY', '') else '❌ Absente'}")
print(f"  OpenAI API Key: {'✅ Présente' if getattr(settings, 'OPENAI_API_KEY', '') else '❌ Absente'}")

# Configuration de logging
logging.basicConfig(
    level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AIProvider:
    """Fournisseur IA hybride avec fallback automatique"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation avec détection intelligente des fournisseurs"""
        try:
            self.config = config or settings.get_ai_config()
        except AttributeError:
            # Fallback si settings n'a pas get_ai_config
            self.config = {
                "mode": getattr(settings, 'AI_MODE', 'hybrid'),
                "primary_provider": getattr(settings, 'PRIMARY_AI_PROVIDER', 'gemini'),
                "fallback_provider": getattr(settings, 'FALLBACK_AI_PROVIDER', 'ollama'),
                "gemini_api_key": getattr(settings, 'GEMINI_API_KEY', ''),
                "openai_api_key": getattr(settings, 'OPENAI_API_KEY', ''),
                "ollama_host": getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434'),
                "ollama_timeout": getattr(settings, 'OLLAMA_TIMEOUT', 120),
                "ollama_model": getattr(settings, 'OLLAMA_MODEL', 'qwen2.5-coder:latest'),
                "max_tokens": 2000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        
        self.logger = logging.getLogger("ai_provider")
        
        # Charger la configuration du YAML
        try:
            model_config_path = project_root / "src" / "core" / "model_config.yaml"
            if model_config_path.exists():
                with open(model_config_path, 'r', encoding='utf-8') as f:
                    self.model_config = yaml.safe_load(f)
                print("✅ Model config chargé depuis YAML")
            else:
                self.model_config = {}
                print("⚠️ model_config.yaml non trouvé")
        except Exception as e:
            self.model_config = {}
            print(f"⚠️ Erreur chargement YAML: {e}")
            
        # Configuration des timeouts
        if self.model_config and self.model_config.get("timeouts"):
            timeouts = self.model_config["timeouts"]
            self.timeout = timeouts.get("total", 45)
        else:
            self.timeout = self.config.get("ollama_timeout", 120)
            
        self.max_retries = 3
        
        # État des fournisseurs
        self._providers_status = {
            "gemini": False,
            "openai": False,
            "ollama": False,
            "local": True  # Toujours disponible
        }
        
        self._available_models = []
        self._active_provider = None
        self._fallback_chain = []
        
        # Initialisation des clients API
        self._gemini_client = None
        self._openai_client = None
        
        self.logger.info("🧠 Initialisation AIProvider (Mode: %s)", self.config["mode"])
        
        # Détection automatique
        self._discover_providers()
        self._setup_fallback_chain()
    
    def _discover_providers(self):
        """Détection intelligente des fournisseurs IA disponibles"""
        
        # 1. Détection Gemini
        if self.config.get("gemini_api_key"):
            try:
                genai.configure(api_key=self.config["gemini_api_key"])
                # Simple test de connexion
                list(genai.list_models())
                self._providers_status["gemini"] = True
                self._gemini_client = genai
                self.logger.info("✅ Gemini disponible")
            except Exception as e:
                self.logger.warning("❌ Gemini non disponible: %s", str(e))
        
        # 2. Détection OpenAI
        if self.config.get("openai_api_key"):
            try:
                self._openai_client = openai.OpenAI(api_key=self.config["openai_api_key"])
                # Test simple
                self._openai_client.models.list()
                self._providers_status["openai"] = True
                self.logger.info("✅ OpenAI disponible")
            except Exception as e:
                self.logger.warning("❌ OpenAI non disponible: %s", str(e))
        
        # 3. Détection Ollama
        try:
            response = requests.get(
                f"{self.config['ollama_host']}/api/tags",
                timeout=10
            )
            
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                self._available_models = [
                    {"name": m["name"], "provider": "ollama"} 
                    for m in models_data
                ]
                
                if self._available_models:
                    self._providers_status["ollama"] = True
                    self.logger.info("📦 Modèles Ollama disponibles: %s", 
                                   [m["name"] for m in self._available_models])
        except Exception as e:
            self.logger.warning("❌ Ollama non disponible: %s", str(e))
        
        self.logger.info("État des fournisseurs: %s", self._providers_status)
    
    def _setup_fallback_chain(self):
        """Configure la chaîne de fallback basée sur le mode et les modèles disponibles"""
        mode = self.config["mode"]
        
        if mode == "hybrid":
            # Chaîne: Gemini -> OpenAI -> Ollama -> Local
            self._fallback_chain = ["gemini", "openai", "ollama", "local"]
        elif mode == "cloud":
            # Chaîne: Gemini -> OpenAI -> Local
            self._fallback_chain = ["gemini", "openai", "local"]
        elif mode == "local":
            # Chaîne: Ollama -> Local
            self._fallback_chain = ["ollama", "local"]
        else:
            # Fallback par défaut
            self._fallback_chain = ["local"]
        
        # Filtrer les fournisseurs non disponibles
        available_chain = []
        for provider in self._fallback_chain:
            if self._providers_status.get(provider, False) or provider == "local":
                available_chain.append(provider)
        
        self._fallback_chain = available_chain
        self._active_provider = self._fallback_chain[0] if self._fallback_chain else "local"
        
        self.logger.info("Chaîne de fallback: %s", self._fallback_chain)
        self.logger.info("Fournisseur actif: %s", self._active_provider)
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Appel à Ollama avec sélection intelligente du modèle et configuration YAML"""
        try:
            # Sélection du modèle avec configuration YAML
            model_name = self._select_ollama_model_with_config()
            if not model_name:
                return None
            
            # Récupérer la configuration du modèle depuis YAML
            model_config = self._get_model_config(model_name)
            
            # Préparer le payload avec configuration YAML
            payload = {
                "model": model_name,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
                "format": "json"
            }
            
            # Options depuis la configuration YAML
            options = {}
            if model_config:
                options.update({
                    "temperature": model_config.get("temperature", self.config["temperature"]),
                    "top_p": model_config.get("top_p", self.config["top_p"]),
                    "num_predict": model_config.get("num_predict", self.config["max_tokens"])
                })
            else:
                options.update({
                    "temperature": self.config["temperature"],
                    "top_p": self.config["top_p"],
                    "num_predict": self.config["max_tokens"]
                })
            
            payload["options"] = options
            
            # Timeout spécifique au modèle
            timeout = model_config.get("timeout", self.timeout) if model_config else self.timeout
            
            response = requests.post(
                f"{self.config['ollama_host']}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_response = data.get("response", "")
                
                json_response = self._extract_json_robust(raw_response)
                
                if json_response:
                    return {
                        "response": json_response,
                        "tokens": data.get("eval_count", 0),
                        "success": True
                    }
        
        except requests.exceptions.Timeout:
            self.logger.warning("Timeout Ollama pour le modèle %s", model_name)
            # Marquer le modèle comme potentiellement problématique
            self._mark_model_problematic(model_name)
            raise Exception(f"Timeout Ollama pour {model_name}")
        except Exception as e:
            self.logger.error("Erreur Ollama avec %s: %s", model_name, str(e))
            self._mark_model_problematic(model_name)
            raise
        
        return None
    
    # def _select_ollama_model_with_config(self) -> Optional[str]:
    #     """Sélection intelligente du modèle Ollama en évitant ceux qui timeout"""
    #     if not self._available_models:
    #         return None
        
    #     # Filtrer les modèles problématiques (ceux qui timeout souvent)
    #     available_models = [m for m in self._available_models if "gemma2:2b" not in m["name"]]
        
    #     if not available_models:
    #         available_models = self._available_models  # Fallback
        
    #     # Priorité 1: Modèle configuré dans settings
    #     preferred = self.config.get("ollama_model")
        
    #     # Chercher d'abord parmi les modèles avec configuration YAML
    #     if self.model_config and "models" in self.model_config:
    #         yaml_models = list(self.model_config["models"].keys())
            
    #         # Priorité: modèles configurés dans YAML, triés par priorité
    #         sorted_yaml_models = sorted(
    #             yaml_models,
    #             key=lambda m: self.model_config["models"].get(m, {}).get("priority", 999)
    #         )
            
    #         # Éviter gemma2:2b qui timeout
    #         safe_yaml_models = [m for m in sorted_yaml_models if "gemma2:2b" not in m]
            
    #         for yaml_model in safe_yaml_models:
    #             # Vérifier si ce modèle est disponible
    #             for available_model in available_models:
    #                 if yaml_model in available_model["name"]:
    #                     self.logger.info("✅ Sélection modèle YAML: %s (priorité: %d)", 
    #                                 yaml_model,
    #                                 self.model_config["models"][yaml_model].get("priority", 999))
    #                     return available_model["name"]
        
    #     # Priorité 2: Modèle préféré de settings (éviter gemma2:2b)
    #     if preferred and "gemma2:2b" not in preferred:
    #         for model in available_models:
    #             if preferred in model["name"]:
    #                 self.logger.info("✅ Sélection modèle settings: %s", model["name"])
    #                 return model["name"]
        
    #     # Priorité 3: Prendre qwen2.5 ou llama3.2 plutôt que gemma2:2b
    #     for model in available_models:
    #         if "qwen2.5" in model["name"]:
    #             self.logger.info("✅ Sélection qwen2.5 (évite gemma2:2b): %s", model["name"])
    #             return model["name"]
    #         elif "llama3.2" in model["name"]:
    #             self.logger.info("✅ Sélection llama3.2 (évite gemma2:2b): %s", model["name"])
    #             return model["name"]
        
    #     # Priorité 4: Premier modèle disponible qui n'est pas gemma2:2b
    #     safe_models = [m for m in available_models if "gemma2:2b" not in m["name"]]
    #     if safe_models:
    #         first_model = safe_models[0]["name"]
    #         self.logger.info("✅ Sélection premier modèle safe: %s", first_model)
    #         return first_model
        
    #     # Dernier recours: premier modèle
    #     first_model = available_models[0]["name"]
    #     self.logger.info("⚠️ Sélection dernier recours: %s", first_model)
    #     return first_model
    
    def _select_ollama_model_with_config(self) -> Optional[str]:
        """Sélectionne le modèle Ollama selon les priorités du YAML"""
        if not self._available_models:
            self.logger.error("❌ Aucun modèle disponible dans Ollama")
            return None

        # On récupère les noms propres (ex: 'qwen2.5-coder:7b')
        available_names = [m["name"] for m in self._available_models]
        
        # 1. Chercher dans le YAML par ordre de priorité
        if self.model_config and "models" in self.model_config:
            # Tri par priorité (1, 2, 3...)
            sorted_cfg = sorted(
                self.model_config["models"].items(), 
                key=lambda x: x[1].get("priority", 999)
            )
            
            for model_key, config in sorted_cfg:
                # On nettoie la clé du YAML pour le matching (enlever les espaces)
                clean_key = model_key.strip()
                
                for full_name in available_names:
                    # Si 'phi3:mini' est dans 'phi3:mini' ou 'phi3:latest'
                    # On utilise une vérification flexible
                    if clean_key in full_name or full_name in clean_key:
                        self.logger.info(f"🎯 Modèle sélectionné: {full_name} [Priorité {config.get('priority')}]")
                        return full_name

        # 2. Fallback sur le modèle par défaut du .env / settings
        preferred = self.config.get("ollama_model")
        if preferred:
            for full_name in available_names:
                if preferred in full_name:
                    return full_name
                    
        # 3. Dernier recours absolu : le premier modèle qu'on trouve
        self.logger.warning(f"⚠️ Aucun match YAML, utilisation du premier modèle dispo: {available_names[0]}")
        return available_names[0]
    
    def _get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Récupère la configuration d'un modèle spécifique depuis YAML"""
        if not self.model_config or "models" not in self.model_config:
            return {}
        
        # Chercher la configuration correspondant au modèle
        for yaml_model_name, config in self.model_config["models"].items():
            if yaml_model_name in model_name:
                return config
        
        return {}
    
    def _mark_model_problematic(self, model_name: str):
        """Marque un modèle comme potentiellement problématique (pour future évolution)"""
        # Pourrait être implémenté avec un cache pour éviter les modèles problématiques
        self.logger.warning("Modèle marqué comme potentiellement problématique: %s", model_name)
    
    def ask_ai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Demande à l'IA avec fallback automatique et gestion robuste"""
        result = {
            "success": False,
            "response": None,
            "provider": None,
            "tokens": 0,
            "error": None,
            "execution_time": 0,
            "fallback_used": False
        }
        
        start_time = time.time()
        original_provider = self._active_provider
        
        # Essayer chaque fournisseur dans la chaîne
        for provider in self._fallback_chain:
            try:
                self._active_provider = provider
                self.logger.info("Tentative avec %s", provider)
                
                response = self._call_provider(system_prompt, user_prompt)
                
                if response and response.get("success", False):
                    result.update(response)
                    result["provider"] = provider
                    result["success"] = True
                    
                    if provider != original_provider:
                        result["fallback_used"] = True
                        self.logger.warning("Fallback activé: %s -> %s", 
                                          original_provider, provider)
                    
                    break
                else:
                    self.logger.warning("Échec avec %s", provider)
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error("Erreur avec %s: %s", provider, error_msg)
                
                # Si c'est une erreur de quota (429), on passe au suivant
                if "429" in error_msg or "quota" in error_msg.lower():
                    self.logger.warning("Quota épuisé pour %s", provider)
                    continue
                
                # Si c'est un timeout, on réessaie avec le même fournisseur une fois
                if "timeout" in error_msg.lower() and self.max_retries > 0:
                    try:
                        self.logger.info("Retry après timeout avec %s", provider)
                        time.sleep(1)
                        response = self._call_provider(system_prompt, user_prompt)
                        if response and response.get("success", False):
                            result.update(response)
                            result["provider"] = provider
                            result["success"] = True
                            break
                    except Exception:
                        pass
        
        # Fallback local si tout échoue
        if not result["success"]:
            self.logger.error("Tous les fournisseurs ont échoué, fallback local")
            result = self._local_fallback(system_prompt, user_prompt)
            result["provider"] = "local_fallback"
            result["success"] = True
        
        result["execution_time"] = time.time() - start_time
        return result
    

    
    
    def _call_provider(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Appelle le fournisseur actif"""
        provider_methods = {
            "gemini": self._call_gemini,
            "openai": self._call_openai,
            "ollama": self._call_ollama,
            "local": self._local_fallback
        }
        
        method = provider_methods.get(self._active_provider)
        if not method:
            return None
        
        return method(system_prompt, user_prompt)
    
    # def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
    #     """Appel à Gemini API avec compatibilité ancienne/nouvelle API"""
    #     try:
    #         if not self._gemini_client or genai is None:
    #             return None
            
    #         # Essayer différents modèles Gemini
    #         gemini_models = [
    #             "gemini-2.0-flash",  # Nouveau modèle rapide et gratuit
    #             "gemini-1.0-pro",    # Alternative
    #             "gemini-pro"                # Ancien nom
    #         ]
            
    #         for model_name in gemini_models:
    #             try:
    #                 self.logger.info(f"Essai avec modèle Gemini: {model_name}")
                    
    #                 # Créer le modèle
    #                 model = genai.GenerativeModel(model_name)
                    
    #                 # Préparer le contenu selon l'API
    #                 content = f"{system_prompt}\n\n{user_prompt}"
                    
    #                 # Générer la réponse
    #                 response = model.generate_content(
    #                     content,
    #                     generation_config={
    #                         "temperature": self.config["temperature"],
    #                         "top_p": self.config["top_p"],
    #                         "max_output_tokens": self.config["max_tokens"],
    #                     }
    #                 )
                    
    #                 raw_response = response.text
    #                 json_response = self._extract_json_robust(raw_response)
                    
    #                 if json_response:
    #                     self.logger.info(f"✅ Succès avec {model_name}")
    #                     return {
    #                         "response": json_response,
    #                         "tokens": len(raw_response.split()),
    #                         "success": True
    #                     }
                        
    #             except Exception as model_error:
    #                 self.logger.warning(f"Échec avec {model_name}: {str(model_error)[:100]}")
    #                 continue
            
    #         # Si tous les modèles ont échoué
    #         self.logger.error("Tous les modèles Gemini ont échoué")
    #         return None
        
        # except Exception as e:
        #     error_msg = str(e)
        #     self.logger.error(f"Erreur Gemini: {error_msg}")
            
        #     if "429" in error_msg:
        #         self.logger.error("Quota Gemini épuisé")
        #         raise Exception("Quota épuisé")
            
        #     if "API key" in error_msg or "invalid" in error_msg.lower():
        #         raise Exception("Clé API Gemini invalide")
                
        #     raise

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
            """
            Appel à Gemini API avec support natif du mode JSON et instructions système.
            Optimisé pour Gemini 2.0 Flash.
            """
            try:
                if not self._gemini_client or genai is None:
                    return None
                
                # Liste des modèles par ordre de préférence
                gemini_models = [
                    "gemini-2.0-flash",    # Le plus rapide et performant actuellement
                    "gemini-1.5-flash",    # Excellente alternative
                    "gemini-1.5-pro"       # Plus puissant mais plus lent
                ]
                
                for model_name in gemini_models:
                    try:
                        self.logger.info(f"🚀 Tentative Gemini avec modèle: {model_name}")
                        
                        # Configuration du modèle avec les instructions système séparées
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=system_prompt
                        )
                        
                        # Configuration de la génération
                        generation_config = {
                            "temperature": self.config.get("temperature", 0.1),
                            "top_p": self.config.get("top_p", 0.9),
                            "max_output_tokens": self.config.get("max_tokens", 2000),
                            "response_mime_type": "application/json"  # Force Gemini à sortir du JSON pur
                        }
                        
                        # Appel API (on n'envoie que le prompt utilisateur car le système est déjà chargé)
                        response = model.generate_content(
                            user_prompt,
                            generation_config=generation_config,
                            request_options={"timeout": 30} # Timeout réseau
                        )
                        
                        if not response or not response.text:
                            continue

                        # Nettoyage et validation du JSON
                        raw_text = response.text.strip()
                        json_response = self._extract_json_robust(raw_text)
                        
                        if json_response:
                            self.logger.info(f"✅ Succès Gemini ({model_name})")
                            return {
                                "response": json_response,
                                "tokens": len(raw_text.split()), # Estimation simple
                                "success": True,
                                "model_used": model_name
                            }
                            
                    except Exception as model_error:
                        # Si c'est une erreur de quota (429), on arrête d'insister sur Gemini
                        if "429" in str(model_error) or "quota" in str(model_error).lower():
                            self.logger.warning(f"⚠️ Quota épuisé pour {model_name}")
                            raise Exception("Quota Gemini atteint") # Force le passage au fallback suivant
                        
                        self.logger.warning(f"❌ Échec partiel {model_name}: {str(model_error)[:100]}")
                        continue # Teste le modèle suivant dans la liste
                
                return None
                
            except Exception as e:
                self.logger.error(f"🚨 Erreur critique Gemini: {str(e)}")
                # On relance l'exception pour que ask_ai puisse passer à Ollama/OpenAI
                raise e
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Appel à OpenAI API"""
        try:
            if not self._openai_client:
                return None
            
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                top_p=self.config["top_p"]
            )
            
            raw_response = response.choices[0].message.content
            json_response = self._extract_json_robust(raw_response)
            
            if json_response:
                return {
                    "response": json_response,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                    "success": True
                }
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                self.logger.error("Quota OpenAI épuisé")
                raise Exception("Quota épuisé")
            raise
        
        return None
    
    def _local_fallback(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Fallback local intelligent"""
        self.logger.info("Utilisation du fallback local")
        
        # Génération d'une réponse basique mais structurée
        response = {
            "sql_query": "SELECT 'Fallback activé' as message",
            "insight": "Je suis actuellement en mode local. Voici une analyse basique de votre requête.",
            "visualization": {"type": "info", "x": "message", "y": "value"},
            "business_recommendations": [
                "Mode local activé",
                "Fonctionnalités limitées",
                "Connectez-vous à un fournisseur IA pour des analyses complètes"
            ]
        }
        
        return {
            "response": response,
            "tokens": 0,
            "success": True
        }
    
    def _extract_json_robust(self, text: str) -> Optional[Dict[str, Any]]:
        """Extraction robuste de JSON avec plusieurs stratégies"""
        if not text:
            return None
        
        # Tentative 1: JSON complet
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Tentative 2: Extraction avec regex
        json_patterns = [
            r'\{.*\}',  # JSON objet
            r'\[.*\]',  # JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Tentative 3: Réparation agressive
        repaired = self._repair_json_aggressive(text)
        if repaired:
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass
        
        self.logger.error("Impossible d'extraire JSON: %s", text[:500])
        return None
    
    def _repair_json_aggressive(self, text: str) -> Optional[str]:
        """Réparation agressive de JSON malformé"""
        if not text:
            return None
        
        text = text.strip()
        
        # Trouver le début et la fin du JSON
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            return None
        
        json_text = text[start:end+1]
        
        # Correction des guillemets manquants pour les clés
        json_text = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_text)
        
        # Correction des virgules terminales
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        # Correction des guillemets simples -> doubles
        json_text = json_text.replace("'", '"')
        
        return json_text
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état du fournisseur IA"""
        return {
            "providers": self._providers_status,
            "active_provider": self._active_provider,
            "fallback_chain": self._fallback_chain,
            "available_models": self._available_models,
            "model_config_loaded": bool(self.model_config)
        }
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Compatibilité avec l'ancienne interface.
        Args:
            prompt: Le prompt utilisateur
            **kwargs: Peut inclure 'system_prompt', 'provider', etc.
        """
        # Extraire les arguments
        system_prompt = kwargs.get("system_prompt", "Tu es un assistant utile.")
        user_prompt = kwargs.get("user_prompt", prompt)
        provider = kwargs.get("provider")
        
        # Si un provider spécifique est demandé, l'utiliser
        if provider and provider in self._fallback_chain:
            self._active_provider = provider
        
        # Appeler ask_ai
        result = self.ask_ai(system_prompt, user_prompt)
        
        if result.get("success"):
            response_data = result.get("response", {})
            
            # Si c'est un dict, convertir en JSON string
            if isinstance(response_data, dict):
                return json.dumps(response_data, ensure_ascii=False, indent=2)
            
            # Sinon retourner tel quel
            return str(response_data)
        
        # En cas d'erreur
        error_msg = result.get("error", "Erreur inconnue")
        return f"Erreur: {error_msg}"


# Test rapide
if __name__ == "__main__":
    print("🧪 Test AIProvider...")
    provider = AIProvider()
    print(f"✅ AIProvider initialisé")
    print(f"   Mode: {provider.config.get('mode')}")
    print(f"   Chaîne de fallback: {provider._fallback_chain}")