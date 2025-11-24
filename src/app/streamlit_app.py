import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

# Ajouter le chemin src au PYTHONPATH
current_dir = Path(__file__).parent
src_path = current_dir.parent
sys.path.append(str(src_path))

from core.database_manager import DatabaseManager

class InsightBotApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
    
    def display_kpi_cards(self):
        """Affiche les cartes KPI"""
        st.subheader("📊 Tableau de Bord Global")
        
        # KPIs depuis la base
        kpi_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(Sales) as total_sales,
                SUM(Profit) as total_profit,
                AVG(Profit_Margin_Percent) as avg_margin,
                SUM(Is_Returned) as total_returns,
                COUNT(DISTINCT "Customer ID") as unique_customers
            FROM merged
        """
        
        kpis = self.db.execute_query(kpi_query).iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Commandes Total", f"{kpis['total_orders']:,}")
            st.metric("Clients Uniques", f"{kpis['unique_customers']:,}")
        
        with col2:
            st.metric("Chiffre d'Affaires", f"${kpis['total_sales']:,.0f}")
            st.metric("Marge Moyenne", f"{kpis['avg_margin']:.1f}%")
        
        with col3:
            st.metric("Profit Total", f"${kpis['total_profit']:,.0f}")
            return_rate = (kpis['total_returns'] / kpis['total_orders']) * 100
            st.metric("Taux Retour", f"{return_rate:.1f}%")
        
        with col4:
            # Commandes profitables
            profit_query = """
                SELECT 
                    SUM(CASE WHEN Profit > 0 THEN 1 ELSE 0 END) as profitable_orders,
                    COUNT(*) as total_orders
                FROM merged
            """
            profit_data = self.db.execute_query(profit_query).iloc[0]
            profitable_rate = (profit_data['profitable_orders'] / profit_data['total_orders']) * 100
            st.metric("Commandes Rentables", f"{profitable_rate:.1f}%")
            st.metric("Commandes Retournées", f"{kpis['total_returns']:,}")
    
    def display_sales_analysis(self):
        """Analyse des ventes"""
        st.subheader("📈 Analyse des Ventes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventes par région
            query = """
                SELECT Region, SUM(Sales) as total_sales
                FROM merged 
                GROUP BY Region 
                ORDER BY total_sales DESC
                LIMIT 10
            """
            data = self.db.execute_query(query)
            
            fig = px.bar(
                data,
                x='total_sales',
                y='Region',
                orientation='h',
                title="Top 10 Régions par Ventes",
                color='total_sales'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ventes par catégorie
            query = """
                SELECT Category, SUM(Sales) as total_sales
                FROM merged 
                GROUP BY Category 
                ORDER BY total_sales DESC
            """
            data = self.db.execute_query(query)
            
            fig = px.pie(
                data,
                values='total_sales',
                names='Category',
                title="Répartition des Ventes par Catégorie"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_profit_analysis(self):
        """Analyse de profitabilité"""
        st.subheader("💰 Analyse de Profitabilité")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Profit par catégorie
            query = """
                SELECT Category, SUM(Profit) as total_profit
                FROM merged 
                GROUP BY Category 
                ORDER BY total_profit DESC
            """
            data = self.db.execute_query(query)
            
            fig = px.bar(
                data,
                x='Category',
                y='total_profit',
                title="Profit par Catégorie",
                color='total_profit'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Commandes profitables vs non profitables
            query = """
                SELECT 
                    CASE 
                        WHEN Profit > 0 THEN 'Profitable' 
                        ELSE 'Non-Profitable' 
                    END as profitability,
                    COUNT(*) as count
                FROM merged 
                GROUP BY profitability
            """
            data = self.db.execute_query(query)
            
            fig = px.pie(
                data,
                values='count',
                names='profitability',
                title="Répartition Profitabilité des Commandes"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_temporal_analysis(self):
        """Analyse temporelle"""
        st.subheader("📅 Analyse Temporelle")
        
        # Évolution mensuelle
        query = """
            SELECT 
                Order_YearMonth,
                SUM(Sales) as monthly_sales,
                SUM(Profit) as monthly_profit
            FROM merged 
            GROUP BY Order_YearMonth
            ORDER BY Order_YearMonth
        """
        data = self.db.execute_query(query)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['Order_YearMonth'].astype(str), 
            y=data['monthly_sales'],
            mode='lines+markers',
            name='Ventes Mensuelles',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=data['Order_YearMonth'].astype(str), 
            y=data['monthly_profit'],
            mode='lines+markers',
            name='Profit Mensuel',
            line=dict(color='green')
        ))
        fig.update_layout(
            title="Évolution des Ventes et Profit Mensuels",
            xaxis_title="Mois",
            yaxis_title="Montant ($)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def display_returns_analysis(self):
        """Analyse des retours"""
        st.subheader("🔙 Analyse des Retours")
        
        query = """
            SELECT 
                Market,
                COUNT(*) as total_orders,
                SUM(Is_Returned) as returned_orders,
                (SUM(Is_Returned) * 100.0 / COUNT(*)) as return_rate
            FROM merged
            GROUP BY Market
            ORDER BY return_rate DESC
        """
        data = self.db.execute_query(query)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                data,
                x='Market',
                y='return_rate',
                title="Taux de Retour par Marché (%)",
                color='return_rate'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                data,
                values='returned_orders',
                names='Market',
                title="Répartition des Retours par Marché"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """Lance l'application Streamlit"""
        st.set_page_config(
            page_title="InsightBot - Analyse E-commerce",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 InsightBot - Assistant d'Analyse E-commerce")
        st.markdown("**Global Superstore 2016 - Données Nettoyées et Optimisées**")
        st.markdown("---")
        
        # Tableau de bord
        self.display_kpi_cards()
        
        # Analyses
        self.display_sales_analysis()
        self.display_profit_analysis()
        self.display_temporal_analysis()
        self.display_returns_analysis()
        
        # Données brutes
        with st.expander("📋 Explorer les Données Brutes"):
            col1, col2 = st.columns(2)
            with col1:
                limit = st.slider("Nombre de lignes", 10, 1000, 100)
            with col2:
                table = st.selectbox("Table", ["merged", "orders", "returns", "peoples"])
            
            data = self.db.execute_query(f"SELECT * FROM {table} LIMIT {limit}")
            st.dataframe(data, use_container_width=True)
            
            # Téléchargement
            csv = data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=csv,
                file_name=f"{table}_data.csv",
                mime="text/csv"
            )

def main():
    app = InsightBotApp()
    app.run()

if __name__ == "__main__":
    main()