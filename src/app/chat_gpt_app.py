import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Ajouter le chemin src
current_dir = Path(__file__).parent
src_path = current_dir.parent
sys.path.append(str(src_path))

from core.insightbot_gpt import InsightBotGPT

class InsightBotGPTChat:
    def __init__(self):
        self.bot = InsightBotGPT()
        
    def initialize_session_state(self):
        """Initialise l'état de la session"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'suggested_questions' not in st.session_state:
            st.session_state.suggested_questions = self.bot.get_suggested_questions()
    
    def display_chat_interface(self):
        """Affiche l'interface de chat avancée"""
        st.subheader("💬 Chat avec InsightBot IA")
        
        # Status GPT
        if self.bot.gpt_enabled:
            st.success("✅ Mode IA GPT activé")
        else:
            st.warning("⚠️ Mode basique - [Configure OpenAI API Key](https://platform.openai.com/api-keys)")
        
        # Questions suggérées avancées
        st.write("**🚀 Questions IA avancées:**")
        cols = st.columns(2)
        for i, question in enumerate(st.session_state.suggested_questions):
            with cols[i % 2]:
                if st.button(question, key=f"suggest_{i}", use_container_width=True):
                    self.process_question(question)
        
        # Input utilisateur avancé
        col1, col2 = st.columns([3, 1])
        with col1:
            user_question = st.text_input(
                "Posez une question complexe:",
                placeholder="Ex: Quels produits ont la meilleure marge par région?..."
            )
        with col2:
            if st.button("Analyser", use_container_width=True) and user_question:
                self.process_question(user_question)
    
    def process_question(self, question):
        """Traite une question avec l'IA avancée"""
        with st.spinner("🤖 InsightBot IA analyse avec GPT..."):
            result = self.bot.process_question(question)
            
            # Ajouter à l'historique
            st.session_state.chat_history.append({
                'question': question,
                'result': result
            })
            
            # Forcer le rerender
            st.rerun()
    
    def display_chat_history(self):
        """Affiche l'historique des conversations avec détails IA"""
        if st.session_state.chat_history:
            st.subheader("📜 Historique des Analyses IA")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"🤖 {chat['question']}", expanded=i==0):
                    result = chat['result']
                    
                    # Afficher l'insight IA
                    st.success(f"💡 **Insight IA:** {result['insight']}")
                    
                    # Afficher la requête SQL (optionnel)
                    with st.expander("🔍 Voir la requête SQL générée"):
                        st.code(result['sql_query'], language='sql')
                    
                    # Afficher le graphique IA
                    if result['chart'] is not None:
                        st.plotly_chart(result['chart'], use_container_width=True)
                        st.caption(f"📊 Type de visualisation: {result['chart_type']}")
                    
                    # Afficher les données
                    with st.expander("📋 Données détaillées"):
                        if hasattr(result['data'], 'head'):
                            st.dataframe(result['data'], use_container_width=True)
                            
                            # Statistiques rapides
                            if len(result['data']) > 1:
                                st.write("**📈 Statistiques:**")
                                numeric_cols = result['data'].select_dtypes(include=['number']).columns
                                for col in numeric_cols[:3]:  # Premieres 3 colonnes numériques
                                    if col in result['data'].columns:
                                        st.metric(
                                            f"Total {col}",
                                            f"{result['data'][col].sum():,.0f}" if 'total' in col else f"{result['data'][col].mean():.1f}"
                                        )
                        else:
                            st.json(result['data'])
    
    def display_ai_features(self):
        """Affiche les fonctionnalités IA"""
        st.sidebar.subheader("🧠 Fonctionnalités IA")
        
        if self.bot.gpt_enabled:
            st.sidebar.success("✅ GPT-3.5 Turbo")
            st.sidebar.info("• Génération SQL intelligente\n• Insights business\n• Visualisations adaptatives")
        else:
            st.sidebar.warning("🔧 Mode Basique")
            st.sidebar.info("• SQL par motifs\n• Insights simples\n• Graphiques standards")
        
        # KPIs avancés
        st.sidebar.subheader("📊 Métriques Avancées")
        
        advanced_kpis = self.bot.db.execute_query("""
            SELECT 
                COUNT(DISTINCT "Customer ID") as unique_customers,
                AVG(Processing_Days) as avg_processing_days,
                SUM(CASE WHEN Profit > 0 THEN 1 ELSE 0 END) as profitable_orders,
                (SUM(CASE WHEN Is_Returned THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as overall_return_rate
            FROM merged
        """).iloc[0]
        
        st.sidebar.metric("Clients Uniques", f"{advanced_kpis['unique_customers']:,}")
        st.sidebar.metric("Délai Moyen", f"{advanced_kpis['avg_processing_days']:.1f}j")
        st.sidebar.metric("Commandes Rentables", f"{(advanced_kpis['profitable_orders']/51290*100):.1f}%")
        st.sidebar.metric("Taux Retour Global", f"{advanced_kpis['overall_return_rate']:.1f}%")
    
    def run(self):
        """Lance l'application de chat IA"""
        st.set_page_config(
            page_title="InsightBot IA",
            page_icon="🧠",
            layout="wide"
        )
        
        st.title("🧠 InsightBot IA - Assistant Intelligent")
        st.markdown("Posez des questions complexes en langage naturel - **Powered by GPT**")
        st.markdown("---")
        
        # Initialisation
        self.initialize_session_state()
        
        # Layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.display_chat_interface()
            self.display_chat_history()
        
        with col2:
            self.display_ai_features()
            
            # Contrôles avancés
            st.sidebar.subheader("⚙️ Contrôles IA")
            
            if st.sidebar.button("🗑️ Effacer l'historique"):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.sidebar.button("🔄 Recharger les données"):
                st.rerun()
            
            if st.sidebar.button("🎯 Mode Découverte"):
                st.session_state.chat_history.append({
                    'question': "Découverte automatique",
                    'result': self.bot.process_question("Quels sont les insights les plus importants dans mes données?")
                })
                st.rerun()

def main():
    app = InsightBotGPTChat()
    app.run()

if __name__ == "__main__":
    main()