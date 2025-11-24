import openai
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database_manager import DatabaseManager
import re
import json

# Charger les variables d'environnement
load_dotenv()

class InsightBotGPT:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        
        # Configuration OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.gpt_enabled = True
            print("✅ GPT intégré à InsightBot")
        else:
            self.gpt_enabled = False
            print("⚠️  GPT non configuré - Mode basique")
    
    def get_schema_info(self):
        """Récupère les informations du schéma de la base"""
        tables_info = {}
        
        # Informations sur les tables et colonnes
        tables = ['merged', 'orders', 'returns', 'peoples']
        for table in tables:
            columns = self.db.get_table_info(table)
            tables_info[table] = [f"{col[0]} ({col[1]})" for col in columns]
        
        return tables_info
    
    def generate_sql_with_gpt(self, question):
        """Utilise GPT pour générer du SQL à partir d'une question naturelle"""
        if not self.gpt_enabled:
            return self._fallback_sql_generation(question)
        
        schema_info = self.get_schema_info()
        
        prompt = f"""
        Tu es un expert SQL. Convertis cette question en SQL pour DuckDB.
        
        SCHEMA DE LA BASE:
        Table 'merged' (principale) - {len(schema_info['merged'])} colonnes:
        {', '.join(schema_info['merged'][:15])}...
        
        Tables disponibles: merged, orders, returns, peoples
        
        QUESTION: "{question}"
        
        RÈGLES:
        - Utilise la table 'merged' comme principale
        - Les noms de colonnes avec espaces doivent être entre guillemets
        - Retourne UNIQUEMENT le code SQL, sans explications
        - Sois précis dans les aggregations (SUM, COUNT, AVG)
        - Ordonne les résultats quand c'est pertinent
        - Limite à 10-20 résultats si nécessaire
        
        SQL:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert SQL qui convertit des questions en requêtes précises."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            print(f"🤖 GPT a généré: {sql_query}")
            return sql_query
            
        except Exception as e:
            print(f"❌ Erreur GPT: {e}")
            return self._fallback_sql_generation(question)
    
    def _fallback_sql_generation(self, question):
        """Génération de SQL basique si GPT n'est pas disponible"""
        question_lower = question.lower()
        
        sql_templates = {
            r'vente.*région': "SELECT Region, SUM(Sales) as total_sales FROM merged GROUP BY Region ORDER BY total_sales DESC LIMIT 10",
            r'profit.*catégorie': "SELECT Category, SUM(Profit) as total_profit FROM merged GROUP BY Category ORDER BY total_profit DESC",
            r'évolution.*vente': "SELECT Order_YearMonth, SUM(Sales) as monthly_sales FROM merged GROUP BY Order_YearMonth ORDER BY Order_YearMonth",
            r'taux.*retour': "SELECT Market, COUNT(*) as total_orders, SUM(Is_Returned) as returned_orders, (SUM(Is_Returned)*100.0/COUNT(*)) as return_rate FROM merged GROUP BY Market ORDER BY return_rate DESC",
            r'top.*produit': 'SELECT "Product Name", SUM(Profit) as total_profit FROM merged GROUP BY "Product Name" ORDER BY total_profit DESC LIMIT 5',
            r'chiffre.*affaire': "SELECT SUM(Sales) as total_sales FROM merged",
            r'client.*fidèle': 'SELECT "Customer Name", COUNT(*) as order_count FROM merged GROUP BY "Customer Name" ORDER BY order_count DESC LIMIT 5',
            r'marge.*moyenne': "SELECT AVG(Profit_Margin_Percent) as avg_margin FROM merged",
            r'segment.*client': "SELECT Segment, SUM(Sales) as total_sales FROM merged GROUP BY Segment ORDER BY total_sales DESC"
        }
        
        for pattern, sql in sql_templates.items():
            if re.search(pattern, question_lower):
                return sql
        
        # Requête par défaut
        return "SELECT COUNT(*) as total_orders, SUM(Sales) as total_sales, SUM(Profit) as total_profit FROM merged"
    
    def generate_insight_with_gpt(self, question, data, sql_query):
        """Utilise GPT pour générer des insights à partir des données"""
        if not self.gpt_enabled:
            return self._fallback_insight_generation(data, sql_query)
        
        # Préparer un échantillon des données pour GPT
        data_sample = data.head(10).to_string() if hasattr(data, 'head') else str(data)
        
        prompt = f"""
        Tu es un analyste business expert. Analyse ces données et génère un insight concis et actionnable.
        
        QUESTION: "{question}"
        REQUÊTE SQL: {sql_query}
        DONNÉES (échantillon):
        {data_sample}
        
        Formule un insight business en 1-2 phrases qui:
        1. Souligne le point le plus important
        2. Donne un contexte business
        3. Suggère une action si pertinent
        
        Réponds en français, sois concis et professionnel.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un analyste business qui génère des insights actionnables à partir de données."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            insight = response.choices[0].message.content.strip()
            return insight
            
        except Exception as e:
            print(f"❌ Erreur GPT insight: {e}")
            return self._fallback_insight_generation(data, sql_query)
    
    def _fallback_insight_generation(self, data, sql_query):
        """Génération d'insight basique"""
        if hasattr(data, 'shape') and data.shape[0] > 0:
            if 'total_sales' in data.columns and len(data) == 1:
                return f"Chiffre d'affaires total: ${data.iloc[0]['total_sales']:,.2f}"
            elif 'total_profit' in data.columns and len(data) == 1:
                return f"Profit total: ${data.iloc[0]['total_profit']:,.2f}"
            elif 'Region' in data.columns:
                top_region = data.iloc[0]['Region']
                top_sales = data.iloc[0]['total_sales']
                return f"La région {top_region} domine avec ${top_sales:,.2f} de ventes"
        
        return f"Analyse terminée: {len(data) if hasattr(data, '__len__') else 1} résultat(s) trouvé(s)"
    
    def suggest_chart_type(self, question, data):
        """Suggère le type de graphique avec GPT"""
        if not self.gpt_enabled:
            return self._fallback_chart_suggestion(question, data)
        
        data_info = f"Colonnes: {list(data.columns) if hasattr(data, 'columns') else 'Single value'}"
        
        prompt = f"""
        QUESTION: "{question}"
        DONNÉES: {data_info}
        
        Quel type de visualisation recommandes-tu?
        Options: bar, line, pie, scatter, histogram, none
        
        Réponds avec UN SEUL MOT: le type de graphique.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            chart_type = response.choices[0].message.content.strip().lower()
            return chart_type if chart_type in ['bar', 'line', 'pie', 'scatter', 'histogram'] else 'bar'
            
        except Exception as e:
            print(f"❌ Erreur GPT chart: {e}")
            return self._fallback_chart_suggestion(question, data)
    
    def _fallback_chart_suggestion(self, question, data):
        """Suggestion basique de graphique"""
        question_lower = question.lower()
        
        if 'évolution' in question_lower or 'temps' in question_lower:
            return 'line'
        elif 'région' in question_lower or 'catégorie' in question_lower:
            return 'bar'
        elif 'pourcentage' in question_lower or 'répartition' in question_lower:
            return 'pie'
        else:
            return 'bar'
    
    def create_chart(self, data, chart_type, title):
        """Crée un graphique basé sur le type suggéré"""
        if chart_type == 'none' or data.empty:
            return None
        
        try:
            if chart_type == 'bar' and len(data) > 1:
                if 'total_sales' in data.columns:
                    return px.bar(data, x=data.columns[1], y=data.columns[0], title=title)
                else:
                    return px.bar(data, x=data.iloc[:, 0], y=data.iloc[:, 1], title=title)
            
            elif chart_type == 'line' and len(data) > 1:
                return px.line(data, x=data.columns[0], y=data.columns[1], title=title)
            
            elif chart_type == 'pie' and len(data) > 1:
                return px.pie(data, names=data.columns[0], values=data.columns[1], title=title)
            
        except Exception as e:
            print(f"❌ Erreur création graphique: {e}")
        
        return None
    
    def process_question(self, question):
        """Traite une question avec l'IA avancée"""
        print(f"🤖 Traitement de: {question}")
        
        # 1. Générer la requête SQL avec GPT
        sql_query = self.generate_sql_with_gpt(question)
        
        # 2. Exécuter la requête
        data = self.db.execute_query(sql_query)
        
        if data is None or data.empty:
            return {
                'question': question,
                'data': None,
                'insight': "❌ Aucune donnée trouvée pour cette question.",
                'chart': None,
                'sql_query': sql_query,
                'chart_type': 'none'
            }
        
        # 3. Générer l'insight avec GPT
        insight = self.generate_insight_with_gpt(question, data, sql_query)
        
        # 4. Suggérer le type de graphique
        chart_type = self.suggest_chart_type(question, data)
        
        # 5. Créer le graphique
        chart = self.create_chart(data, chart_type, f"Résultat: {question}")
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': chart,
            'sql_query': sql_query,
            'chart_type': chart_type
        }
    
    def get_suggested_questions(self):
        """Retourne des questions suggérées avancées"""
        return [
            "Quelles régions ont la croissance la plus forte?",
            "Quels produits ont la meilleure marge?",
            "Comment le taux de retour évolue-t-il dans le temps?",
            "Quels sont les clients les plus fidèles?",
            "Quelle est la saisonnalité des ventes?",
            "Quels segments clients sont les plus rentables?",
            "Comment les remises impactent-elles le profit?",
            "Quelle est la performance par canal de livraison?"
        ]

def main():
    # Test de l'IA avancée
    bot = InsightBotGPT()
    
    test_questions = [
        "Quelles sont les ventes par région?",
        "Quel est le profit par catégorie?",
        "Comment évoluent les ventes dans le temps?",
        "Quels sont les clients les plus fidèles?"
    ]
    
    for question in test_questions:
        print(f"\n🎯 Question: {question}")
        result = bot.process_question(question)
        print(f"💡 Insight: {result['insight']}")
        print(f"📊 SQL: {result['sql_query']}")
        print(f"📈 Chart type: {result['chart_type']}")

if __name__ == "__main__":
    main()