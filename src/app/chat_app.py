import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Ajouter le chemin src
current_dir = Path(__file__).parent
src_path = current_dir.parent
sys.path.append(str(src_path))

from core.insightbot_ai import InsightBotAI

class InsightBotChat:
    def __init__(self):
        self.bot = InsightBotAI()
        
    def initialize_session_state(self):
        """Initialise l'état de la session"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'suggested_questions' not in st.session_state:
            st.session_state.suggested_questions = self.bot.get_suggested_questions()
    
    def display_chat_interface(self):
        """Affiche l'interface de chat"""
        st.subheader("💬 Posez une question à InsightBot")
        
        # Questions suggérées
        st.write("**Questions suggérées:**")
        cols = st.columns(2)
        for i, question in enumerate(st.session_state.suggested_questions):
            with cols[i % 2]:
                if st.button(question, key=f"suggest_{i}"):
                    self.process_question(question)
        
        # Input utilisateur
        user_question = st.text_input(
            "Ou tapez votre propre question:",
            placeholder="Ex: Montre-moi les ventes par région..."
        )
        
        if user_question and user_question not in [msg['question'] for msg in st.session_state.chat_history]:
            self.process_question(user_question)
    
    def process_question(self, question):
        """Traite une question et met à jour l'historique"""
        with st.spinner("🤖 InsightBot analyse..."):
            result = self.bot.process_question(question)
            
            # Ajouter à l'historique
            st.session_state.chat_history.append({
                'question': question,
                'result': result
            })
    
    def display_chat_history(self):
        """Affiche l'historique des conversations"""
        if st.session_state.chat_history:
            st.subheader("📜 Historique des Analyses")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"Q: {chat['question']}", expanded=i==0):
                    result = chat['result']
                    
                    # Afficher l'insight
                    st.success(f"💡 {result['insight']}")
                    
                    # Afficher le graphique
                    if result['chart'] is not None:
                        st.plotly_chart(result['chart'], use_container_width=True)
                    
                    # Afficher les données
                    with st.expander("📊 Voir les données détaillées"):
                        if hasattr(result['data'], 'head'):
                            st.dataframe(result['data'], use_container_width=True)
                        else:
                            st.json(result['data'])
    
    def display_kpi_overview(self):
        """Affiche un aperçu des KPIs"""
        st.sidebar.subheader("📊 Aperçu Global")
        
        # KPIs rapides
        kpi_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(Sales) as total_sales,
                SUM(Profit) as total_profit,
                AVG(Profit_Margin_Percent) as avg_margin
            FROM merged
        """
        kpis = self.bot.db.execute_query(kpi_query).iloc[0]
        
        st.sidebar.metric("Commandes", f"{kpis['total_orders']:,}")
        st.sidebar.metric("Chiffre d'Affaires", f"${kpis['total_sales']:,.0f}")
        st.sidebar.metric("Profit Total", f"${kpis['total_profit']:,.0f}")
        st.sidebar.metric("Marge Moyenne", f"{kpis['avg_margin']:.1f}%")
    
    def run(self):
        """Lance l'application de chat"""
        st.set_page_config(
            page_title="InsightBot Chat",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 InsightBot - Assistant Conversationnel")
        st.markdown("Posez des questions en langage naturel sur vos données e-commerce")
        st.markdown("---")
        
        # Initialisation
        self.initialize_session_state()
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.display_chat_interface()
            self.display_chat_history()
        
        with col2:
            self.display_kpi_overview()
            
            # Options
            st.sidebar.subheader("⚙️ Options")
            if st.sidebar.button("🗑️ Effacer l'historique"):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.sidebar.button("🔄 Actualiser les données"):
                st.rerun()

def main():
    app = InsightBotChat()
    app.run()

if __name__ == "__main__":
    main()