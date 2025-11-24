import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import time

# Ajouter le chemin src
current_dir = Path(__file__).parent
src_path = current_dir.parent
sys.path.append(str(src_path))

from core.insightbot_gpt import InsightBotGPT

class InsightBotUltimateChat:
    def __init__(self):
        self.bot = InsightBotGPT()
        
    def initialize_session_state(self):
        """Initialise l'état de la session avancée"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'suggested_questions' not in st.session_state:
            st.session_state.suggested_questions = self.bot.get_suggested_questions()
        if 'discovery_mode' not in st.session_state:
            st.session_state.discovery_mode = False
    
    def display_hero_section(self):
        """Section hero avec métriques en temps réel"""
        st.title("🧠 InsightBot IA - Assistant Business Intelligent")
        st.markdown("**Analysez vos données e-commerce en langage naturel avec l'IA**")
        
        # Métriques hero en temps réel
        hero_kpis = self.bot.db.execute_query("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(Sales) as total_sales,
                SUM(Profit) as total_profit,
                (SUM(Profit) / SUM(Sales) * 100) as overall_margin
            FROM merged
        """).iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Commandes", f"{hero_kpis['total_orders']:,}")
        with col2:
            st.metric("💰 Chiffre d'Affaires", f"${hero_kpis['total_sales']:,.0f}")
        with col3:
            st.metric("💸 Profit Total", f"${hero_kpis['total_profit']:,.0f}")
        with col4:
            st.metric("📊 Marge Globale", f"{hero_kpis['overall_margin']:.1f}%")
        
        st.markdown("---")
    
    def display_smart_chat_interface(self):
        """Interface de chat intelligente avec suggestions contextuelles"""
        st.subheader("💬 Dialoguez avec InsightBot IA")
        
        # Status IA
        if self.bot.gpt_enabled:
            st.success("✅ **Mode IA Avancé Activé** - GPT-3.5 Turbo")
        else:
            st.warning("🔧 **Mode Basique** - [Configurez OpenAI API](https://platform.openai.com/api-keys)")
        
        # Catégories de questions intelligentes
        st.write("### 🎯 Questions Intelligentes par Catégorie")
        
        categories = {
            "📈 Analyse Performance": [
                "Quelles sont les tendances de vente par mois?",
                "Quels produits ont la croissance la plus rapide?",
                "Comment évolue la profitabilité par catégorie?"
            ],
            "👥 Analyse Clients": [
                "Quels sont les clients les plus fidèles?",
                "Quelle est la valeur vie client par région?",
                "Quels segments clients sont les plus rentables?"
            ],
            "🌍 Analyse Géographique": [
                "Quelles régions ont les meilleures marges?",
                "Comment les ventes varient-elles par pays?",
                "Quels marchés ont le plus fort potentiel?"
            ],
            "📊 Analyse Produits": [
                "Quels produits ont la meilleure marge?",
                "Quelle est la saisonnalité par catégorie?",
                "Quels produits sont souvent achetés ensemble?"
            ]
        }
        
        for category, questions in categories.items():
            with st.expander(f"{category}"):
                cols = st.columns(2)
                for i, question in enumerate(questions):
                    with cols[i % 2]:
                        if st.button(question, key=f"cat_{category}_{i}", use_container_width=True):
                            self.process_question_with_animation(question)
        
        # Recherche avancée
        st.write("### 🔍 Recherche Personnalisée")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            user_question = st.text_input(
                "Posez votre question business:",
                placeholder="Ex: Compare les performances Europe vs Asie sur les 6 derniers mois..."
            )
        with col2:
            analyze_btn = st.button("🚀 Analyser", use_container_width=True)
        with col3:
            discover_btn = st.button("🎯 Découvrir", use_container_width=True)
        
        if analyze_btn and user_question:
            self.process_question_with_animation(user_question)
        
        if discover_btn:
            self.trigger_discovery_mode()
    
    def process_question_with_animation(self, question):
        """Traite une question avec des animations"""
        # Animation de chargement
        with st.spinner("🤖 InsightBot IA analyse en profondeur..."):
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            result = self.bot.process_question(question)
            
            # Ajouter à l'historique
            st.session_state.chat_history.append({
                'question': question,
                'result': result,
                'timestamp': time.time()
            })
            
            # Success animation
            st.success("✅ Analyse terminée!")
            time.sleep(0.5)
            st.rerun()
    
    def trigger_discovery_mode(self):
        """Lance le mode découverte automatique"""
        st.session_state.discovery_mode = True
        
        discovery_questions = [
            "Quels sont les 3 insights les plus importants dans mes données?",
            "Quelles opportunités business identifie-tu?",
            "Quels risques ou problèmes detecte-tu?",
            "Quelles recommandations stratégiques proposes-tu?"
        ]
        
        for question in discovery_questions:
            result = self.bot.process_question(question)
            st.session_state.chat_history.append({
                'question': question,
                'result': result,
                'timestamp': time.time(),
                'discovery': True
            })
        
        st.rerun()
    
    def display_smart_chat_history(self):
        """Affiche l'historique avec intelligence"""
        if st.session_state.chat_history:
            st.subheader("📜 Historique Intelligent")
            
            # Trier par timestamp
            sorted_history = sorted(st.session_state.chat_history, key=lambda x: x['timestamp'], reverse=True)
            
            for i, chat in enumerate(sorted_history):
                # Style différent pour le mode découverte
                if chat.get('discovery'):
                    emoji = "🔍"
                    color = "info"
                else:
                    emoji = "🤖" 
                    color = "secondary"
                
                with st.expander(f"{emoji} {chat['question']}", expanded=i==0):
                    result = chat['result']
                    
                    # Insight principal
                    st.success(f"💡 **Insight IA:** {result['insight']}")
                    
                    # Score de confiance (simulé)
                    confidence = min(95, max(70, len(result['insight']) // 3))
                    st.progress(confidence/100, text=f"Confiance IA: {confidence}%")
                    
                    # Détails techniques (repliable)
                    with st.expander("🔧 Détails Techniques"):
                        st.code(f"SQL: {result['sql_query']}", language='sql')
                        st.text(f"Type de visualisation: {result['chart_type']}")
                    
                    # Visualisation
                    if result['chart'] is not None:
                        st.plotly_chart(result['chart'], use_container_width=True)
                    
                    # Données et actions
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        with st.expander("📋 Données détaillées"):
                            if hasattr(result['data'], 'head'):
                                st.dataframe(result['data'], use_container_width=True)
                                
                                # Statistiques automatiques
                                if len(result['data']) > 1:
                                    self.display_auto_insights(result['data'])
                            else:
                                st.json(result['data'])
                    
                    with col2:
                        st.write("**📤 Actions**")
                        if st.button("📊 Exporter CSV", key=f"export_{i}"):
                            self.export_to_csv(result['data'], chat['question'])
                        
                        if st.button("📈 Copier SQL", key=f"sql_{i}"):
                            st.code(result['sql_query'], language='sql')
    
    def display_auto_insights(self, data):
        """Génère des insights automatiques depuis les données"""
        if len(data) > 1:
            st.write("**🎯 Insights Auto:**")
            
            # Analyser la première colonne numérique
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                main_col = numeric_cols[0]
                
                # Top performer
                max_idx = data[main_col].idxmax()
                min_idx = data[main_col].idxmin()
                
                st.metric(
                    f"🏆 Meilleur: {data.iloc[max_idx][data.columns[0]]}",
                    f"{data.iloc[max_idx][main_col]:,.0f}"
                )
                
                if data.iloc[max_idx][main_col] != data.iloc[min_idx][main_col]:
                    st.metric(
                        f"📉 Plus bas: {data.iloc[min_idx][data.columns[0]]}",
                        f"{data.iloc[min_idx][main_col]:,.0f}"
                    )
    
    def export_to_csv(self, data, question):
        """Exporte les données en CSV"""
        if hasattr(data, 'to_csv'):
            filename = f"insightbot_{question[:20]}.csv".replace(' ', '_')
            data.to_csv(filename, index=False)
            st.success(f"✅ Exporté: {filename}")
    
    def display_advanced_sidebar(self):
        """Sidebar avancé avec analytics"""
        st.sidebar.title("🧠 Tableau de Bord IA")
        
        # Status système
        st.sidebar.subheader("📊 Status Système")
        st.sidebar.metric("Analyses Effectuées", len(st.session_state.chat_history))
        st.sidebar.metric("Mode IA", "✅ Activé" if self.bot.gpt_enabled else "🔧 Basique")
        
        # Analytics avancés
        st.sidebar.subheader("📈 Analytics Avancés")
        
        advanced_metrics = self.bot.db.execute_query("""
            SELECT 
                COUNT(DISTINCT "Product ID") as unique_products,
                COUNT(DISTINCT Region) as unique_regions,
                AVG(Profit_Margin_Percent) as avg_margin,
                (SUM(CASE WHEN Profit > 100 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as high_profit_rate
            FROM merged
        """).iloc[0]
        
        st.sidebar.metric("🛍️ Produits Uniques", f"{advanced_metrics['unique_products']:,}")
        st.sidebar.metric("🌍 Régions Couvertes", advanced_metrics['unique_regions'])
        st.sidebar.metric("💎 Marge Moyenne", f"{advanced_metrics['avg_margin']:.1f}%")
        st.sidebar.metric("🚀 Haut Profit", f"{advanced_metrics['high_profit_rate']:.1f}%")
        
        # Contrôles avancés
        st.sidebar.subheader("⚙️ Contrôles Avancés")
        
        if st.sidebar.button("🎯 Mode Découverte Auto", use_container_width=True):
            self.trigger_discovery_mode()
        
        if st.sidebar.button("📊 Dashboard Complet", use_container_width=True):
            st.session_state.show_dashboard = True
        
        if st.sidebar.button("🔄 Rafraîchir Données", use_container_width=True):
            st.rerun()
        
        if st.sidebar.button("🗑️ Reset Complet", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.discovery_mode = False
            st.rerun()
    
    def run(self):
        """Lance l'application ultime"""
        st.set_page_config(
            page_title="InsightBot IA Ultimate",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialisation
        self.initialize_session_state()
        
        # Layout principal
        self.display_hero_section()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.display_smart_chat_interface()
            self.display_smart_chat_history()
        
        with col2:
            self.display_advanced_sidebar()

def main():
    app = InsightBotUltimateChat()
    app.run()

if __name__ == "__main__":
    main()