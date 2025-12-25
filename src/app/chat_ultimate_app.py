"""
Application Streamlit Ultimate - Version Complète avec Toutes les Fonctionnalités
Interface utilisateur avancée pour InsightBot AI
"""
import re
from typing import Dict, Any, List, Optional, Tuple
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import hashlib
from pathlib import Path
import sys
import os
import traceback
import logging

# ============================================================================
# CONFIGURATION DES CHEMINS - VERSION SIMPLIFIÉE
# ============================================================================

# Obtenir le répertoire du fichier actuel
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # src/app -> src -> InsightBot
core_path = project_root / "src" / "core"

print(f"Project root: {project_root}")
print(f"Core path: {core_path}")

# VÉRIFICATION DES CHEMINS
if not core_path.exists():
    st.error(f"❌ Chemin core introuvable: {core_path}")
    st.error("Structure de dossiers attendue: InsightBot/src/core/")
    st.stop()

# Ajouter les chemins au PYTHONPATH
paths_to_add = [str(project_root), str(project_root / "src"), str(core_path)]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)
        print(f"Added to sys.path: {path}")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
app_logger = logging.getLogger("InsightBotApp")

# ============================================================================
# IMPORT DES MODULES CORE AVEC IMPORT DYNAMIQUE
# ============================================================================

def import_insightbot_gpt():
    """Importe InsightBotGPT avec import dynamique simplifié"""
    try:
        # Méthode 1: Import direct via sys.path configuré
        from core.insightbot_gpt import InsightBotGPT
        app_logger.info("✅ InsightBotGPT importé via core.insightbot_gpt")
        return InsightBotGPT
        
    except ImportError as e:
        app_logger.warning(f"⚠️ Import direct échoué: {e}")
        
        try:
            # Méthode 2: Import du fichier direct
            import importlib.util
            
            # Chemin vers le fichier insightbot_gpt.py
            file_path = core_path / "insightbot_gpt.py"
            
            if not file_path.exists():
                app_logger.error(f"❌ Fichier non trouvé: {file_path}")
                raise ImportError(f"Fichier {file_path} non trouvé")
            
            # Charger le module
            spec = importlib.util.spec_from_file_location("insightbot_gpt", str(file_path))
            module = importlib.util.module_from_spec(spec)
            
            # Ajouter les modules nécessaires au namespace
            module.__dict__.update({
                'sys': sys,
                'os': os,
                'json': json,
                'pandas': pd,
                'numpy': np,
                're': re,
                'time': time,
                'logging': logging,
                'datetime': datetime,
                'Optional': Optional,
                'Dict': Dict,
                'List': List,
                'Any': Any,
                'Tuple': Tuple,
                'Path': Path,
                'timedelta': timedelta
            })
            
            # Exécuter le module
            spec.loader.exec_module(module)
            
            # Récupérer la classe
            if hasattr(module, 'InsightBotGPT'):
                InsightBotGPT = module.InsightBotGPT
                app_logger.info("✅ InsightBotGPT importé via import dynamique")
                return InsightBotGPT
            else:
                raise ImportError("Classe InsightBotGPT non trouvée dans le module")
                
        except Exception as e2:
            app_logger.error(f"❌ Import dynamique échoué: {e2}")
            st.error(f"Erreur d'import: {e2}")
            raise

# Importer re pour l'exécution
import re

# Essayer d'importer
try:
    InsightBotGPT = import_insightbot_gpt()
    app_logger.info("✅ InsightBotGPT importé avec succès")
except Exception as e:
    st.error(f"❌ Erreur critique d'import: {e}")
    st.code(traceback.format_exc())
    st.stop()

# ============================================================================
# LE RESTE DU CODE (inchangé car correct)
# ============================================================================

st.set_page_config(
    page_title="InsightBot AI - Assistant Analytique Intelligent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLE CSS PERSONNALISÉ
# ============================================================================

def load_custom_css():
    """Charge le CSS personnalisé pour l'application"""
    st.markdown("""
    <style>
    /* ===== VARIABLES DE COULEUR ===== */
    :root {
        --primary: #667eea;
        --primary-dark: #5a67d8;
        --secondary: #764ba2;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --light: #f8fafc;
        --dark: #1e293b;
        --gray: #64748b;
        --gray-light: #e2e8f0;
    }
    
    /* ===== OVERRIDE STREAMLIT PAR DÉFAUT ===== */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* ===== EN-TÊTE ===== */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* ===== CARTES DE MÉTRIQUES ===== */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid var(--primary);
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card-title {
        font-size: 0.9rem;
        color: var(--gray);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--dark);
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-card-subtitle {
        font-size: 0.85rem;
        color: var(--gray);
        font-weight: 500;
    }
    
    /* ===== BOUTONS ===== */
    .stButton > button {
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .secondary-button {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }
    
    .secondary-button:hover {
        background: var(--light) !important;
    }
    
    /* ===== ZONES DE TEXTE ===== */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid var(--gray-light);
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* ===== ONGLETS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        background-color: white;
        border: 1px solid var(--gray-light);
        color: var(--gray);
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--light);
        color: var(--primary);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
        font-weight: 600;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid var(--gray-light);
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
        color: var(--dark);
    }
    
    .streamlit-expanderContent {
        background-color: var(--light);
        border-radius: 0 0 10px 10px;
        padding: 1.5rem;
        border: 1px solid var(--gray-light);
        border-top: none;
    }
    
    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid var(--gray-light);
    }
    
    /* ===== SIDEBAR ===== */
    .css-1d391kg {
        background: linear-gradient(135deg, var(--dark) 0%, #2d3748 100%);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--light);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* ===== BADGES ===== */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--warning);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--danger);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .badge-info {
        background-color: rgba(59, 130, 246, 0.1);
        color: var(--info);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* ===== TOOLTIPS ===== */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--dark);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* ===== LOADING SPINNER ===== */
    .loading-spinner {
        border: 3px solid var(--gray-light);
        border-top: 3px solid var(--primary);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CLASSE PRINCIPALE DE L'APPLICATION
# ============================================================================

class ChatUltimateApp:
    def __init__(self):
        """Initialisation optimisée de l'application"""
        self.bot = None
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialisation complète de l'état de session"""
        defaults = {
            # Historique et état
            "chat_history": [],
            "current_question": "",
            "last_analysis": None,
            "current_tab": "chat",
            
            # État système
            "sql_schema_discovered": False,
            "nosql_schema_discovered": False,
            "available_sql_columns": [],
            "available_nosql_collections": [],
            "last_update": None,
            
            # Cache et métriques
            "cached_metrics": {},
            "auto_insights": [],
            "favorite_queries": [],
            "recent_searches": [],
            
            # Configuration
            "ai_provider_preference": "auto",
            "response_language": "auto",
            "show_technical_details": False,
            "auto_refresh": True,
            "theme_mode": "light",
            
            # État UI
            "sidebar_collapsed": False,
            "animation_enabled": True,
            
            # Statistiques
            "stats_total_questions": 0,
            "stats_successful_queries": 0,
            "stats_failed_queries": 0,
            "stats_total_time": 0,
            
            # Filtres et sélections
            "selected_table": "merged",
            "selected_time_range": "all",
            "selected_region": "all",
            "selected_category": "all",
            
            # État batch
            "batch_processing": False,
            "batch_questions": [],
            "batch_results": [],
            
            # Configuration sauvegardée
            "saved_configuration": None,
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @st.cache_resource(ttl=600, show_spinner=False)
    def initialize_bot(_self):
        """Initialisation lazy du bot avec cache"""
        try:
            app_logger.info("🧠 Initialisation de InsightBotGPT...")
            
            # Affichage du statut
            status_placeholder = st.empty()
            status_placeholder.info("🔄 Initialisation du système en cours...")
            
            # Initialisation
            bot = InsightBotGPT()
            
            if bot.initialize():
                status_placeholder.success("✅ InsightBotGPT initialisé avec succès")
                time.sleep(0.5)  # Laisse le temps de voir le message
                status_placeholder.empty()
                
                app_logger.info("✅ Bot initialisé avec succès")
                return bot
            else:
                status_placeholder.error("❌ Échec de l'initialisation")
                time.sleep(2)
                status_placeholder.empty()
                return None
                
        except Exception as e:
            app_logger.error(f"❌ Erreur initialisation bot: {str(e)}")
            st.error(f"Erreur d'initialisation: {str(e)}")
            return None
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_cached_metrics(_self, _bot):
        """Récupère les métriques avec cache"""
        try:
            if not _bot:
                return {}
            
            # Récupérer le statut complet
            status = _bot.get_status()
            
            # Récupérer les métriques d'exécution
            execution_metrics = _bot.get_execution_metrics()
            
            # Combiner les informations
            metrics = {
                "sql_stats": status.get("database", {}).get("statistics", {}),
                "nosql_stats": status.get("nosql", {}).get("statistics", {}),
                "ai_status": status.get("ai", {}),
                "execution_metrics": execution_metrics,
                "system_info": status.get("system", {}),
                "database_info": status.get("database", {}),
            }
            
            return metrics
            
        except Exception as e:
            app_logger.warning(f"⚠️ Erreur récupération métriques: {e}")
            return {}
    
    def get_available_tables(self) -> List[str]:
        """Récupère la liste des tables disponibles"""
        try:
            if self.bot and hasattr(self.bot.db, 'get_tables'):
                tables = self.bot.db.get_tables()
                return tables if tables else ["merged"]
            return ["merged"]
        except Exception as e:
            app_logger.error(f"Erreur récupération tables: {e}")
            return ["merged"]
    
    def clear_cache(self):
        """Vide le cache"""
        st.cache_data.clear()
        st.cache_resource.clear()
    
    def refresh_schema(self):
        """Rafraîchit le schéma"""
        if self.bot:
            try:
                self.bot._discover_sql_schema()
                st.success("✅ Schéma rafraîchi")
            except Exception as e:
                st.error(f"Erreur rafraîchissement schéma: {e}")
    
    def test_query(self, query: str):
        """Teste une requête SQL"""
        try:
            result = self.bot.db.execute_query(query)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Point d'entrée principal de l'application"""
        # Charger le CSS personnalisé
        load_custom_css()
        
        # Initialisation
        self.bot = self.initialize_bot()
        
        if not self.bot:
            self.display_error_state()
            return
        
        # Mise à jour de l'état système
        self.update_system_status()
        
        # Barre latérale
        self.display_sidebar()
        
        # Interface principale
        self.display_main_interface()
        
        # Footer
        self.display_footer()
    
    # ============================================================================
    # BARRE LATÉRALE
    # ============================================================================
    
    def display_sidebar(self):
        """Affiche la barre latérale avec navigation et informations"""
        with st.sidebar:
            # Logo et titre
            st.markdown("""
                <div style="text-align: center; padding: 1rem 0 2rem 0;">
                    <h1 style="color: white; margin: 0;">🤖</h1>
                    <h2 style="color: white; margin: 0.5rem 0;">InsightBot AI</h2>
                    <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
                        Assistant Analytique Intelligent
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Navigation rapide
            st.markdown("### 🗺️ Navigation")
            
            # Boutons de navigation
            nav_cols = st.columns(2)
            with nav_cols[0]:
                if st.button("🏠 Accueil", width='stretch', key="nav_home"):
                    st.session_state.current_tab = "chat"
                    st.rerun()
            
            with nav_cols[1]:
                if st.button("📊 Tableaux", width='stretch', key="nav_dashboards"):
                    st.session_state.current_tab = "dashboards"
                    st.rerun()
            
            # Sélecteur de langue
            st.markdown("---")
            st.markdown("### 🌍 Langue")
            
            lang_options = {
                "auto": "Auto-détection",
                "fr": "Français 🇫🇷",
                "en": "English 🇬🇧",
                "ar": "العربية 🇸🇦"
            }
            
            selected_lang = st.selectbox(
                "Langue de réponse",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                key="lang_selector"
            )
            
            st.session_state.response_language = selected_lang
            
            # Configuration IA
            st.markdown("---")
            st.markdown("### 🧠 Configuration IA")
            
            provider_options = {
                "auto": "Auto (Recommandé)",
                "gemini": "Gemini (Google)",
                "openai": "OpenAI",
                "ollama": "Ollama (Local)",
                "local": "Mode Local"
            }
            
            selected_provider = st.selectbox(
                "Fournisseur IA",
                options=list(provider_options.keys()),
                format_func=lambda x: provider_options[x],
                key="provider_selector"
            )
            
            st.session_state.ai_provider_preference = selected_provider
            
            # Options d'affichage
            st.markdown("---")
            st.markdown("### ⚙️ Options")
            
            col1, col2 = st.columns(2)
            with col1:
                show_tech = st.checkbox("Détails techniques", 
                                      value=st.session_state.show_technical_details)
                st.session_state.show_technical_details = show_tech
            
            with col2:
                auto_refresh = st.checkbox("Auto-rafraîchir",
                                         value=st.session_state.auto_refresh)
                st.session_state.auto_refresh = auto_refresh
            
            # Statistiques rapides
            st.markdown("---")
            st.markdown("### 📈 Statistiques")
            
            metrics = st.session_state.get("cached_metrics", {})
            exec_metrics = metrics.get("execution_metrics", {})
            
            if exec_metrics:
                st.metric("Questions", exec_metrics.get("total_questions", 0))
                st.metric("Taux de succès", f"{exec_metrics.get('success_rate', 0):.1f}%")
                st.metric("Temps moyen", f"{exec_metrics.get('average_execution_time', 0):.1f}s")
            
            # Bouton de rafraîchissement
            st.markdown("---")
            if st.button("🔄 Rafraîchir les données", width='stretch', key="refresh_data"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
    
    # ============================================================================
    # INTERFACE PRINCIPALE
    # ============================================================================
    
    def display_main_interface(self):
        """Affiche l'interface principale"""
        # En-tête principal
        self.display_header()
        
        # Navigation par onglets
        tabs = st.tabs([
            "💬 Chat Intelligent", 
            "📊 Tableaux de Bord",
            "🔍 Exploration Données",
            "🤖 Insights Automatiques",
            "⚙️ Configuration Système",
            "📚 Historique & Export"
        ])
        
        # Onglet 1: Chat Intelligent
        with tabs[0]:
            self.display_chat_interface()
        
        # Onglet 2: Tableaux de Bord
        with tabs[1]:
            self.display_dashboards()
        
        # Onglet 3: Exploration Données
        with tabs[2]:
            self.display_data_exploration()
        
        # Onglet 4: Insights Automatiques
        with tabs[3]:
            self.display_auto_insights()
        
        # Onglet 5: Configuration Système
        with tabs[4]:
            self.display_system_configuration()
        
        # Onglet 6: Historique
        with tabs[5]:
            self.display_history_and_export()
    
    def display_header(self):
        """Affiche l'en-tête principal avec métriques"""
        st.markdown("""
            <div class="main-header fade-in">
                <h1>🤖 InsightBot AI</h1>
                <p>Assistant Analytique Intelligent - Analyse SQL en Temps Réel avec IA</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Cartes de métriques
        self.display_metrics_cards()
    
    def display_metrics_cards(self):
        """Affiche les cartes de métriques principales"""
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = st.session_state.get("cached_metrics", {})
        sql_stats = metrics.get("sql_stats", {})
        exec_metrics = metrics.get("execution_metrics", {})
        ai_status = metrics.get("ai_status", {})
        
        with col1:
            self.display_metric_card(
                title="📊 Données SQL",
                value=f"{sql_stats.get('total_rows', 0):,}",
                subtitle="Lignes analysées",
                icon="📊",
                color="#667eea",
                help_text="Nombre total d'enregistrements dans la base SQL"
            )
        
        with col2:
            total_sales = sql_stats.get('total_sales', 0)
            self.display_metric_card(
                title="💰 Chiffre d'Affaires",
                value=f"${total_sales:,.0f}" if total_sales > 0 else "$0",
                subtitle="Ventes totales",
                icon="💰",
                color="#10b981",
                help_text="Somme des ventes en dollars"
            )
        
        with col3:
            success_rate = exec_metrics.get('success_rate', 0)
            self.display_metric_card(
                title="🎯 Analyse IA",
                value=f"{success_rate:.1f}%",
                subtitle="Taux de réussite",
                icon="🎯",
                color="#8b5cf6",
                help_text="Pourcentage d'analyses réussies"
            )
        
        with col4:
            active_provider = ai_status.get('active_provider', 'Local')
            provider_icons = {
                "gemini": "🔷",
                "openai": "🟢", 
                "ollama": "🟣",
                "local": "⚪"
            }
            icon = provider_icons.get(active_provider.lower(), "🤖")
            
            self.display_metric_card(
                title="🧠 Intelligence",
                value=f"{icon} {active_provider}",
                subtitle="Fournisseur actif",
                icon="🧠",
                color="#f59e0b",
                help_text="Modèle d'IA utilisé pour les analyses"
            )
        
        # Dernière mise à jour
        if st.session_state.get("last_update"):
            last_update = st.session_state["last_update"]
            st.caption(f"🔄 Dernière mise à jour: {last_update.strftime('%H:%M:%S')}")
    
    def display_metric_card(self, title, value, subtitle, icon="📊", color="#667eea", help_text=None):
        """Affiche une carte de métrique stylisée"""
        st.markdown(f"""
            <div class="metric-card fade-in" style="border-left-color: {color};">
                <div class="metric-card-title">
                    {icon} {title}
                </div>
                <div class="metric-card-value">
                    {value}
                </div>
                <div class="metric-card-subtitle">
                    {subtitle}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if help_text:
            with st.popover("ℹ️"):
                st.info(help_text)
    
    # ============================================================================
    # ONGLET CHAT INTELLIGENT
    # ============================================================================
    
    def display_chat_interface(self):
        """Affiche l'interface de chat intelligent"""
        st.markdown("### 💬 Posez votre question analytique")
        
        # Interface en deux colonnes
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Zone de saisie principale
            question = self.display_question_input()
            
            # Boutons d'action
            self.display_action_buttons(question)
            
            # Affichage des résultats
            if st.session_state.get("last_analysis"):
                self.display_analysis_results(st.session_state["last_analysis"])
        
        with col_right:
            # Catégories de questions
            self.display_question_categories()
            
            # Exemples de questions
            self.display_example_questions()
            
            # Filtres rapides
            self.display_quick_filters()
    
    def display_question_input(self):
        """Affiche la zone de saisie de question"""
        with st.container():
            st.markdown("#### 📝 Votre question analytique")
            
            # Zone de texte avec placeholder
            question = st.text_area(
                " ",
                placeholder="Ex: Quels sont les produits les plus vendus par région ?\nQuelle est l'évolution des ventes mensuelles ?\nComparez la rentabilité par catégorie...",
                height=120,
                key="question_input",
                help="Posez votre question en français, anglais ou arabe"
            )
            
            # Indicateur de langue
            if question:
                try:
                    from core.prompt_templates import detect_language
                    lang = detect_language(question)
                    lang_names = {"fr": "Français", "en": "Anglais", "ar": "Arabe"}
                    st.caption(f"🌐 Langue détectée: {lang_names.get(lang, 'Inconnue')}")
                except:
                    pass
            
            return question
    
    def display_action_buttons(self, question):
        """Affiche les boutons d'action"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            analyze_clicked = st.button(
                "🔍 Analyser avec l'IA",
                type="primary",
                width='stretch',
                disabled=not question.strip(),
                help="Lancer l'analyse avec l'intelligence artificielle"
            )
        
        with col2:
            clear_clicked = st.button(
                "🗑️ Effacer",
                type="secondary",
                width='stretch',
                help="Effacer la question actuelle"
            )
        
        with col3:
            save_clicked = st.button(
                "💾 Enregistrer",
                type="secondary",
                width='stretch',
                help="Enregistrer cette question dans les favoris"
            )
        
        with col4:
            batch_clicked = st.button(
                "📁 Lot",
                type="secondary",
                width='stretch',
                help="Ajouter à un traitement par lot"
            )
        
        # Gestion des clics
        if clear_clicked:
            st.session_state.current_question = ""
            st.rerun()
        
        if save_clicked and question.strip():
            self.save_to_favorites(question)
            st.success("✅ Question enregistrée dans les favoris")
        
        if batch_clicked and question.strip():
            if question not in st.session_state.batch_questions:
                st.session_state.batch_questions.append(question)
                st.success("✅ Question ajoutée au traitement par lot")
        
        if analyze_clicked and question.strip():
            self.process_question_with_ui(question)
    
    def process_question_with_ui(self, question: str):
        """Traite une question avec interface utilisateur avancée"""
        # Enregistrer la question
        st.session_state.current_question = question
        st.session_state.stats_total_questions += 1
        
        # Créer un conteneur pour les résultats
        result_container = st.container()
        
        # Barre de progression et animations
        with st.status("🧠 **Analyse en cours...**", expanded=True) as status:
            # Étape 1: Préparation
            status.update(label="🔧 Préparation de l'analyse...", state="running")
            time.sleep(0.3)
            
            # Étape 2: Génération du prompt
            status.update(label="📝 Génération du prompt avec schéma SQL...", state="running")
            time.sleep(0.3)
            
            # Étape 3: Appel IA
            status.update(label="🤖 Consultation de l'intelligence artificielle...", state="running")
            
            # Traitement réel
            result = self.bot.process_question(question)
            
            # Mettre à jour les statistiques
            if result.get("success"):
                st.session_state.stats_successful_queries += 1
                status.update(label="✅ Analyse complétée avec succès!", state="complete")
            else:
                st.session_state.stats_failed_queries += 1
                status.update(label="⚠️ Analyse terminée avec avertissements", state="complete")
        
        # Ajouter à l'historique
        self.add_to_chat_history(question, result)
        
        # Stocker le dernier résultat
        st.session_state.last_analysis = result
        
        # Afficher les résultats
        with result_container:
            self.display_analysis_results(result)
    
    def display_analysis_results(self, result: Dict):
        """Affiche les résultats d'une analyse"""
        if not result:
            return
        
        st.markdown("---")
        st.markdown("### 📊 Résultats de l'Analyse")
        
        # Badge de statut
        if result.get("success"):
            st.markdown('<span class="badge badge-success">Succès</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-warning">Avertissements</span>', unsafe_allow_html=True)
        
        # Question
        with st.expander("📝 **Question analysée**", expanded=False):
            st.info(f"**{result.get('question', 'N/A')}**")
        
        # Insight principal
        st.markdown("#### 💡 Insight Principal")
        insight_text = result.get("insight", "Aucun insight disponible")
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f0f4ff 0%, #e6f0ff 100%);
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                margin: 1rem 0;
            ">
                {insight_text}
            </div>
        """, unsafe_allow_html=True)
        
        # Visualisation
        viz_config = result.get("visualization", {})
        data = result.get("data")
        
        if viz_config.get("type") and data is not None and not data.empty:
            self.display_interactive_visualization(data, viz_config)
        
        # Données tabulaires
        if data is not None and not data.empty:
            self.display_data_table(data)
        
        # Recommandations business
        recommendations = result.get("business_recommendations", [])
        if recommendations:
            self.display_recommendations(recommendations)
        
        # Détails techniques (si activé)
        if st.session_state.show_technical_details:
            self.display_technical_details(result)
        
        # Actions sur les résultats
        self.display_result_actions(result)
    
    def display_interactive_visualization(self, data: pd.DataFrame, config: Dict):
        """Affiche une visualisation interactive"""
        st.markdown("#### 📈 Visualisation Interactive")
        
        try:
            viz_type = config.get("type", "table")
            
            # Sélecteur de type de visualisation
            viz_types = ["bar", "line", "pie", "scatter", "table", "area"]
            selected_viz = st.selectbox(
                "Type de visualisation",
                options=viz_types,
                index=viz_types.index(viz_type) if viz_type in viz_types else 0,
                key=f"viz_selector_{hashlib.md5(str(data).encode()).hexdigest()[:8]}"
            )
            
            # Configuration des axes
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox(
                    "Axe X",
                    options=data.columns.tolist(),
                    index=0,
                    key=f"x_axis_{hashlib.md5(str(data).encode()).hexdigest()[:8]}"
                )
            
            with col2:
                y_options = [col for col in data.columns if col != x_axis]
                y_axis = st.selectbox(
                    "Axe Y",
                    options=y_options if y_options else data.columns.tolist(),
                    index=min(1, len(data.columns) - 1) if len(data.columns) > 1 else 0,
                    key=f"y_axis_{hashlib.md5(str(data).encode()).hexdigest()[:8]}"
                )
            
            # Générer la visualisation
            fig = None
            
            if selected_viz == "bar":
                fig = px.bar(
                    data, 
                    x=x_axis, 
                    y=y_axis,
                    title=config.get("title", "Graphique à barres"),
                    color=x_axis,
                    text_auto=True
                )
                fig.update_traces(textposition='outside')
                
            elif selected_viz == "line":
                fig = px.line(
                    data, 
                    x=x_axis, 
                    y=y_axis,
                    title=config.get("title", "Graphique linéaire"),
                    markers=True
                )
                
            elif selected_viz == "pie":
                fig = px.pie(
                    data,
                    names=x_axis,
                    values=y_axis,
                    title=config.get("title", "Diagramme circulaire"),
                    hole=0.3
                )
                
            elif selected_viz == "scatter":
                fig = px.scatter(
                    data,
                    x=x_axis,
                    y=y_axis,
                    title=config.get("title", "Nuage de points"),
                    trendline="ols"
                )
                
            elif selected_viz == "area":
                fig = px.area(
                    data,
                    x=x_axis,
                    y=y_axis,
                    title=config.get("title", "Graphique en aires")
                )
            
            # Afficher le graphique
            if fig:
                # Personnaliser le layout
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, width='stretch', key=f"viz_{selected_viz}")
                
                # Options d'export
                col_exp1, col_exp2, col_exp3 = st.columns(3)
                with col_exp1:
                    if st.button("📥 PNG", key=f"export_png_{selected_viz}"):
                        st.info("Export PNG disponible dans la version pro")
                with col_exp2:
                    if st.button("📥 SVG", key=f"export_svg_{selected_viz}"):
                        st.info("Export SVG disponible dans la version pro")
                with col_exp3:
                    if st.button("📥 HTML", key=f"export_html_{selected_viz}"):
                        st.info("Export HTML disponible dans la version pro")
            
        except Exception as e:
            st.warning(f"⚠️ Impossible de générer la visualisation: {str(e)}")
            # Fallback: afficher un tableau
            st.dataframe(data.head(20), width='stretch')
    
    def display_data_table(self, data: pd.DataFrame):
        """Affiche les données sous forme de tableau interactif"""
        st.markdown("#### 📋 Données Analysées")
        
        # Options d'affichage
        col1, col2, col3 = st.columns(3)
        with col1:
            show_rows = st.slider("Nombre de lignes", 5, 100, 20, key="row_slider")
        with col2:
            sort_by = st.selectbox("Trier par", options=data.columns.tolist(), key="sort_select")
        with col3:
            sort_order = st.radio("Ordre", ["Croissant", "Décroissant"], horizontal=True, key="sort_order")
        
        # Trier les données
        sorted_data = data.sort_values(
            by=sort_by,
            ascending=(sort_order == "Croissant")
        )
        
        # Afficher le tableau
        st.dataframe(
            sorted_data.head(show_rows),
            width='stretch',
            hide_index=True,
            column_config={
                col: st.column_config.Column(
                    help=f"Colonne: {col}",
                    width="medium"
                ) for col in data.columns
            }
        )
        
        # Statistiques rapides
        with st.expander("📊 Statistiques des données"):
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Lignes totales", f"{len(data):,}")
                st.metric("Colonnes", len(data.columns))
            
            with col_stat2:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.metric("Colonnes numériques", len(numeric_cols))
                    st.metric("Valeurs nulles", data.isnull().sum().sum())
    
    def display_recommendations(self, recommendations: List[str]):
        """Affiche les recommandations business"""
        st.markdown("#### 🎯 Recommandations Business")
        
        for i, rec in enumerate(recommendations[:3], 1):  # Limiter à 3 recommandations
            # Déterminer l'icône en fonction du type de recommandation
            if "immédiat" in rec.lower() or "immediate" in rec.lower():
                icon = "🚀"
                color = "#10b981"
            elif "moyen terme" in rec.lower() or "medium term" in rec.lower():
                icon = "📈"
                color = "#3b82f6"
            elif "long terme" in rec.lower() or "long term" in rec.lower():
                icon = "🏗️"
                color = "#8b5cf6"
            else:
                icon = "✅"
                color = "#64748b"
            
            # Afficher la recommandation
            st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.25rem;
                    border-radius: 10px;
                    border-left: 4px solid {color};
                    margin: 0.5rem 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.5rem;">{icon}</span>
                        <span style="font-weight: 600; color: {color};">Recommandation #{i}</span>
                    </div>
                    <div style="margin-top: 0.75rem; color: #1e293b;">
                        {rec}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    def display_technical_details(self, result: Dict):
        """Affiche les détails techniques de l'analyse"""
        with st.expander("🔧 **Détails Techniques**", expanded=False):
            execution_info = result.get("execution", {})
            
            # Métriques d'exécution
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏱️ Temps", f"{execution_info.get('time', 0):.2f}s")
            with col2:
                provider = execution_info.get('provider', 'Inconnu')
                st.metric("🧠 Fournisseur", provider)
            with col3:
                tokens = execution_info.get('tokens', 0)
                st.metric("🔤 Tokens", f"{tokens:,}")
            with col4:
                retries = execution_info.get('sql_retries', 0)
                st.metric("🔄 Tentatives SQL", retries)
            
            # Requête SQL
            sql_query = result.get("sql_query")
            if sql_query:
                st.markdown("##### 📝 Requête SQL Générée")
                st.code(sql_query, language="sql")
            
            # Warnings et messages
            warnings = execution_info.get('warnings', [])
            if warnings:
                st.markdown("##### ⚠️ Avertissements")
                for warning in warnings:
                    st.warning(warning)
            
            # Message d'exécution
            if execution_info.get('message'):
                st.info(f"ℹ️ {execution_info['message']}")
    
    def display_result_actions(self, result: Dict):
        """Affiche les actions disponibles sur les résultats"""
        st.markdown("---")
        st.markdown("#### 📤 Export & Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Préparer les données pour l'export
        data = result.get("data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with col1:
            if data is not None and not data.empty:
                csv_data = data.to_csv(index=False)
                st.download_button(
                    label="📥 CSV",
                    data=csv_data,
                    file_name=f"insightbot_analysis_{timestamp}.csv",
                    mime="text/csv",
                    help="Télécharger les données au format CSV"
                )
        
        with col2:
            if data is not None and not data.empty:
                json_data = data.to_json(orient="records", indent=2, force_ascii=False)
                st.download_button(
                    label="📥 JSON",
                    data=json_data,
                    file_name=f"insightbot_analysis_{timestamp}.json",
                    mime="application/json",
                    help="Télécharger les données au format JSON"
                )
        
        with col3:
            # Export du rapport complet
            report_data = {
                "question": result.get("question"),
                "insight": result.get("insight"),
                "recommendations": result.get("business_recommendations", []),
                "sql_query": result.get("sql_query"),
                "execution_info": result.get("execution", {}),
                "timestamp": timestamp
            }
            
            st.download_button(
                label="📄 Rapport",
                data=json.dumps(report_data, indent=2, ensure_ascii=False),
                file_name=f"insightbot_report_{timestamp}.json",
                mime="application/json",
                help="Télécharger le rapport complet au format JSON"
            )
        
        with col4:
            if st.button("🔄 Réanalyser", width='stretch'):
                st.session_state.current_question = result.get("question", "")
                st.rerun()
    
    def display_question_categories(self):
        """Affiche les catégories de questions"""
        st.markdown("#### 📁 Catégories")
        
        categories = [
            {"icon": "📈", "name": "Ventes", "color": "#10b981",
             "examples": ["Top produits", "Ventes par région", "Évolution mensuelle"]},
            {"icon": "💰", "name": "Rentabilité", "color": "#f59e0b",
             "examples": ["Marge par produit", "Coûts vs revenus", "ROI par campagne"]},
            {"icon": "👥", "name": "Clients", "color": "#3b82f6",
             "examples": ["Segmentation", "Comportement d'achat", "Valeur à vie"]},
            {"icon": "🔄", "name": "Retours", "color": "#ef4444",
             "examples": ["Taux de retour", "Raisons des retours", "Impact sur profit"]},
            {"icon": "📦", "name": "Stock", "color": "#8b5cf6",
             "examples": ["Rotation des stocks", "Niveaux optimaux", "Ruptures de stock"]},
            {"icon": "🌍", "name": "Géographie", "color": "#06b6d4",
             "examples": ["Performances par marché", "Densité par région", "Opportunités géographiques"]},
        ]
        
        for cat in categories:
            with st.expander(f"{cat['icon']} **{cat['name']}**", expanded=False):
                for example in cat["examples"]:
                    if st.button(
                        f"{example}",
                        key=f"cat_{cat['name']}_{example}",
                        width='stretch'
                    ):
                        st.session_state.current_question = f"Analyse {example.lower()}"
                        st.rerun()
    
    def display_example_questions(self):
        """Affiche des exemples de questions"""
        st.markdown("#### 💡 Exemples de Questions")
        
        examples = [
            "Quels sont les 10 produits les plus vendus ?",
            "Comment évoluent les ventes mensuelles ?",
            "Quelle région a la plus forte croissance ?",
            "Comparez la rentabilité par catégorie",
            "Analysez les retours par produit",
            "Quel est le panier moyen par client ?",
            "Identifiez les tendances saisonnières",
            "Quels produits ont la meilleure marge ?",
            "Analysez la distribution géographique des ventes",
            "Quelle est la performance par canal de vente ?"
        ]
        
        for example in examples:
            if st.button(
                f"• {example}",
                key=f"ex_{hashlib.md5(example.encode()).hexdigest()[:8]}",
                help="Cliquez pour utiliser cet exemple",
                width='stretch'
            ):
                st.session_state.current_question = example
                st.rerun()
    
    def display_quick_filters(self):
        """Affiche les filtres rapides"""
        st.markdown("#### ⚡ Filtres Rapides")
        
        # Période
        time_options = {
            "all": "Toute la période",
            "month": "30 derniers jours",
            "quarter": "3 derniers mois",
            "year": "12 derniers mois"
        }
        
        selected_time = st.selectbox(
            "Période",
            options=list(time_options.keys()),
            format_func=lambda x: time_options[x],
            key="quick_time_filter"
        )
        st.session_state.selected_time_range = selected_time
        
        # Région
        # Récupérer les régions disponibles depuis la base
        try:
            region_query = "SELECT DISTINCT Region FROM merged WHERE Region IS NOT NULL"
            region_data = self.bot.db.execute_query(region_query)
            
            if region_data is not None and not region_data.empty:
                regions = ["all"] + region_data["Region"].tolist()
                selected_region = st.selectbox(
                    "Région",
                    options=regions,
                    format_func=lambda x: "Toutes les régions" if x == "all" else x,
                    key="quick_region_filter"
                )
                st.session_state.selected_region = selected_region
        except:
            pass
        
        # Catégorie
        try:
            category_query = "SELECT DISTINCT Category FROM merged WHERE Category IS NOT NULL"
            category_data = self.bot.db.execute_query(category_query)
            
            if category_data is not None and not category_data.empty:
                categories = ["all"] + category_data["Category"].tolist()
                selected_category = st.selectbox(
                    "Catégorie",
                    options=categories,
                    format_func=lambda x: "Toutes les catégories" if x == "all" else x,
                    key="quick_category_filter"
                )
                st.session_state.selected_category = selected_category
        except:
            pass
        
        # Appliquer les filtres
        if st.button("🔍 Appliquer les filtres", width='stretch'):
            st.info("⚠️ Les filtres seront appliqués aux prochaines analyses")
    
    # ============================================================================
    # ONGLET TABLEAUX DE BORD
    # ============================================================================
    
    def display_dashboards(self):
        """Affiche les tableaux de bord pré-calculés"""
        st.markdown("### 📊 Tableaux de Bord Interactifs")
        
        # Sélecteur de dashboard
        dashboard_options = {
            "sales": "📈 Tableau de Bord Ventes",
            "profit": "💰 Tableau de Bord Rentabilité",
            "customers": "👥 Tableau de Bord Clients",
            "returns": "🔄 Tableau de Bord Retours",
            "inventory": "📦 Tableau de Bord Stock",
            "geographic": "🌍 Tableau de Bord Géographique"
        }
        
        selected_dashboard = st.selectbox(
            "Sélectionnez un tableau de bord",
            options=list(dashboard_options.keys()),
            format_func=lambda x: dashboard_options[x],
            key="dashboard_selector"
        )
        
        # Afficher le dashboard sélectionné
        if selected_dashboard == "sales":
            self.display_sales_dashboard()
        elif selected_dashboard == "profit":
            self.display_profit_dashboard()
        elif selected_dashboard == "customers":
            self.display_customers_dashboard()
        elif selected_dashboard == "returns":
            self.display_returns_dashboard()
        elif selected_dashboard == "inventory":
            self.display_inventory_dashboard()
        elif selected_dashboard == "geographic":
            self.display_geographic_dashboard()
    
    @st.cache_data(ttl=300, show_spinner=False)
    def display_sales_dashboard(_self):
        """Tableau de bord des ventes"""
        try:
            st.markdown("#### 📈 Performance des Ventes")
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_sales_query = "SELECT COALESCE(SUM(Sales), 0) as total_sales FROM merged"
                total_sales_data = _self.bot.db.execute_query(total_sales_query)
                if total_sales_data is not None and not total_sales_data.empty:
                    total_sales = total_sales_data.iloc[0]["total_sales"]
                    st.metric("Ventes Totales", f"${total_sales:,.0f}")
            
            with col2:
                avg_order_query = "SELECT COALESCE(AVG(Sales), 0) as avg_order FROM merged"
                avg_order_data = _self.bot.db.execute_query(avg_order_query)
                if avg_order_data is not None and not avg_order_data.empty:
                    avg_order = avg_order_data.iloc[0]["avg_order"]
                    st.metric("Panier Moyen", f"${avg_order:,.2f}")
            
            with col3:
                top_product_query = """
                    SELECT "Product Name", SUM(Sales) as total_sales 
                    FROM merged 
                    GROUP BY "Product Name" 
                    ORDER BY total_sales DESC 
                    LIMIT 1
                """
                top_product_data = _self.bot.db.execute_query(top_product_query)
                if top_product_data is not None and not top_product_data.empty:
                    top_product = top_product_data.iloc[0]["Product Name"]
                    st.metric("Produit Phare", top_product[:20])
            
            with col4:
                growth_query = """
                    WITH monthly_sales AS (
                        SELECT 
                            strftime('%Y-%m', "Order Date") as month,
                            SUM(Sales) as monthly_sales
                        FROM merged
                        GROUP BY strftime('%Y-%m', "Order Date")
                        ORDER BY month DESC
                    )
                    SELECT 
                        (MAX(monthly_sales) - MIN(monthly_sales)) * 100.0 / MIN(monthly_sales) as growth_rate
                    FROM monthly_sales
                """
                growth_data = _self.bot.db.execute_query(growth_query)
                if growth_data is not None and not growth_data.empty:
                    growth_rate = growth_data.iloc[0]["growth_rate"]
                    st.metric("Taux Croissance", f"{growth_rate:.1f}%")
            
            # Graphiques
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Ventes par mois
                monthly_sales_query = """
                    SELECT 
                        strftime('%Y-%m', "Order Date") as month,
                        SUM(Sales) as total_sales
                    FROM merged
                    GROUP BY strftime('%Y-%m', "Order Date")
                    ORDER BY month
                """
                monthly_sales_data = _self.bot.db.execute_query(monthly_sales_query)
                
                if monthly_sales_data is not None and not monthly_sales_data.empty:
                    fig = px.line(
                        monthly_sales_data,
                        x="month",
                        y="total_sales",
                        title="📅 Ventes Mensuelles",
                        markers=True
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            with col_chart2:
                # Ventes par catégorie
                category_sales_query = """
                    SELECT 
                        Category,
                        SUM(Sales) as total_sales
                    FROM merged
                    GROUP BY Category
                    ORDER BY total_sales DESC
                """
                category_sales_data = _self.bot.db.execute_query(category_sales_query)
                
                if category_sales_data is not None and not category_sales_data.empty:
                    fig = px.pie(
                        category_sales_data,
                        values="total_sales",
                        names="Category",
                        title="📊 Ventes par Catégorie",
                        hole=0.3
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            # Top produits
            st.markdown("#### 🏆 Top 10 Produits")
            top_products_query = """
                SELECT 
                    "Product Name",
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    COUNT(*) as order_count
                FROM merged
                GROUP BY "Product Name"
                ORDER BY total_sales DESC
                LIMIT 10
            """
            top_products_data = _self.bot.db.execute_query(top_products_query)
            
            if top_products_data is not None and not top_products_data.empty:
                st.dataframe(
                    top_products_data,
                    width='stretch',
                    column_config={
                        "Product Name": "Produit",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "order_count": "Commandes"
                    }
                )
                
        except Exception as e:
            st.error(f"❌ Erreur chargement dashboard ventes: {e}")
    
    @st.cache_data(ttl=300, show_spinner=False)
    def display_profit_dashboard(_self):
        """Tableau de bord de la rentabilité"""
        try:
            st.markdown("#### 💰 Analyse de Rentabilité")
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_profit_query = "SELECT COALESCE(SUM(Profit), 0) as total_profit FROM merged"
                total_profit_data = _self.bot.db.execute_query(total_profit_query)
                if total_profit_data is not None and not total_profit_data.empty:
                    total_profit = total_profit_data.iloc[0]["total_profit"]
                    st.metric("Profit Total", f"${total_profit:,.0f}")
            
            with col2:
                margin_query = """
                    SELECT 
                        (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as avg_margin
                    FROM merged
                    WHERE Sales > 0
                """
                margin_data = _self.bot.db.execute_query(margin_query)
                if margin_data is not None and not margin_data.empty:
                    avg_margin = margin_data.iloc[0]["avg_margin"]
                    st.metric("Marge Moyenne", f"{avg_margin:.1f}%")
            
            with col3:
                most_profitable_query = """
                    SELECT "Product Name", SUM(Profit) as total_profit
                    FROM merged
                    GROUP BY "Product Name"
                    ORDER BY total_profit DESC
                    LIMIT 1
                """
                most_profitable_data = _self.bot.db.execute_query(most_profitable_query)
                if most_profitable_data is not None and not most_profitable_data.empty:
                    most_profitable = most_profitable_data.iloc[0]["Product Name"]
                    st.metric("Plus Rentable", most_profitable[:20])
            
            with col4:
                loss_query = """
                    SELECT COUNT(*) as loss_count
                    FROM merged
                    WHERE Profit < 0
                """
                loss_data = _self.bot.db.execute_query(loss_query)
                if loss_data is not None and not loss_data.empty:
                    loss_count = loss_data.iloc[0]["loss_count"]
                    st.metric("Produits Déficitaires", loss_count)
            
            # Graphiques
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Marge par catégorie
                margin_category_query = """
                    SELECT 
                        Category,
                        (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin_percentage,
                        SUM(Profit) as total_profit
                    FROM merged
                    WHERE Sales > 0
                    GROUP BY Category
                    ORDER BY margin_percentage DESC
                """
                margin_category_data = _self.bot.db.execute_query(margin_category_query)
                
                if margin_category_data is not None and not margin_category_data.empty:
                    fig = px.bar(
                        margin_category_data,
                        x="Category",
                        y="margin_percentage",
                        title="📊 Marge par Catégorie (%)",
                        color="total_profit",
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            with col_chart2:
                # Profit vs Ventes
                profit_vs_sales_query = """
                    SELECT 
                        "Product Name",
                        SUM(Sales) as total_sales,
                        SUM(Profit) as total_profit,
                        (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin
                    FROM merged
                    GROUP BY "Product Name"
                    HAVING total_sales > 1000
                    ORDER BY total_profit DESC
                    LIMIT 20
                """
                profit_vs_sales_data = _self.bot.db.execute_query(profit_vs_sales_query)
                
                if profit_vs_sales_data is not None and not profit_vs_sales_data.empty:
                    fig = px.scatter(
                        profit_vs_sales_data,
                        x="total_sales",
                        y="total_profit",
                        size="margin",
                        color="margin",
                        hover_name="Product Name",
                        title="📈 Profit vs Ventes",
                        labels={
                            "total_sales": "Ventes Totales ($)",
                            "total_profit": "Profit Total ($)",
                            "margin": "Marge (%)"
                        }
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            # Analyse de rentabilité détaillée
            st.markdown("#### 📋 Détail de la Rentabilité")
            
            profitability_detail_query = """
                SELECT 
                    Category,
                    COUNT(*) as transaction_count,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    AVG(Profit) as avg_profit_per_transaction,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin_percentage
                FROM merged
                GROUP BY Category
                ORDER BY margin_percentage DESC
            """
            
            profitability_detail_data = _self.bot.db.execute_query(profitability_detail_query)
            
            if profitability_detail_data is not None and not profitability_detail_data.empty:
                st.dataframe(
                    profitability_detail_data,
                    width='stretch',
                    column_config={
                        "Category": "Catégorie",
                        "transaction_count": "Transactions",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "avg_profit_per_transaction": st.column_config.NumberColumn("Profit/Trans", format="$%.2f"),
                        "margin_percentage": st.column_config.NumberColumn("Marge", format="%.1f%%")
                    }
                )
                
        except Exception as e:
            st.error(f"❌ Erreur chargement dashboard rentabilité: {e}")
    
    def display_customers_dashboard(self):
        """Tableau de bord clients"""
        st.info("""
        ### 👥 Tableau de Bord Clients
        *En cours de développement*
        
        **Fonctionnalités à venir:**
        - Segmentation des clients
        - Analyse RFM (Récence, Fréquence, Montant)
        - Valeur à vie du client (LTV)
        - Taux de rétention
        - Analyse de cohortes
        """)
        
        # Placeholder avec des métriques basiques
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                customer_count_query = "SELECT COUNT(DISTINCT \"Customer ID\") as customer_count FROM merged"
                customer_count_data = self.bot.db.execute_query(customer_count_query)
                if customer_count_data is not None and not customer_count_data.empty:
                    customer_count = customer_count_data.iloc[0]["customer_count"]
                    st.metric("Clients Uniques", f"{customer_count:,}")
            
            with col2:
                avg_orders_query = """
                    SELECT AVG(order_count) as avg_orders_per_customer
                    FROM (
                        SELECT "Customer ID", COUNT(*) as order_count
                        FROM merged
                        GROUP BY "Customer ID"
                    )
                """
                avg_orders_data = self.bot.db.execute_query(avg_orders_query)
                if avg_orders_data is not None and not avg_orders_data.empty:
                    avg_orders = avg_orders_data.iloc[0]["avg_orders_per_customer"]
                    st.metric("Commandes Moyennes", f"{avg_orders:.1f}")
            
            with col3:
                repeat_customers_query = """
                    SELECT COUNT(*) as repeat_customers
                    FROM (
                        SELECT "Customer ID", COUNT(*) as order_count
                        FROM merged
                        GROUP BY "Customer ID"
                        HAVING COUNT(*) > 1
                    )
                """
                repeat_customers_data = self.bot.db.execute_query(repeat_customers_query)
                if repeat_customers_data is not None and not repeat_customers_data.empty:
                    repeat_customers = repeat_customers_data.iloc[0]["repeat_customers"]
                    st.metric("Clients Fidèles", f"{repeat_customers:,}")
                
        except Exception as e:
            st.warning(f"⚠️ Données clients limitées: {e}")
    
    def display_returns_dashboard(self):
        """Tableau de bord des retours"""
        st.info("""
        ### 🔄 Tableau de Bord Retours
        *En cours de développement*
        
        **Fonctionnalités à venir:**
        - Taux de retour par produit/catégorie
        - Raisons principales des retours
        - Impact financier des retours
        - Analyse temporelle des retours
        - Prédiction des retours
        """)
        
        # Placeholder avec des métriques basiques
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                return_rate_query = """
                    SELECT 
                        (SUM(CASE WHEN Is_Returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as return_rate
                    FROM merged
                """
                return_rate_data = self.bot.db.execute_query(return_rate_query)
                if return_rate_data is not None and not return_rate_data.empty:
                    return_rate = return_rate_data.iloc[0]["return_rate"]
                    st.metric("Taux de Retour", f"{return_rate:.1f}%")
            
            with col2:
                return_value_query = """
                    SELECT 
                        SUM(CASE WHEN Is_Returned = 1 THEN Sales ELSE 0 END) as return_value
                    FROM merged
                """
                return_value_data = self.bot.db.execute_query(return_value_query)
                if return_value_data is not None and not return_value_data.empty:
                    return_value = return_value_data.iloc[0]["return_value"]
                    st.metric("Valeur Retournée", f"${return_value:,.0f}")
            
            with col3:
                top_return_product_query = """
                    SELECT "Product Name", COUNT(*) as return_count
                    FROM merged
                    WHERE Is_Returned = 1
                    GROUP BY "Product Name"
                    ORDER BY return_count DESC
                    LIMIT 1
                """
                top_return_product_data = self.bot.db.execute_query(top_return_product_query)
                if top_return_product_data is not None and not top_return_product_data.empty:
                    top_return_product = top_return_product_data.iloc[0]["Product Name"]
                    st.metric("Produit Retourné", top_return_product[:20])
                
        except Exception as e:
            st.warning(f"⚠️ Données retours limitées: {e}")
    
    def display_inventory_dashboard(self):
        """Tableau de bord du stock"""
        st.info("""
        ### 📦 Tableau de Bord Stock
        *En cours de développement*
        
        **Fonctionnalités à venir:**
        - Niveaux de stock actuels
        - Rotation des stocks
        - Prévisions de demande
        - Analyse ABC des stocks
        - Optimisation des réapprovisionnements
        """)
    
    def display_geographic_dashboard(self):
        """Tableau de bord géographique"""
        st.info("""
        ### 🌍 Tableau de Bord Géographique
        *En cours de développement*
        
        **Fonctionnalités à venir:**
        - Carte interactive des ventes
        - Performance par région/pays
        - Densité de la clientèle
        - Analyse des marchés émergents
        - Optimisation logistique
        """)
        
        # Placeholder avec des données basiques
        try:
            region_performance_query = """
                SELECT 
                    Region,
                    COUNT(*) as order_count,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin
                FROM merged
                WHERE Region IS NOT NULL
                GROUP BY Region
                ORDER BY total_sales DESC
                LIMIT 10
            """
            
            region_performance_data = self.bot.db.execute_query(region_performance_query)
            
            if region_performance_data is not None and not region_performance_data.empty:
                st.markdown("#### 📍 Performance par Région")
                st.dataframe(
                    region_performance_data,
                    width='stretch',
                    column_config={
                        "Region": "Région",
                        "order_count": "Commandes",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "margin": st.column_config.NumberColumn("Marge", format="%.1f%%")
                    }
                )
                
        except Exception as e:
            st.warning(f"⚠️ Données géographiques limitées: {e}")
    
    # ============================================================================
    # ONGLET EXPLORATION DONNÉES
    # ============================================================================
    
    def display_data_exploration(self):
        """Affiche l'interface d'exploration des données"""
        st.markdown("### 🔍 Exploration des Données")
        
        # Sélecteur de source
        source_tabs = st.tabs(["📊 Base SQL", "📁 Fichiers JSON", "🔄 Données Fusionnées"])
        
        with source_tabs[0]:
            self.explore_sql_data()
        
        with source_tabs[1]:
            self.explore_json_data()
        
        with source_tabs[2]:
            self.explore_merged_data()
    
    def explore_sql_data(self):
        """Exploration des données SQL"""
        st.markdown("#### 📊 Exploration de la Base SQL")
        
        # Sélection de la table
        tables = self.get_available_tables()
        selected_table = st.selectbox(
            "Sélectionnez une table",
            options=tables,
            index=0,
            key="sql_table_select"
        )
        
        if selected_table:
            # Options d'affichage
            col1, col2 = st.columns(2)
            with col1:
                limit = st.slider("Nombre de lignes", 10, 1000, 100, key="sql_limit")
            with col2:
                show_schema = st.checkbox("Afficher le schéma", value=True)
            
            # Afficher le schéma
            if show_schema:
                try:
                    schema_query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{selected_table}'
                        ORDER BY ordinal_position
                    """
                    schema_data = self.bot.db.execute_query(schema_query)
                    
                    if schema_data is not None and not schema_data.empty:
                        st.markdown("##### 🗂️ Schéma de la Table")
                        st.dataframe(
                            schema_data,
                            width='stretch',
                            column_config={
                                "column_name": "Colonne",
                                "data_type": "Type",
                                "is_nullable": "Nullable"
                            }
                        )
                except:
                    pass
            
            # Récupérer les données
            try:
                query = f'SELECT * FROM "{selected_table}" LIMIT {limit}'
                data = self.bot.db.execute_query(query)
                
                if data is not None and not data.empty:
                    st.markdown(f"##### 📋 Données ({len(data)} lignes)")
                    
                    # Options d'affichage avancées
                    display_col1, display_col2 = st.columns(2)
                    with display_col1:
                        selected_columns = st.multiselect(
                            "Colonnes à afficher",
                            options=data.columns.tolist(),
                            default=data.columns.tolist()[:min(8, len(data.columns))]
                        )
                    
                    with display_col2:
                        sort_column = st.selectbox(
                            "Trier par",
                            options=data.columns.tolist(),
                            index=0
                        )
                        sort_ascending = st.checkbox("Ordre croissant", value=True)
                    
                    # Filtrer et trier les données
                    filtered_data = data[selected_columns] if selected_columns else data
                    sorted_data = filtered_data.sort_values(by=sort_column, ascending=sort_ascending)
                    
                    # Afficher le tableau
                    st.dataframe(sorted_data, width='stretch')
                    
                    # Statistiques
                    with st.expander("📊 Statistiques descriptives"):
                        numeric_cols = sorted_data.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            st.dataframe(sorted_data[numeric_cols].describe(), width='stretch')
                        
                        # Informations sur les données
                        st.metric("Lignes", len(sorted_data))
                        st.metric("Colonnes", len(sorted_data.columns))
                        st.metric("Valeurs nulles", sorted_data.isnull().sum().sum())
                        
                else:
                    st.warning(f"⚠️ Aucune donnée dans la table '{selected_table}'")
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la récupération des données: {e}")
    
    def explore_json_data(self):
        """Exploration des données JSON"""
        st.info("""
        ### 📁 Exploration des Données JSON
        *Fonctionnalité NoSQL en développement*
        
        **À venir:**
        - Navigation dans les collections JSON
        - Requêtes NoSQL interactives
        - Visualisation des documents
        - Analyse de schéma dynamique
        """)
    
    def explore_merged_data(self):
        """Exploration des données fusionnées"""
        st.markdown("#### 🔄 Données Fusionnées (Table 'merged')")
        
        try:
            # Vérifier si la table merged existe
            check_query = "SELECT COUNT(*) as row_count FROM merged"
            check_data = self.bot.db.execute_query(check_query)
            
            if check_data is not None and not check_data.empty:
                row_count = check_data.iloc[0]["row_count"]
                st.success(f"✅ Table 'merged' disponible avec {row_count:,} lignes")
                
                # Options d'analyse
                analysis_type = st.selectbox(
                    "Type d'analyse",
                    options=["Aperçu général", "Analyse temporelle", "Analyse catégorielle", "Analyse géographique"],
                    key="merged_analysis_type"
                )
                
                if analysis_type == "Aperçu général":
                    self.display_merged_overview()
                elif analysis_type == "Analyse temporelle":
                    self.display_merged_temporal_analysis()
                elif analysis_type == "Analyse catégorielle":
                    self.display_merged_category_analysis()
                elif analysis_type == "Analyse géographique":
                    self.display_merged_geographic_analysis()
                    
            else:
                st.warning("⚠️ La table 'merged' n'existe pas ou est vide")
                
        except Exception as e:
            st.error(f"❌ Erreur accès table merged: {e}")
    
    def display_merged_overview(self):
        """Affiche un aperçu général des données fusionnées"""
        try:
            # Métriques clés
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_sales_query = "SELECT COALESCE(SUM(Sales), 0) as total_sales FROM merged"
                total_sales_data = self.bot.db.execute_query(total_sales_query)
                if total_sales_data is not None and not total_sales_data.empty:
                    total_sales = total_sales_data.iloc[0]["total_sales"]
                    st.metric("Ventes Totales", f"${total_sales:,.0f}")
            
            with col2:
                total_profit_query = "SELECT COALESCE(SUM(Profit), 0) as total_profit FROM merged"
                total_profit_data = self.bot.db.execute_query(total_profit_query)
                if total_profit_data is not None and not total_profit_data.empty:
                    total_profit = total_profit_data.iloc[0]["total_profit"]
                    st.metric("Profit Total", f"${total_profit:,.0f}")
            
            with col3:
                avg_margin_query = """
                    SELECT 
                        (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as avg_margin
                    FROM merged
                    WHERE Sales > 0
                """
                avg_margin_data = self.bot.db.execute_query(avg_margin_query)
                if avg_margin_data is not None and not avg_margin_data.empty:
                    avg_margin = avg_margin_data.iloc[0]["avg_margin"]
                    st.metric("Marge Moyenne", f"{avg_margin:.1f}%")
            
            with col4:
                return_rate_query = """
                    SELECT 
                        (SUM(CASE WHEN Is_Returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as return_rate
                    FROM merged
                """
                return_rate_data = self.bot.db.execute_query(return_rate_query)
                if return_rate_data is not None and not return_rate_data.empty:
                    return_rate = return_rate_data.iloc[0]["return_rate"]
                    st.metric("Taux de Retour", f"{return_rate:.1f}%")
            
            # Distribution des données
            st.markdown("##### 📊 Distribution des Données")
            
            dist_col1, dist_col2 = st.columns(2)
            
            with dist_col1:
                # Distribution par catégorie
                category_dist_query = """
                    SELECT 
                        Category,
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
                    FROM merged
                    WHERE Category IS NOT NULL
                    GROUP BY Category
                    ORDER BY count DESC
                """
                category_dist_data = self.bot.db.execute_query(category_dist_query)
                
                if category_dist_data is not None and not category_dist_data.empty:
                    fig = px.pie(
                        category_dist_data,
                        values="count",
                        names="Category",
                        title="Répartition par Catégorie",
                        hole=0.3
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            with dist_col2:
                # Distribution par région
                region_dist_query = """
                    SELECT 
                        Region,
                        COUNT(*) as count,
                        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
                    FROM merged
                    WHERE Region IS NOT NULL
                    GROUP BY Region
                    ORDER BY count DESC
                    LIMIT 10
                """
                region_dist_data = self.bot.db.execute_query(region_dist_query)
                
                if region_dist_data is not None and not region_dist_data.empty:
                    fig = px.bar(
                        region_dist_data,
                        x="Region",
                        y="count",
                        title="Top 10 Régions",
                        color="count",
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
            
            # Aperçu des données brutes
            st.markdown("##### 📋 Aperçu des Données")
            
            preview_query = "SELECT * FROM merged LIMIT 50"
            preview_data = self.bot.db.execute_query(preview_query)
            
            if preview_data is not None and not preview_data.empty:
                st.dataframe(preview_data, width='stretch')
                
        except Exception as e:
            st.error(f"❌ Erreur aperçu merged: {e}")
    
    def display_merged_temporal_analysis(self):
        """Analyse temporelle des données fusionnées"""
        st.markdown("##### 📅 Analyse Temporelle")
        
        try:
            # Sélecteur de période
            period = st.selectbox(
                "Période d'analyse",
                options=["Journalier", "Hebdomadaire", "Mensuel", "Trimestriel", "Annuel"],
                key="temporal_period"
            )
            
            # Requête selon la période
            period_map = {
                "Journalier": "%Y-%m-%d",
                "Hebdomadaire": "%Y-%W",
                "Mensuel": "%Y-%m",
                "Trimestriel": "%Y-%m",
                "Annuel": "%Y"
            }
            
            date_format = period_map.get(period, "%Y-%m")
            
            temporal_query = f"""
                SELECT 
                    strftime('{date_format}', "Order Date") as period,
                    COUNT(*) as transaction_count,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    AVG(Sales) as avg_sales_per_transaction,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin_percentage
                FROM merged
                WHERE "Order Date" IS NOT NULL
                GROUP BY strftime('{date_format}', "Order Date")
                ORDER BY period
            """
            
            temporal_data = self.bot.db.execute_query(temporal_query)
            
            if temporal_data is not None and not temporal_data.empty:
                # Graphique des ventes dans le temps
                fig = px.line(
                    temporal_data,
                    x="period",
                    y="total_sales",
                    title=f"📈 Ventes {period.lower()}",
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
                
                # Tableau détaillé
                st.dataframe(
                    temporal_data,
                    width='stretch',
                    column_config={
                        "period": "Période",
                        "transaction_count": "Transactions",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "avg_sales_per_transaction": st.column_config.NumberColumn("Moyenne/Trans", format="$%.2f"),
                        "margin_percentage": st.column_config.NumberColumn("Marge", format="%.1f%%")
                    }
                )
            else:
                st.warning("⚠️ Aucune donnée temporelle disponible")
                
        except Exception as e:
            st.error(f"❌ Erreur analyse temporelle: {e}")
    
    def display_merged_category_analysis(self):
        """Analyse catégorielle des données fusionnées"""
        st.markdown("##### 🏷️ Analyse par Catégorie")
        
        try:
            category_query = """
                SELECT 
                    Category,
                    COUNT(*) as transaction_count,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    AVG(Sales) as avg_sales_per_transaction,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin_percentage,
                    SUM(CASE WHEN Is_Returned = 1 THEN 1 ELSE 0 END) as return_count,
                    (SUM(CASE WHEN Is_Returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as return_rate
                FROM merged
                WHERE Category IS NOT NULL
                GROUP BY Category
                ORDER BY total_sales DESC
            """
            
            category_data = self.bot.db.execute_query(category_query)
            
            if category_data is not None and not category_data.empty:
                # Graphique des ventes par catégorie
                fig = px.bar(
                    category_data,
                    x="Category",
                    y="total_sales",
                    title="📊 Ventes par Catégorie",
                    color="margin_percentage",
                    color_continuous_scale="Viridis",
                    hover_data=["transaction_count", "return_rate"]
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
                
                # Tableau détaillé
                st.dataframe(
                    category_data,
                    width='stretch',
                    column_config={
                        "Category": "Catégorie",
                        "transaction_count": "Transactions",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "avg_sales_per_transaction": st.column_config.NumberColumn("Moyenne/Trans", format="$%.2f"),
                        "margin_percentage": st.column_config.NumberColumn("Marge", format="%.1f%%"),
                        "return_count": "Retours",
                        "return_rate": st.column_config.NumberColumn("Taux Retour", format="%.1f%%")
                    }
                )
            else:
                st.warning("⚠️ Aucune donnée catégorielle disponible")
                
        except Exception as e:
            st.error(f"❌ Erreur analyse catégorielle: {e}")
    
    def display_merged_geographic_analysis(self):
        """Analyse géographique des données fusionnées"""
        st.markdown("##### 🌍 Analyse Géographique")
        
        try:
            geographic_query = """
                SELECT 
                    Region,
                    COUNT(*) as transaction_count,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    AVG(Sales) as avg_sales_per_transaction,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as margin_percentage,
                    COUNT(DISTINCT "Customer ID") as unique_customers
                FROM merged
                WHERE Region IS NOT NULL
                GROUP BY Region
                ORDER BY total_sales DESC
            """
            
            geographic_data = self.bot.db.execute_query(geographic_query)
            
            if geographic_data is not None and not geographic_data.empty:
                # Graphique des ventes par région
                fig = px.bar(
                    geographic_data,
                    x="Region",
                    y="total_sales",
                    title="📊 Ventes par Région",
                    color="margin_percentage",
                    color_continuous_scale="Viridis",
                    hover_data=["unique_customers", "avg_sales_per_transaction"]
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
                
                # Tableau détaillé
                st.dataframe(
                    geographic_data,
                    width='stretch',
                    column_config={
                        "Region": "Région",
                        "transaction_count": "Transactions",
                        "total_sales": st.column_config.NumberColumn("Ventes", format="$%.2f"),
                        "total_profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                        "avg_sales_per_transaction": st.column_config.NumberColumn("Moyenne/Trans", format="$%.2f"),
                        "margin_percentage": st.column_config.NumberColumn("Marge", format="%.1f%%"),
                        "unique_customers": "Clients Uniques"
                    }
                )
            else:
                st.warning("⚠️ Aucune donnée géographique disponible")
                
        except Exception as e:
            st.error(f"❌ Erreur analyse géographique: {e}")
    
    # ============================================================================
    # ONGLET INSIGHTS AUTOMATIQUES
    # ============================================================================
    
    def display_auto_insights(self):
        """Affiche les insights automatiques générés"""
        st.markdown("### 🤖 Insights Automatiques")
        
        # Bouton de génération
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Générer de nouveaux insights", width='stretch'):
                with st.spinner("Génération des insights en cours..."):
                    st.session_state.auto_insights = self.generate_auto_insights()
                    st.success("✅ Insights générés avec succès!")
        
        with col2:
            insight_count = len(st.session_state.get("auto_insights", []))
            st.info(f"📊 {insight_count} insights disponibles")
        
        # Affichage des insights
        insights = st.session_state.get("auto_insights", [])
        
        if not insights:
            st.warning("⚠️ Aucun insight disponible. Cliquez sur 'Générer' pour créer des insights.")
            return
        
        # Filtrage des insights
        insight_types = list(set([insight.get("type", "general") for insight in insights]))
        selected_type = st.selectbox(
            "Filtrer par type",
            options=["Tous"] + insight_types,
            key="insight_filter"
        )
        
        # Afficher les insights filtrés
        filtered_insights = insights
        if selected_type != "Tous":
            filtered_insights = [i for i in insights if i.get("type") == selected_type]
        
        # Affichage paginé
        items_per_page = 5
        total_pages = max(1, (len(filtered_insights) + items_per_page - 1) // items_per_page)
        
        # Sélecteur de page
        if total_pages > 1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="insight_page"
            )
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_insights))
            page_insights = filtered_insights[start_idx:end_idx]
        else:
            page_insights = filtered_insights
        
        # Afficher chaque insight
        for idx, insight in enumerate(page_insights):
            self.display_single_insight(insight, idx)
    
    def generate_auto_insights(self):
        """Génère des insights automatiques à partir des données"""
        insights = []
        
        try:
            # Insight 1: Top produits
            query = """
                SELECT 
                    "Product Name", 
                    SUM(Sales) as total_sales, 
                    SUM(Profit) as total_profit,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as profit_margin
                FROM merged 
                GROUP BY "Product Name" 
                ORDER BY total_sales DESC 
                LIMIT 5
            """
            data = self.bot.db.execute_query(query)
            
            if data is not None and not data.empty:
                top_product = data.iloc[0]
                insights.append({
                    "id": "top_products",
                    "type": "sales",
                    "title": "🏆 Produit le Plus Vendu",
                    "description": f"**{top_product['Product Name']}** génère ${top_product['total_sales']:,.0f} de ventes avec une marge de {top_product['profit_margin']:.1f}%.",
                    "data": data,
                    "severity": "high",
                    "recommendation": "Augmenter le stock et la promotion de ce produit.",
                    "analysis_question": "Quels sont les produits les plus vendus et leur rentabilité ?"
                })
            
            # Insight 2: Régions performantes
            query = """
                SELECT 
                    Region,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    COUNT(DISTINCT "Customer ID") as unique_customers
                FROM merged
                WHERE Region IS NOT NULL
                GROUP BY Region
                ORDER BY total_sales DESC
                LIMIT 3
            """
            data = self.bot.db.execute_query(query)
            
            if data is not None and not data.empty:
                top_region = data.iloc[0]
                insights.append({
                    "id": "top_regions",
                    "type": "geographic",
                    "title": "📍 Région la Plus Performante",
                    "description": f"La région **{top_region['Region']}** génère ${top_region['total_sales']:,.0f} avec {top_region['unique_customers']} clients uniques.",
                    "data": data,
                    "severity": "medium",
                    "recommendation": "Augmenter les investissements marketing dans cette région.",
                    "analysis_question": "Quelle région a les meilleures performances commerciales ?"
                })
            
            # Insight 3: Marge par catégorie
            query = """
                SELECT 
                    Category,
                    (SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)) as profit_margin,
                    SUM(Sales) as total_sales
                FROM merged
                WHERE Category IS NOT NULL
                GROUP BY Category
                ORDER BY profit_margin DESC
                LIMIT 3
            """
            data = self.bot.db.execute_query(query)
            
            if data is not None and not data.empty:
                top_category = data.iloc[0]
                insights.append({
                    "id": "top_margin_categories",
                    "type": "profit",
                    "title": "💰 Catégorie la Plus Rentable",
                    "description": f"La catégorie **{top_category['Category']}** a la meilleure marge: {top_category['profit_margin']:.1f}% (${top_category['total_sales']:,.0f} de ventes).",
                    "data": data,
                    "severity": "high",
                    "recommendation": "Développer l'assortiment dans cette catégorie.",
                    "analysis_question": "Quelles catégories ont les meilleures marges ?"
                })
            
            # Insight 4: Taux de retour problématique
            query = """
                SELECT 
                    "Product Name",
                    (SUM(CASE WHEN Is_Returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as return_rate,
                    COUNT(*) as total_orders
                FROM merged
                GROUP BY "Product Name"
                HAVING total_orders > 10 AND return_rate > 10
                ORDER BY return_rate DESC
                LIMIT 3
            """
            data = self.bot.db.execute_query(query)
            
            if data is not None and not data.empty:
                problem_product = data.iloc[0]
                insights.append({
                    "id": "high_return_products",
                    "type": "returns",
                    "title": "⚠️ Produit à Taux de Retour Élevé",
                    "description": f"**{problem_product['Product Name']}** a un taux de retour de {problem_product['return_rate']:.1f}% sur {problem_product['total_orders']} commandes.",
                    "data": data,
                    "severity": "critical",
                    "recommendation": "Investiguer les causes des retours et améliorer la qualité.",
                    "analysis_question": "Quels produits ont les taux de retour les plus élevés ?"
                })
            
            # Insight 5: Saisonnalité
            query = """
                SELECT 
                    strftime('%m', "Order Date") as month,
                    SUM(Sales) as monthly_sales
                FROM merged
                WHERE "Order Date" IS NOT NULL
                GROUP BY strftime('%m', "Order Date")
                ORDER BY monthly_sales DESC
                LIMIT 1
            """
            data = self.bot.db.execute_query(query)
            
            if data is not None and not data.empty:
                best_month = data.iloc[0]
                month_names = {
                    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
                    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
                    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
                }
                month_name = month_names.get(best_month["month"], best_month["month"])
                
                insights.append({
                    "id": "seasonality",
                    "type": "temporal",
                    "title": "📅 Mois le Plus Performant",
                    "description": f"Le mois de **{month_name}** génère le plus de ventes: ${best_month['monthly_sales']:,.0f}.",
                    "data": data,
                    "severity": "medium",
                    "recommendation": "Préparer des promotions spéciales pour ce mois.",
                    "analysis_question": "Quel est le mois le plus performant de l'année ?"
                })
            
        except Exception as e:
            app_logger.error(f"❌ Erreur génération insights: {e}")
        
        return insights
    
    def display_single_insight(self, insight: Dict, idx: int):
        """Affiche un insight individuel"""
        # Déterminer la couleur en fonction de la sévérité
        severity_colors = {
            "critical": "#ef4444",
            "high": "#f59e0b",
            "medium": "#3b82f6",
            "low": "#10b981"
        }
        
        color = severity_colors.get(insight.get("severity", "medium"), "#3b82f6")
        
        with st.container():
            st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 10px;
                    border-left: 5px solid {color};
                    padding: 1.5rem;
                    margin: 1rem 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h3 style="margin: 0 0 0.5rem 0; color: {color};">{insight['title']}</h3>
                            <p style="margin: 0 0 1rem 0; color: #64748b;">{insight['description']}</p>
                        </div>
                        <span class="badge" style="background-color: {color}20; color: {color}; border-color: {color}40;">
                            {insight.get('type', 'general').upper()}
                        </span>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <strong>💡 Recommandation:</strong> {insight.get('recommendation', 'Aucune recommandation disponible.')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Actions
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button(
                    "🔍 Analyser cet insight",
                    key=f"analyze_insight_{idx}",
                    width='stretch'
                ):
                    st.session_state.current_question = insight["analysis_question"]
                    st.rerun()
            
            with col2:
                if insight.get("data") is not None:
                    with st.popover("📊 Voir les données"):
                        st.dataframe(insight["data"], width='stretch')
            
            with col3:
                if st.button(
                    "📌 Épingler",
                    key=f"pin_insight_{idx}",
                    width='stretch'
                ):
                    st.success("✅ Insight épinglé")
            
            st.markdown("---")
    
    # ============================================================================
    # ONGLET CONFIGURATION SYSTÈME
    # ============================================================================
    
    def display_system_configuration(self):
        """Affiche le panneau de configuration système"""
        st.markdown("### ⚙️ Configuration du Système")
        
        # Onglets de configuration
        config_tabs = st.tabs(["🔧 Paramètres", "📊 Base de Données", "🧠 Intelligence Artificielle", "📈 Performances"])
        
        with config_tabs[0]:
            self.display_general_settings()
        
        with config_tabs[1]:
            self.display_database_settings()
        
        with config_tabs[2]:
            self.display_ai_settings()
        
        with config_tabs[3]:
            self.display_performance_settings()
    
    def display_general_settings(self):
        """Affiche les paramètres généraux"""
        st.markdown("#### 🔧 Paramètres Généraux")
        
        # Interface
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Thème",
                options=["light", "dark", "auto"],
                index=0,
                key="theme_setting"
            )
            st.session_state.theme_mode = theme
        
        with col2:
            language = st.selectbox(
                "Langue par défaut",
                options=["Français", "English", "Auto"],
                index=2,
                key="default_language"
            )
        
        # Affichage
        st.markdown("##### 👁️ Affichage")
        
        display_col1, display_col2 = st.columns(2)
        
        with display_col1:
            show_animations = st.checkbox(
                "Animations",
                value=st.session_state.animation_enabled,
                key="animations_setting"
            )
            st.session_state.animation_enabled = show_animations
        
        with display_col2:
            auto_refresh = st.checkbox(
                "Auto-rafraîchissement",
                value=st.session_state.auto_refresh,
                key="auto_refresh_setting"
            )
            st.session_state.auto_refresh = auto_refresh
        
        # Sauvegarde
        st.markdown("##### 💾 Sauvegarde")
        
        backup_col1, backup_col2 = st.columns(2)
        
        with backup_col1:
            if st.button("💾 Sauvegarder la configuration", width='stretch'):
                self.save_configuration()
                st.success("✅ Configuration sauvegardée")
        
        with backup_col2:
            if st.button("🔄 Restaurer par défaut", width='stretch'):
                self.restore_default_configuration()
                st.success("✅ Configuration restaurée")
    
    def display_database_settings(self):
        """Affiche les paramètres de la base de données"""
        st.markdown("#### 📊 Configuration Base de Données")
        
        # Statut de la base
        metrics = st.session_state.get("cached_metrics", {})
        db_info = metrics.get("database_info", {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            db_available = db_info.get("available", False)
            status = "✅ Connectée" if db_available else "❌ Non connectée"
            st.metric("Statut", status)
        
        with col2:
            table_count = len(db_info.get("tables", []))
            st.metric("Tables", table_count)
        
        with col3:
            column_count = db_info.get("columns_count", 0)
            st.metric("Colonnes", column_count)
        
        # Actions sur la base
        st.markdown("##### ⚡ Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🔄 Rafraîchir le schéma", width='stretch'):
                self.refresh_schema()
                st.success("✅ Schéma rafraîchi")
                st.rerun()
        
        with action_col2:
            if st.button("🧹 Vider le cache", width='stretch'):
                self.clear_cache()
                st.success("✅ Cache vidé")
                st.rerun()
        
        with action_col3:
            if st.button("📋 Tester la connexion", width='stretch'):
                test_result = self.test_query("SELECT 1 as test")
                if test_result.get("success"):
                    st.success("✅ Connexion OK")
                else:
                    st.error("❌ Échec connexion")
        
        # Informations détaillées
        with st.expander("📋 Informations détaillées"):
            if db_info:
                st.json(db_info, expanded=False)
    
    def display_ai_settings(self):
        """Affiche les paramètres de l'IA"""
        st.markdown("#### 🧠 Configuration Intelligence Artificielle")
        
        # Statut IA
        metrics = st.session_state.get("cached_metrics", {})
        ai_status = metrics.get("ai_status", {})
        
        # Fournisseurs disponibles
        st.markdown("##### 🤖 Fournisseurs Disponibles")
        
        providers = ai_status.get("providers", {})
        
        provider_cols = st.columns(len(providers) if providers else 1)
        
        if providers:
            for idx, (provider_name, is_available) in enumerate(providers.items()):
                with provider_cols[idx]:
                    icon = "✅" if is_available else "❌"
                    color = "green" if is_available else "red"
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="font-size: 2rem;">{icon}</div>
                            <div style="font-weight: bold; color: {color};">{provider_name.upper()}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Aucun fournisseur IA disponible")
        
        # Fournisseur actif
        active_provider = ai_status.get("active_provider", "local")
        st.info(f"**Fournisseur actif:** {active_provider.upper()}")
        
        # Paramètres de génération
        st.markdown("##### ⚙️ Paramètres de Génération")
        
        gen_col1, gen_col2, gen_col3 = st.columns(3)
        
        with gen_col1:
            temperature = st.slider(
                "Température",
                min_value=0.0,
                max_value=2.0,
                value=0.1,
                step=0.1,
                key="temperature_setting",
                help="Contrôle la créativité des réponses (0 = précis, 2 = créatif)"
            )
        
        with gen_col2:
            max_tokens = st.slider(
                "Tokens maximum",
                min_value=100,
                max_value=4000,
                value=2000,
                step=100,
                key="max_tokens_setting",
                help="Nombre maximum de tokens par réponse"
            )
        
        with gen_col3:
            top_p = st.slider(
                "Top-P",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.1,
                key="top_p_setting",
                help="Contrôle la diversité des réponses"
            )
        
        # Test de l'IA
        st.markdown("##### 🧪 Test de l'IA")
        
        test_question = st.text_input(
            "Question de test",
            value="Quelle est la somme des ventes totales ?",
            key="ai_test_question"
        )
        
        if st.button("🧪 Tester l'IA", width='stretch'):
            with st.spinner("Test en cours..."):
                result = self.bot.process_question(test_question)
                
                if result.get("success"):
                    st.success("✅ Test réussi")
                    st.info(f"Fournisseur utilisé: {result['execution']['provider']}")
                    st.info(f"Temps d'exécution: {result['execution']['time']:.2f}s")
                else:
                    st.error("❌ Test échoué")
    
    def display_performance_settings(self):
        """Affiche les paramètres de performance"""
        st.markdown("#### 📈 Métriques de Performance")
        
        # Récupérer les métriques
        metrics = st.session_state.get("cached_metrics", {})
        exec_metrics = metrics.get("execution_metrics", {})
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_questions = exec_metrics.get("total_questions", 0)
            st.metric("Questions totales", total_questions)
        
        with col2:
            success_rate = exec_metrics.get("success_rate", 0)
            st.metric("Taux de succès", f"{success_rate:.1f}%")
        
        with col3:
            avg_time = exec_metrics.get("average_execution_time", 0)
            st.metric("Temps moyen", f"{avg_time:.2f}s")
        
        with col4:
            fallback_used = exec_metrics.get("fallback_used", 0)
            st.metric("Fallbacks utilisés", fallback_used)
        
        # Graphique de performance
        st.markdown("##### 📊 Évolution des Performances")
        
        # Placeholder pour un futur graphique
        st.info("""
        **Graphique de performance à venir:**
        - Évolution du temps de réponse
        - Taux de succès historique
        - Utilisation des fournisseurs IA
        - Analyse des erreurs
        """)
        
        # Optimisation
        st.markdown("##### ⚡ Optimisation")
        
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            cache_ttl = st.slider(
                "Durée de cache (secondes)",
                min_value=10,
                max_value=600,
                value=60,
                step=10,
                key="cache_ttl_setting",
                help="Durée de conservation des données en cache"
            )
        
        with opt_col2:
            max_retries = st.slider(
                "Tentatives SQL maximum",
                min_value=1,
                max_value=5,
                value=3,
                step=1,
                key="max_retries_setting",
                help="Nombre maximum de tentatives pour les requêtes SQL"
            )
        
        # Logs de performance
        with st.expander("📝 Logs de Performance"):
            if exec_metrics:
                st.json(exec_metrics, expanded=False)
            else:
                st.warning("Aucune métrique de performance disponible")
    
    def save_configuration(self):
        """Sauvegarde la configuration"""
        config = {
            "theme_mode": st.session_state.theme_mode,
            "animation_enabled": st.session_state.animation_enabled,
            "auto_refresh": st.session_state.auto_refresh,
            "show_technical_details": st.session_state.show_technical_details,
            "ai_provider_preference": st.session_state.ai_provider_preference,
            "response_language": st.session_state.response_language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Sauvegarder dans session_state
        st.session_state.saved_configuration = config
    
    def restore_default_configuration(self):
        """Restaure la configuration par défaut"""
        defaults = {
            "theme_mode": "light",
            "animation_enabled": True,
            "auto_refresh": True,
            "show_technical_details": False,
            "ai_provider_preference": "auto",
            "response_language": "auto"
        }
        
        for key, value in defaults.items():
            st.session_state[key] = value
    
    # ============================================================================
    # ONGLET HISTORIQUE & EXPORT
    # ============================================================================
    
    def display_history_and_export(self):
        """Affiche l'historique et les options d'export"""
        st.markdown("### 📚 Historique & Export")
        
        # Onglets
        history_tabs = st.tabs(["🗃️ Historique des Analyses", "⭐ Questions Favorites", "📤 Export des Données"])
        
        with history_tabs[0]:
            self.display_analysis_history()
        
        with history_tabs[1]:
            self.display_favorite_questions()
        
        with history_tabs[2]:
            self.display_data_export()
    
    def display_analysis_history(self):
        """Affiche l'historique des analyses"""
        history = st.session_state.get("chat_history", [])
        
        if not history:
            st.info("ℹ️ Aucune analyse dans l'historique")
            return
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.date_input(
                "Filtrer par date",
                value=None,
                key="history_date_filter"
            )
        
        with col2:
            success_filter = st.selectbox(
                "Filtrer par statut",
                options=["Tous", "Succès", "Échecs"],
                key="history_status_filter"
            )
        
        with col3:
            search_term = st.text_input(
                "Rechercher dans l'historique",
                key="history_search"
            )
        
        # Filtrer l'historique
        filtered_history = history
        
        if date_filter:
            filtered_history = [
                h for h in filtered_history 
                if datetime.fromisoformat(h["timestamp"]).date() == date_filter
            ]
        
        if success_filter == "Succès":
            filtered_history = [h for h in filtered_history if h["result"].get("success")]
        elif success_filter == "Échecs":
            filtered_history = [h for h in filtered_history if not h["result"].get("success")]
        
        if search_term:
            filtered_history = [
                h for h in filtered_history 
                if search_term.lower() in h["question"].lower()
            ]
        
        # Pagination
        items_per_page = 10
        total_pages = max(1, (len(filtered_history) + items_per_page - 1) // items_per_page)
        
        if total_pages > 1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="history_page"
            )
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_history))
            page_history = filtered_history[start_idx:end_idx]
        else:
            page_history = filtered_history
        
        # Afficher l'historique
        st.markdown(f"**{len(filtered_history)} analyses trouvées**")
        
        for idx, entry in enumerate(page_history):
            self.display_history_entry(entry, idx)
    
    def display_history_entry(self, entry: Dict, idx: int):
        """Affiche une entrée d'historique"""
        timestamp = datetime.fromisoformat(entry["timestamp"])
        result = entry["result"]
        
        with st.expander(f"📅 {timestamp.strftime('%H:%M')} - {entry['question'][:50]}...", expanded=False):
            # En-tête
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**Question:** {entry['question']}")
            
            with col2:
                status = "✅" if result.get("success") else "❌"
                st.markdown(f"**Statut:** {status}")
            
            with col3:
                st.markdown(f"**Temps:** {result.get('execution', {}).get('time', 0):.2f}s")
            
            # Insight
            if result.get("insight"):
                st.markdown("**💡 Insight:**")
                st.info(result["insight"][:200] + "..." if len(result["insight"]) > 200 else result["insight"])
            
            # Actions
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("🔄 Réanalyser", key=f"reanalyze_{idx}"):
                    st.session_state.current_question = entry["question"]
                    st.rerun()
            
            with action_col2:
                if st.button("⭐ Favoris", key=f"favorite_{idx}"):
                    self.save_to_favorites(entry["question"])
                    st.success("✅ Ajouté aux favoris")
            
            with action_col3:
                if st.button("🗑️ Supprimer", key=f"delete_{idx}"):
                    st.session_state.chat_history.remove(entry)
                    st.success("✅ Supprimé de l'historique")
                    st.rerun()
    
    def display_favorite_questions(self):
        """Affiche les questions favorites"""
        favorites = st.session_state.get("favorite_queries", [])
        
        if not favorites:
            st.info("ℹ️ Aucune question favorite")
            return
        
        st.markdown(f"**{len(favorites)} questions favorites**")
        
        for idx, favorite in enumerate(favorites):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"• **{favorite['question']}**")
                st.caption(f"Ajouté le: {favorite.get('timestamp', 'N/A')}")
            
            with col2:
                col2_1, col2_2 = st.columns(2)
                
                with col2_1:
                    if st.button("🔍", key=f"use_favorite_{idx}"):
                        st.session_state.current_question = favorite["question"]
                        st.rerun()
                
                with col2_2:
                    if st.button("🗑️", key=f"remove_favorite_{idx}"):
                        st.session_state.favorite_queries.pop(idx)
                        st.success("✅ Retiré des favoris")
                        st.rerun()
        
        # Export des favoris
        if favorites:
            st.markdown("---")
            favorite_data = json.dumps(favorites, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Exporter les favoris",
                data=favorite_data,
                file_name=f"insightbot_favorites_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                width='stretch'
            )
    
    def display_data_export(self):
        """Affiche les options d'export de données"""
        st.markdown("#### 📤 Export des Données")
        
        # Options d'export
        export_type = st.selectbox(
            "Type d'export",
            options=["Données complètes", "Rapport d'analyse", "Configuration", "Historique"],
            key="export_type"
        )
        
        if export_type == "Données complètes":
            self.export_complete_data()
        elif export_type == "Rapport d'analyse":
            self.export_analysis_report()
        elif export_type == "Configuration":
            self.export_configuration()
        elif export_type == "Historique":
            self.export_history()
    
    def export_complete_data(self):
        """Export des données complètes"""
        st.markdown("##### 📊 Export des Données Complètes")
        
        # Sélection des tables
        tables = self.get_available_tables()
        selected_tables = st.multiselect(
            "Tables à exporter",
            options=tables,
            default=tables,
            key="export_tables"
        )
        
        # Format d'export
        export_format = st.radio(
            "Format",
            options=["CSV", "JSON", "Excel"],
            horizontal=True,
            key="export_format"
        )
        
        if st.button("📥 Générer l'export", width='stretch'):
            with st.spinner("Génération de l'export en cours..."):
                try:
                    export_data = {}
                    
                    for table in selected_tables:
                        query = f'SELECT * FROM "{table}"'
                        data = self.bot.db.execute_query(query)
                        
                        if data is not None and not data.empty:
                            export_data[table] = data
                    
                    if export_data:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        if export_format == "CSV":
                            # Créer un ZIP avec tous les CSV
                            import zipfile
                            import io
                            
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                                for table_name, table_data in export_data.items():
                                    csv_buffer = io.StringIO()
                                    table_data.to_csv(csv_buffer, index=False)
                                    zip_file.writestr(f"{table_name}.csv", csv_buffer.getvalue())
                            
                            zip_buffer.seek(0)
                            
                            st.download_button(
                                label="📥 Télécharger le ZIP",
                                data=zip_buffer,
                                file_name=f"insightbot_data_export_{timestamp}.zip",
                                mime="application/zip",
                                width='stretch'
                            )
                        
                        elif export_format == "JSON":
                            json_data = {}
                            for table_name, table_data in export_data.items():
                                json_data[table_name] = table_data.to_dict('records')
                            
                            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                            
                            st.download_button(
                                label="📥 Télécharger le JSON",
                                data=json_str,
                                file_name=f"insightbot_data_export_{timestamp}.json",
                                mime="application/json",
                                width='stretch'
                            )
                        
                        elif export_format == "Excel":
                            # Créer un fichier Excel avec plusieurs onglets
                            excel_buffer = io.BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                for table_name, table_data in export_data.items():
                                    table_data.to_excel(writer, sheet_name=table_name[:31], index=False)
                            
                            excel_buffer.seek(0)
                            
                            st.download_button(
                                label="📥 Télécharger Excel",
                                data=excel_buffer,
                                file_name=f"insightbot_data_export_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                width='stretch'
                            )
                        
                        st.success("✅ Export généré avec succès")
                    else:
                        st.warning("⚠️ Aucune donnée à exporter")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'export: {e}")
    
    def export_analysis_report(self):
        """Export d'un rapport d'analyse"""
        st.markdown("##### 📄 Rapport d'Analyse")
        
        # Sélection des analyses à inclure
        history = st.session_state.get("chat_history", [])
        
        if not history:
            st.warning("⚠️ Aucune analyse disponible pour l'export")
            return
        
        analysis_options = [f"{h['question'][:50]}..." for h in history]
        selected_indices = st.multiselect(
            "Analyses à inclure",
            options=range(len(analysis_options)),
            format_func=lambda x: analysis_options[x],
            key="export_analyses"
        )
        
        # Format du rapport
        report_format = st.radio(
            "Format du rapport",
            options=["HTML", "PDF", "Markdown"],
            horizontal=True,
            key="report_format"
        )
        
        if st.button("📊 Générer le rapport", width='stretch'):
            with st.spinner("Génération du rapport en cours..."):
                try:
                    # Préparer les données du rapport
                    report_data = {
                        "generated_at": datetime.now().isoformat(),
                        "analyses": []
                    }
                    
                    for idx in selected_indices:
                        if idx < len(history):
                            entry = history[idx]
                            analysis = {
                                "question": entry["question"],
                                "timestamp": entry["timestamp"],
                                "insight": entry["result"].get("insight", ""),
                                "recommendations": entry["result"].get("business_recommendations", []),
                                "execution_time": entry["result"].get("execution", {}).get("time", 0),
                                "success": entry["result"].get("success", False)
                            }
                            report_data["analyses"].append(analysis)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    if report_format == "HTML":
                        # Générer un rapport HTML simple
                        html_report = self._generate_html_report(report_data)
                        
                        st.download_button(
                            label="📥 Télécharger HTML",
                            data=html_report,
                            file_name=f"insightbot_report_{timestamp}.html",
                            mime="text/html",
                            width='stretch'
                        )
                    
                    elif report_format == "PDF":
                        st.info("⚠️ Export PDF disponible dans la version pro")
                    
                    elif report_format == "Markdown":
                        markdown_report = self._generate_markdown_report(report_data)
                        
                        st.download_button(
                            label="📥 Télécharger Markdown",
                            data=markdown_report,
                            file_name=f"insightbot_report_{timestamp}.md",
                            mime="text/markdown",
                            width='stretch'
                        )
                    
                    st.success("✅ Rapport généré avec succès")
                    
                except Exception as e:
                    st.error(f"❌ Erreur génération rapport: {e}")
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """Génère un rapport HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Rapport InsightBot - {datetime.now().strftime('%d/%m/%Y')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .analysis {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .success {{ border-left: 5px solid #10b981; }}
                .failure {{ border-left: 5px solid #ef4444; }}
                .recommendation {{ background: #f0f9ff; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Rapport InsightBot AI</h1>
                <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <p>{len(report_data['analyses'])} analyses incluses</p>
            </div>
        """
        
        # Statistiques
        success_count = sum(1 for a in report_data['analyses'] if a['success'])
        total_time = sum(a['execution_time'] for a in report_data['analyses'])
        
        html += f"""
            <div class="stats">
                <div class="stat">
                    <h3>📊 Statistiques</h3>
                    <p><strong>Analyses:</strong> {len(report_data['analyses'])}</p>
                    <p><strong>Réussites:</strong> {success_count}</p>
                    <p><strong>Temps total:</strong> {total_time:.2f}s</p>
                    <p><strong>Taux de réussite:</strong> {(success_count/len(report_data['analyses'])*100 if report_data['analyses'] else 0):.1f}%</p>
                </div>
            </div>
        """
        
        # Analyses détaillées
        for i, analysis in enumerate(report_data['analyses'], 1):
            status_class = "success" if analysis['success'] else "failure"
            status_icon = "✅" if analysis['success'] else "❌"
            
            html += f"""
                <div class="analysis {status_class}">
                    <h3>{status_icon} Analyse #{i}: {analysis['question'][:100]}</h3>
                    <p><strong>Date:</strong> {analysis['timestamp']}</p>
                    <p><strong>Temps d'exécution:</strong> {analysis['execution_time']:.2f}s</p>
                    
                    <h4>💡 Insight:</h4>
                    <p>{analysis['insight']}</p>
            """
            
            if analysis['recommendations']:
                html += "<h4>🎯 Recommandations:</h4>"
                for rec in analysis['recommendations']:
                    html += f'<div class="recommendation">• {rec}</div>'
            
            html += "</div>"
        
        html += """
            <footer style="margin-top: 50px; padding: 20px; text-align: center; color: #666; border-top: 1px solid #ddd;">
                <p>Rapport généré par InsightBot AI - https://github.com/your-repo/insightbot</p>
            </footer>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, report_data: Dict) -> str:
        """Génère un rapport Markdown"""
        md = f"""# 🤖 Rapport InsightBot AI\n\n"""
        md += f"**Généré le:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
        md += f"**Analyses incluses:** {len(report_data['analyses'])}\n\n"
        
        # Statistiques
        success_count = sum(1 for a in report_data['analyses'] if a['success'])
        total_time = sum(a['execution_time'] for a in report_data['analyses'])
        
        md += f"""## 📊 Statistiques\n\n"""
        md += f"- **Total analyses:** {len(report_data['analyses'])}\n"
        md += f"- **Analyses réussies:** {success_count}\n"
        md += f"- **Temps total d'exécution:** {total_time:.2f}s\n"
        md += f"- **Taux de réussite:** {(success_count/len(report_data['analyses'])*100 if report_data['analyses'] else 0):.1f}%\n\n"
        
        # Analyses détaillées
        md += f"""## 📋 Analyses Détailées\n\n"""
        
        for i, analysis in enumerate(report_data['analyses'], 1):
            status_icon = "✅" if analysis['success'] else "❌"
            
            md += f"""### {status_icon} Analyse #{i}: {analysis['question'][:100]}\n\n"""
            md += f"- **Date:** {analysis['timestamp']}\n"
            md += f"- **Temps d'exécution:** {analysis['execution_time']:.2f}s\n"
            md += f"- **Statut:** {'Réussie' if analysis['success'] else 'Échouée'}\n\n"
            
            md += f"""#### 💡 Insight\n\n{analysis['insight']}\n\n"""
            
            if analysis['recommendations']:
                md += f"""#### 🎯 Recommandations\n\n"""
                for rec in analysis['recommendations']:
                    md += f"- {rec}\n"
                md += "\n"
            
            md += "---\n\n"
        
        md += f"""---\n\n*Rapport généré par InsightBot AI - https://github.com/your-repo/insightbot*\n"""
        
        return md
    
    def export_configuration(self):
        """Export de la configuration"""
        st.markdown("##### ⚙️ Export de la Configuration")
        
        config = {
            "general": {
                "theme_mode": st.session_state.theme_mode,
                "animation_enabled": st.session_state.animation_enabled,
                "auto_refresh": st.session_state.auto_refresh
            },
            "ai": {
                "provider_preference": st.session_state.ai_provider_preference,
                "response_language": st.session_state.response_language
            },
            "exported_at": datetime.now().isoformat()
        }
        
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Télécharger la configuration",
            data=config_json,
            file_name=f"insightbot_config_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            width='stretch'
        )
        
        st.info("💡 La configuration peut être importée ultérieurement pour restaurer les paramètres.")
    
    def export_history(self):
        """Export de l'historique"""
        st.markdown("##### 🗃️ Export de l'Historique")
        
        history = st.session_state.get("chat_history", [])
        
        if not history:
            st.warning("⚠️ Aucun historique à exporter")
            return
        
        # Options d'export
        history_format = st.radio(
            "Format",
            options=["JSON", "CSV"],
            horizontal=True,
            key="history_export_format"
        )
        
        if st.button("📥 Exporter l'historique", width='stretch'):
            with st.spinner("Préparation de l'export..."):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if history_format == "JSON":
                    history_data = json.dumps(history, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="📥 Télécharger JSON",
                        data=history_data,
                        file_name=f"insightbot_history_{timestamp}.json",
                        mime="application/json",
                        width='stretch'
                    )
                
                elif history_format == "CSV":
                    # Convertir l'historique en DataFrame
                    history_list = []
                    for entry in history:
                        result = entry["result"]
                        history_list.append({
                            "timestamp": entry["timestamp"],
                            "question": entry["question"],
                            "success": result.get("success", False),
                            "execution_time": result.get("execution", {}).get("time", 0),
                            "provider": result.get("execution", {}).get("provider", ""),
                            "insight_preview": (result.get("insight", "")[:100] + "...") if result.get("insight") else ""
                        })
                    
                    df = pd.DataFrame(history_list)
                    csv_data = df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv_data,
                        file_name=f"insightbot_history_{timestamp}.csv",
                        mime="text/csv",
                        width='stretch'
                    )
                
                st.success("✅ Historique prêt pour l'export")
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def update_system_status(self):
        """Met à jour l'état du système"""
        try:
            if self.bot:
                cached_metrics = self.get_cached_metrics(self.bot)
                
                if cached_metrics:
                    st.session_state["cached_metrics"] = cached_metrics
                    st.session_state["last_update"] = datetime.now()
                    
                    # Mettre à jour l'état du schéma
                    system_info = self.bot.get_system_info()
                    st.session_state["sql_schema_discovered"] = system_info["database"]["available"]
                    st.session_state["available_sql_columns"] = self.bot.get_sql_columns()
                    
        except Exception as e:
            app_logger.warning(f"⚠️ Erreur mise à jour statut: {e}")
    
    def add_to_chat_history(self, question: str, result: dict):
        """Ajoute une conversation à l'historique"""
        chat_entry = {
            "id": hashlib.md5(f"{question}{datetime.now()}".encode()).hexdigest()[:8],
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "result": result
        }
        
        st.session_state["chat_history"].insert(0, chat_entry)
        
        # Limiter l'historique à 100 entrées
        if len(st.session_state["chat_history"]) > 100:
            st.session_state["chat_history"] = st.session_state["chat_history"][:100]
    
    def save_to_favorites(self, question: str):
        """Ajoute une question aux favoris"""
        favorite = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "id": hashlib.md5(question.encode()).hexdigest()[:8]
        }
        
        # Vérifier si déjà dans les favoris
        existing_ids = [f["id"] for f in st.session_state.get("favorite_queries", [])]
        if favorite["id"] not in existing_ids:
            st.session_state["favorite_queries"].append(favorite)
            
            # Limiter à 50 favoris
            if len(st.session_state["favorite_queries"]) > 50:
                st.session_state["favorite_queries"] = st.session_state["favorite_queries"][:50]
    
    def display_footer(self):
        """Affiche le footer de l'application"""
        st.markdown("---")
        
        footer_cols = st.columns([2, 1, 1])
        
        with footer_cols[0]:
            st.markdown("""
                **🤖 InsightBot AI**  
                v2.0 • Assistant Analytique Intelligent  
                [Documentation](https://github.com/your-repo/insightbot) • [Support](mailto:support@insightbot.ai)
            """)
        
        with footer_cols[1]:
            # Statut des connexions
            sql_status = "✅" if st.session_state.get("sql_schema_discovered") else "❌"
            metrics = st.session_state.get("cached_metrics", {})
            ai_status = metrics.get("ai_status", {})
            ai_provider = ai_status.get("active_provider", "Local")
            
            st.markdown(f"""
                **🔗 Connexions**  
                SQL: {sql_status} • IA: {ai_provider}
            """)
        
        with footer_cols[2]:
            # Statistiques
            history_count = len(st.session_state.get("chat_history", []))
            favorites_count = len(st.session_state.get("favorite_queries", []))
            
            st.markdown(f"""
                **📊 Statistiques**  
                Analyses: {history_count}  
                Favoris: {favorites_count}
            """)
    
    def display_error_state(self):
        """Affiche l'état d'erreur"""
        st.error("""
            ## ⚠️ Impossible de démarrer l'application
            
            **Problèmes possibles :**
            1. Base de données non accessible
            2. Fichiers de données manquants
            3. Connexion réseau interrompue
            4. Problème d'import des modules
            
            **Solutions :**
            - Vérifiez que la base de données existe dans `data/database/`
            - Assurez-vous que les fichiers CSV sont dans `data/processed/`
            - Redémarrez l'application
            - Consultez les logs pour plus d'informations
        """)
        
        # Boutons de récupération
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Réessayer", width='stretch'):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
        
        with col2:
            if st.button("📋 Voir les logs", width='stretch'):
                try:
                    log_path = Path(__file__).parent.parent.parent / "logs" / "insightbot.log"
                    if log_path.exists():
                        with open(log_path, 'r') as f:
                            logs = f.read()[-5000:]  # Derniers 5000 caractères
                        st.code(logs, language="text")
                    else:
                        st.warning("Fichier de logs non trouvé")
                except:
                    st.error("Impossible de lire les logs")
        
        # Instructions de débogage
        with st.expander("🔧 Instructions de débogage avancé"):
            st.markdown("""
            ### Pour les développeurs :
            
            **1. Vérifier les imports :**
            ```bash
            python -c "from core.insightbot_gpt import InsightBotGPT; print('Import OK')"
            ```
            
            **2. Tester la base de données :**
            ```bash
            python scripts/test_database.py
            ```
            
            **3. Vérifier la structure des dossiers :**
            ```bash
            tree data/ -L 3
            ```
            
            **4. Lancer en mode debug :**
            ```bash
            DEBUG=true streamlit run src/app/chat_ultimate_app.py
            ```
            """)

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale de l'application"""
    try:
        # Initialiser et lancer l'application
        app = ChatUltimateApp()
        app.run()
        
    except Exception as e:
        # Gestion d'erreur globale
        st.error(f"""
        ## ❌ Erreur Critique
        
        Une erreur inattendue est survenue :
        ```
        {str(e)}
        ```
        
        **Veuillez :**
        1. Redémarrer l'application
        2. Vérifier les fichiers de configuration
        3. Consulter la documentation
        
        Si le problème persiste, contactez le support technique.
        """)
        
        # Afficher la trace complète en mode debug
        if os.getenv("DEBUG", "False").lower() == "true":
            st.code(traceback.format_exc(), language="text")

if __name__ == "__main__":
    main()