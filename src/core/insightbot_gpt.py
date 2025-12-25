"""
InsightBotGPT - Module principal d'orchestration
Version avec imports corrigés
"""

import json
import numpy as np
import pandas as pd
import re
import time
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# ============================================================================
# CONFIGURATION DES CHEMINS
# ============================================================================

# Déterminer le chemin racine
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
config_path = project_root / "config"

# Ajouter config au sys.path
if str(config_path) not in sys.path:
    sys.path.insert(0, str(config_path))

# ============================================================================
# IMPORT DES SETTINGS - VERSION CORRIGÉE
# ============================================================================

try:
    # Import direct depuis config
    from settings import settings
    print("✅ Settings importé avec succès")
except ImportError as e:
    print(f"⚠️ Import settings échoué: {e}")
    
    # Fallback: créer des settings minimales
    class SimpleSettings:
        MAX_SQL_RETRIES = 3
        AI_MODE = "hybrid"
        PRIMARY_AI_PROVIDER = "gemini"
        FALLBACK_AI_PROVIDER = "ollama"
        APP_VERSION = "2.0.0"
        DATABASE_PATH = "data/database/insightbot.db"
        SQLITE_TIMEOUT = 30
        LOG_LEVEL = "INFO"
        ENABLE_CACHE = True
        CACHE_TTL = 300
        
        def get_ai_config(self, provider=None):
            return {
                "temperature": 0.1,
                "max_tokens": 2000,
                "top_p": 0.9
            }
    
    settings = SimpleSettings()
    print("✅ Settings minimales créées")

# ============================================================================
# IMPORT DES AUTRES MODULES CORE
# ============================================================================

try:
    from core.database_manager import DatabaseManager
    print("✅ DatabaseManager importé")
except ImportError:
    print("⚠️ DatabaseManager non trouvé, tentative alternative...")
    
    # Fallback pour DatabaseManager
    class DatabaseManager:
        def __init__(self):
            self.conn = None
            self.logger = logging.getLogger("DatabaseManager")
        
        def connect(self):
            try:
                import sqlite3
                self.conn = sqlite3.connect(settings.DATABASE_PATH, timeout=settings.SQLITE_TIMEOUT)
                return True
            except Exception as e:
                self.logger.error(f"Erreur connexion DB: {e}")
                return False
        
        def execute_query(self, query, params=None):
            try:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    data = cursor.fetchall()
                    return pd.DataFrame(data, columns=columns)
                else:
                    self.conn.commit()
                    return {"rowcount": cursor.rowcount}
            except Exception as e:
                self.logger.error(f"Erreur requête: {e}")
                raise
        
        def get_tables(self):
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                return [row[0] for row in cursor.fetchall()]
            except:
                return []

try:
    from core.ai_provider import AIProvider
    print("✅ AIProvider importé")
except ImportError:
    print("⚠️ AIProvider non trouvé")
    
    class AIProvider:
        def __init__(self):
            self.logger = logging.getLogger("AIProvider")
            self.active_provider = "local"
        
        def get_status(self):
            return {"active_provider": self.active_provider, "available": True}
        
        def ask_ai(self, system_prompt, user_prompt):
            return {
                "success": False,
                "response": {"sql_query": "SELECT 'AIProvider non disponible' as status"},
                "provider": "local"
            }

# ============================================================================
# IMPORT CORRIGÉ DE PROMPT_TEMPLATES
# ============================================================================

try:
    # Essayer d'abord le chemin relatif
    from prompt_templates import create_analysis_prompt, create_sql_correction_prompt, detect_language
    print("✅ prompt_templates importé avec succès")
except ImportError as e:
    print(f"⚠️ Import prompt_templates échoué: {e}")
    
    # Fonctions de secours
    def detect_language(text):
        """Détecte la langue du texte"""
        if not text:
            return 'fr'
        text_lower = text.lower()
        french_keywords = ['le', 'la', 'les', 'de', 'des', 'du', 'est', 'dans']
        english_keywords = ['the', 'and', 'for', 'with', 'what', 'how']
        french_count = sum(1 for word in french_keywords if word in text_lower.split())
        english_count = sum(1 for word in english_keywords if word in text_lower.split())
        return 'fr' if french_count > english_count else 'en'
    
    def create_analysis_prompt(question, sql_columns, sql_statistics, context=None):
        """Crée un prompt d'analyse simple"""
        # Formater les colonnes
        columns_by_table = {}
        for col in sql_columns:
            table = col.get("table", "unknown")
            if table not in columns_by_table:
                columns_by_table[table] = []
            col_name = col.get("column") or col.get("name", "unknown")
            col_type = col.get("type", "unknown")
            columns_by_table[table].append(f"{col_name} ({col_type})")
        
        schema_text = ""
        for table, columns in columns_by_table.items():
            schema_text += f"\nTable '{table}':"
            for col in columns[:5]:  # Limiter à 5 colonnes par table
                schema_text += f"\n  - {col}"
            if len(columns) > 5:
                schema_text += f"\n  ... et {len(columns) - 5} autres colonnes"
        
        prompt = f"""
        Tu es InsightBot, expert en analyse de données SQL.
        
        Schéma disponible:{schema_text}
        
        Statistiques: {json.dumps(sql_statistics, indent=2)}
        
        Question: {question}
        
        Génère une réponse JSON avec ce format:
        {{
            "sql_query": "SELECT ... (requête SQL valide)",
            "insight": "Explication des résultats...",
            "visualization": {{"type": "bar|line|pie|table", "x": "colonne_x", "y": "colonne_y"}},
            "business_recommendations": ["rec1", "rec2", "rec3"]
        }}
        """
        return {
            "system_prompt": prompt,
            "user_prompt": f"Question: {question}",
            "language": detect_language(question)
        }
    
    def create_sql_correction_prompt(broken_query, error_message, sql_schema, original_question, language="fr"):
        """Crée un prompt pour corriger une requête SQL"""
        prompt = f"""
        Requête SQL erronée: {broken_query}
        
        Erreur: {error_message}
        
        Schéma SQL: {sql_schema}
        
        Question originale: {original_question}
        
        Corrige la requête SQL. Réponds UNIQUEMENT avec la requête SQL corrigée.
        """
        return {
            "system_prompt": prompt,
            "user_prompt": "Corrige cette requête SQL.",
            "language": language
        }
    
    print("✅ Fonctions prompt de secours créées")

# ============================================================================
# CLASSE PRINCIPALE InsightBotGPT - VERSION CORRIGÉE
# ============================================================================

class InsightBotGPT:
    """Orchestrateur principal avec injection dynamique du schéma SQL"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("InsightBotGPT")
        
        # Initialiser le logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
        
        # État d'initialisation
        self._initialized = False
        self._sql_schema_discovered = False
        self._available_sql_columns = []
        self._sql_statistics = {}
        
        # Cache
        self._schema_cache = {}
        self._schema_cache_time = None
        
        # Composants
        self.db = None
        self.ai_provider = None
        
        # Métriques
        self._execution_metrics = {
            "total_questions": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "fallback_used": 0,
            "total_execution_time": 0
        }
        
        self.logger.info("🤖 InsightBotGPT initialisé")
    
    def initialize(self) -> bool:
        """Initialisation complète du système"""
        try:
            if self._initialized:
                self.logger.info("✅ Déjà initialisé")
                return True
            
            self.logger.info("🔧 Démarrage de l'initialisation...")
            
            # 1. Initialiser la base de données
            self.db = DatabaseManager()
            if not self.db.connect():
                self.logger.error("❌ Impossible de se connecter à la base de données")
                return False
            
            # 2. Découvrir le schéma SQL
            self._discover_sql_schema()
            
            # 3. Initialiser le fournisseur IA
            self.ai_provider = AIProvider()
            ai_status = self.ai_provider.get_status() if hasattr(self.ai_provider, 'get_status') else {"active_provider": "local"}
            self.logger.info(f"🧠 Fournisseur IA: {ai_status.get('active_provider', 'inconnu')}")
            
            self._initialized = True
            self.logger.info("✅ Initialisation complète réussie")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Échec critique de l'initialisation: {str(e)}")
            return False
    
    def _discover_sql_schema(self) -> None:
        """Découvre dynamiquement le schéma SQL"""
        try:
            self.logger.info("🔍 Découverte du schéma SQL...")
            
            # Récupérer toutes les tables
            tables = self.db.get_tables()
            if not tables:
                self.logger.warning("⚠️ Aucune table trouvée dans la base de données")
                self._sql_schema_discovered = False
                return
            
            self.logger.info(f"📊 {len(tables)} tables trouvées: {tables}")
            
            # Pour chaque table, récupérer les colonnes
            all_columns = []
            for table in tables:
                try:
                    # Requête pour obtenir les informations de la table
                    query = f"PRAGMA table_info('{table}')"
                    table_info = self.db.execute_query(query)
                    
                    if table_info is not None and not table_info.empty:
                        for _, row in table_info.iterrows():
                            column_info = {
                                "table": table,
                                "column": row["name"],  # "column" pour compatibilité avec prompt_templates
                                "name": row["name"],    # Garder "name" aussi pour compatibilité interne
                                "type": row["type"],
                                "nullable": row["notnull"] == 0
                            }
                            all_columns.append(column_info)
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur analyse table {table}: {e}")
            
            self._available_sql_columns = all_columns
            
            # Initialiser les statistiques SQL
            self._sql_statistics = {
                "total_tables": len(tables),
                "total_columns": len(all_columns),
                "column_count": len(all_columns),
                "tables_found": tables
            }
            
            self._sql_schema_discovered = len(all_columns) > 0
            
            if self._sql_schema_discovered:
                self.logger.info(f"✅ Schéma SQL découvert: {len(all_columns)} colonnes")
                self.logger.info(f"📈 Statistiques SQL: {self._sql_statistics}")
            else:
                self.logger.warning("⚠️ Aucune colonne découverte")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur découverte schéma SQL: {str(e)}")
            self._sql_schema_discovered = False
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """Traite une question utilisateur et retourne une analyse"""
        start_time = time.time()
        self._execution_metrics["total_questions"] += 1
        
        try:
            self.logger.info(f"📝 Traitement question: {question[:100]}...")
            
            # DEBUG: Afficher les informations disponibles
            self.logger.info(f"📊 Colonnes disponibles: {len(self._available_sql_columns)}")
            self.logger.info(f"📈 Statistiques SQL: {self._sql_statistics}")
            
            # Vérifier l'initialisation
            if not self._initialized:
                success = self.initialize()
                if not success:
                    return self._create_error_response("Système non initialisé")
            
            # Détecter la langue
            language = detect_language(question)
            self.logger.info(f"🌍 Langue détectée: {language}")
            
            # ✅ CORRECTION ICI: Utiliser create_analysis_prompt avec les bons paramètres
            prompt_data = create_analysis_prompt(
                question=question,
                sql_columns=self._available_sql_columns,  # Liste de dicts
                sql_statistics=self._sql_statistics,      # Dict
                context={"additional_context": "Base de données: DuckDB"}
            )
            
            self.logger.info(f"📝 Prompt généré (system: {len(prompt_data.get('system_prompt', ''))} chars)")
            
            # Appeler l'IA avec la méthode CORRECTE
            ai_response = self.ai_provider.ask_ai(
                system_prompt=prompt_data["system_prompt"],
                user_prompt=prompt_data["user_prompt"]
            )
            
            if not ai_response.get("success"):
                return self._create_error_response(f"Erreur IA: {ai_response.get('error', 'Erreur inconnue')}")
            
            self.logger.info(f"✅ Réponse IA reçue du provider: {ai_response.get('provider')}")
            
            # Extraire la réponse JSON de l'IA
            ai_data = ai_response.get("response", {})
            
            # DEBUG: Afficher la réponse IA
            self.logger.info(f"📦 Données IA: {json.dumps(ai_data, indent=2)[:500]}...")
            
            # Extraire la requête SQL de la réponse
            sql_query = ai_data.get("sql_query")
            if not sql_query:
                # Fallback: essayer d'extraire du texte
                sql_query = self._extract_sql_query(str(ai_data))
            
            if not sql_query:
                return self._create_error_response("Aucune requête SQL générée")
            
            self.logger.info(f"⚡ Requête SQL à exécuter: {sql_query[:200]}...")
            
            # Exécuter la requête SQL
            query_result = None
            sql_error = None
            
            for attempt in range(settings.MAX_SQL_RETRIES):
                try:
                    query_result = self.db.execute_query(sql_query)
                    self.logger.info(f"✅ Requête SQL exécutée avec succès (tentative {attempt + 1})")
                    break
                except Exception as e:
                    sql_error = str(e)
                    self.logger.warning(f"⚠️ Tentative {attempt + 1} échouée: {sql_error}")
                    
                    if attempt < settings.MAX_SQL_RETRIES - 1:
                        # Essayer de corriger la requête
                        correction_prompt_data = create_sql_correction_prompt(
                            broken_query=sql_query,
                            error_message=sql_error,
                            sql_schema=self._get_schema_info_for_prompt(),
                            original_question=question,
                            language=language
                        )
                        
                        correction_response = self.ai_provider.ask_ai(
                            system_prompt=correction_prompt_data["system_prompt"],
                            user_prompt=correction_prompt_data["user_prompt"]
                        )
                        
                        if correction_response.get("success"):
                            correction_data = correction_response.get("response", {})
                            # Extraire la requête corrigée
                            if isinstance(correction_data, dict):
                                sql_query = correction_data.get("sql_query", sql_query)
                            else:
                                sql_query = self._extract_sql_query(str(correction_data))
                            
                            if sql_query:
                                self.logger.info(f"🔄 Requête corrigée (tentative {attempt + 2}): {sql_query[:200]}...")
                            else:
                                break
                        else:
                            break
            
            if query_result is None:
                return self._create_error_response(f"Échec exécution SQL: {sql_error}")
            
            # Formater la réponse
            execution_time = time.time() - start_time
            self._execution_metrics["successful_queries"] += 1
            self._execution_metrics["total_execution_time"] += execution_time
            
            # Préparer la réponse finale
            response = {
                "success": True,
                "question": question,
                "insight": ai_data.get("insight", self._generate_insight(question, query_result)),
                "data": query_result,
                "sql_query": sql_query,
                "execution": {
                    "time": execution_time,
                    "provider": ai_response.get("provider", "unknown"),
                    "tokens": ai_response.get("tokens", 0),
                    "sql_retries": 0
                },
                "business_recommendations": ai_data.get("business_recommendations", 
                                                        self._generate_recommendations(query_result)),
                "visualization": ai_data.get("visualization", 
                                            self._suggest_visualization(query_result))
            }
            
            self.logger.info(f"✅ Analyse complétée en {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._execution_metrics["failed_queries"] += 1
            self.logger.error(f"❌ Erreur traitement question: {str(e)}", exc_info=True)
            
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "execution": {
                    "time": execution_time,
                    "error": str(e)
                }
            }
    
    def _get_schema_info_for_prompt(self) -> str:
        """Formate les informations du schéma pour le prompt de correction"""
        if not self._available_sql_columns:
            return "Aucun schéma disponible"
        
        schema_by_table = {}
        for col in self._available_sql_columns:
            table = col["table"]
            if table not in schema_by_table:
                schema_by_table[table] = []
            schema_by_table[table].append(f"{col['name']} ({col['type']})")
        
        schema_lines = []
        for table, columns in schema_by_table.items():
            schema_lines.append(f"Table '{table}':")
            schema_lines.extend(f"  - {col}" for col in columns)
        
        return "\n".join(schema_lines)
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """Récupère des exemples de données pour aider l'IA"""
        try:
            sample_data = {}
            tables = self.db.get_tables()[:3]  # Limiter à 3 tables
            
            for table in tables:
                try:
                    query = f"SELECT * FROM \"{table}\" LIMIT 3"
                    data = self.db.execute_query(query)
                    if data is not None and not data.empty:
                        sample_data[table] = data.to_dict('records')
                except:
                    continue
            
            return sample_data
        except:
            return {}
    
    def _extract_sql_query(self, text: str) -> Optional[str]:
        """Extrait une requête SQL d'un texte"""
        if not text:
            return None
        
        # Si c'est un dict, chercher sql_query
        if isinstance(text, dict):
            return text.get("sql_query")
        
        text_str = str(text)
        
        # Chercher du code SQL entre backticks ou avec mot-clé SELECT
        patterns = [
            r'"sql_query"\s*:\s*"([^"]+)"',
            r'"sql_query"\s*:\s*\'([^\']+)\'',
            r'```sql\n(.*?)\n```',
            r"```\n(.*?)\n```",
            r"SELECT .*?;(?=\n|$)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_str, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Nettoyer la requête
                query = match.strip()
                # Décoder les caractères échappés
                query = query.replace('\\"', '"').replace("\\'", "'").replace('\\n', '\n')
                if query:
                    return query
        
        return None
    
    def _generate_insight(self, question: str, data: pd.DataFrame) -> str:
        """Génère un insight basique à partir des données"""
        if data is None or data.empty:
            return "Aucune donnée disponible pour générer un insight."
        
        try:
            # Insight simple basé sur la forme des données
            num_rows = len(data)
            num_cols = len(data.columns)
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary = data[numeric_cols].describe()
                insight = f"Analyse de {num_rows} lignes avec {num_cols} colonnes. "
                insight += f"Données numériques disponibles: {', '.join(numeric_cols)}."
            else:
                insight = f"Analyse de {num_rows} lignes avec {num_cols} colonnes catégorielles."
            
            return insight
        except:
            return f"Données analysées: {num_rows} lignes, {num_cols} colonnes."
    
    def _generate_recommendations(self, data: pd.DataFrame) -> List[str]:
        """Génère des recommandations business basiques"""
        if data is None or data.empty:
            return ["Collecter plus de données pour l'analyse."]
        
        recommendations = []
        
        if len(data) > 1000:
            recommendations.append("Large volume de données détecté - considérez une analyse plus approfondie.")
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            recommendations.append("Données numériques disponibles - possibilité d'analyses statistiques avancées.")
        
        return recommendations
    
    def _suggest_visualization(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Suggère un type de visualisation"""
        if data is None or data.empty:
            return {"type": "table", "title": "Données"}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            return {"type": "scatter", "title": "Relation entre variables"}
        elif len(numeric_cols) == 1:
            return {"type": "bar", "title": "Distribution"}
        else:
            return {"type": "table", "title": "Données catégorielles"}
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Crée une réponse d'erreur standardisée"""
        return {
            "success": False,
            "error": error_message,
            "execution": {"time": 0.0, "error": error_message}
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état du système"""
        return {
            "database": {
                "available": self.db is not None,
                "statistics": self._sql_statistics,
                "tables": self.db.get_tables() if self.db else []
            },
            "ai": self.ai_provider.get_status() if hasattr(self.ai_provider, 'get_status') else {"available": False},
            "system": {
                "initialized": self._initialized,
                "version": settings.APP_VERSION,
                "schema_discovered": self._sql_schema_discovered
            }
        }
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques d'exécution"""
        total = self._execution_metrics["total_questions"]
        successful = self._execution_metrics["successful_queries"]
        total_time = self._execution_metrics["total_execution_time"]
        
        metrics = self._execution_metrics.copy()
        if total > 0:
            metrics["success_rate"] = (successful / total) * 100
            metrics["average_execution_time"] = total_time / total if total > 0 else 0
        else:
            metrics["success_rate"] = 0
            metrics["average_execution_time"] = 0
        
        return metrics
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retourne les informations système"""
        return {
            "database": {
                "available": self._sql_schema_discovered,
                "columns_count": len(self._available_sql_columns),
                "tables": list(set([col["table"] for col in self._available_sql_columns]))
            },
            "ai": self.ai_provider.get_status() if hasattr(self.ai_provider, 'get_status') else {"available": False},
            "cache": {
                "schema_cached": self._schema_cache_time is not None,
                "cache_time": self._schema_cache_time
            }
        }
    
    def get_sql_columns(self) -> List[Dict[str, Any]]:
        """Retourne les colonnes SQL disponibles"""
        return self._available_sql_columns
    
    def clear_cache(self):
        """Vide le cache"""
        self._schema_cache = {}
        self._schema_cache_time = None
        self.logger.info("🗑️ Cache vidé")
    
    def test_query(self, query: str = "SELECT 1 as test") -> Dict[str, Any]:
        """Teste une requête SQL simple"""
        try:
            if not self.db:
                return {"success": False, "error": "Database non initialisée"}
            
            result = self.db.execute_query(query)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test simple
    bot = InsightBotGPT()
    if bot.initialize():
        print("✅ Initialisation réussie")
        print("Status:", bot.get_status())
        
        # Test avec une question simple
        test_question = "Combien de tables y a-t-il dans la base de données ?"
        print(f"\n🧪 Test question: {test_question}")
        result = bot.process_question(test_question)
        print(f"✅ Résultat: {result.get('success')}")
        if result.get('success'):
            print(f"📊 Données: {result.get('data')}")
    else:
        print("❌ Initialisation échouée")