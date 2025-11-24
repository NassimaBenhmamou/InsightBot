import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database_manager import DatabaseManager
import re

class InsightBotAI:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        
        # Mapping des questions types vers les requêtes SQL
        self.question_patterns = {
            r'vente.*région': self._sales_by_region,
            r'profit.*catégorie': self._profit_by_category,
            r'évolution.*vente': self._sales_trend,
            r'taux.*retour': self._return_rates,
            r'top.*produit': self._top_products,
            r'chiffre.*affaire': self._total_sales,
            r'profit.*total': self._total_profit,
            r'marge.*moyenne': self._average_margin,
            r'quantité.*vendu': self._total_quantity
        }
    
    def process_question(self, question):
        """Traite une question en langage naturel"""
        question_lower = question.lower()
        
        # Chercher le pattern correspondant
        for pattern, handler in self.question_patterns.items():
            if re.search(pattern, question_lower):
                return handler(question)
        
        # Si aucun pattern ne correspond, retourner une analyse générale
        return self._general_analysis(question)
    
    def _sales_by_region(self, question):
        """Ventes par région"""
        query = """
            SELECT Region, SUM(Sales) as total_sales
            FROM merged 
            GROUP BY Region 
            ORDER BY total_sales DESC
            LIMIT 10
        """
        data = self.db.execute_query(query)
        
        # Générer un insight
        top_region = data.iloc[0]['Region']
        top_sales = data.iloc[0]['total_sales']
        insight = f"La région {top_region} a les ventes les plus élevées avec ${top_sales:,.2f}"
        
        # Générer un graphique
        fig = px.bar(
            data,
            x='total_sales',
            y='Region',
            orientation='h',
            title="Top 10 Régions par Ventes",
            labels={'total_sales': 'Ventes ($)', 'Region': 'Région'}
        )
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': fig,
            'chart_type': 'bar'
        }
    
    def _profit_by_category(self, question):
        """Profit par catégorie"""
        query = """
            SELECT Category, SUM(Profit) as total_profit
            FROM merged 
            GROUP BY Category 
            ORDER BY total_profit DESC
        """
        data = self.db.execute_query(query)
        
        insight = f"La catégorie {data.iloc[0]['Category']} génère le plus de profit: ${data.iloc[0]['total_profit']:,.2f}"
        
        fig = px.pie(
            data,
            values='total_profit',
            names='Category',
            title="Distribution du Profit par Catégorie"
        )
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': fig,
            'chart_type': 'pie'
        }
    
    def _sales_trend(self, question):
        """Évolution des ventes dans le temps"""
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
        
        # Calculer la croissance
        first_sales = data.iloc[0]['monthly_sales']
        last_sales = data.iloc[-1]['monthly_sales']
        growth = ((last_sales - first_sales) / first_sales) * 100
        
        insight = f"Les ventes ont {'augmenté' if growth > 0 else 'diminué'} de {abs(growth):.1f}% sur la période"
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['Order_YearMonth'].astype(str),
            y=data['monthly_sales'],
            mode='lines+markers',
            name='Ventes Mensuelles'
        ))
        fig.update_layout(
            title="Évolution des Ventes Mensuelles",
            xaxis_title="Mois",
            yaxis_title="Ventes ($)"
        )
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': fig,
            'chart_type': 'line'
        }
    
    def _return_rates(self, question):
        """Taux de retour par marché"""
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
        
        highest_return = data.iloc[0]
        lowest_return = data.iloc[-1]
        
        insight = f"Le marché {highest_return['Market']} a le plus haut taux de retour ({highest_return['return_rate']:.1f}%)"
        
        fig = px.bar(
            data,
            x='Market',
            y='return_rate',
            title="Taux de Retour par Marché",
            labels={'return_rate': 'Taux de Retour (%)', 'Market': 'Marché'}
        )
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': fig,
            'chart_type': 'bar'
        }
    
    def _top_products(self, question):
        """Top produits par profit"""
        query = """
            SELECT 
                "Product Name" as product_name,
                SUM(Sales) as total_sales,
                SUM(Profit) as total_profit,
                AVG(Profit_Margin_Percent) as avg_margin
            FROM merged 
            GROUP BY "Product Name"
            HAVING total_profit > 0
            ORDER BY total_profit DESC
            LIMIT 5
        """
        data = self.db.execute_query(query)
        
        top_product = data.iloc[0]
        insight = f"Le produit le plus rentable est '{top_product['product_name']}' avec ${top_product['total_profit']:,.2f} de profit"
        
        fig = px.bar(
            data,
            x='total_profit',
            y='product_name',
            orientation='h',
            title="Top 5 Produits les Plus Rentables",
            labels={'total_profit': 'Profit Total ($)', 'product_name': 'Produit'}
        )
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': fig,
            'chart_type': 'bar'
        }
    
    def _total_sales(self, question):
        """Chiffre d'affaires total"""
        query = "SELECT SUM(Sales) as total_sales FROM merged"
        data = self.db.execute_query(query).iloc[0]
        
        insight = f"Le chiffre d'affaires total est de ${data['total_sales']:,.2f}"
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': None,
            'chart_type': 'none'
        }
    
    def _total_profit(self, question):
        """Profit total"""
        query = "SELECT SUM(Profit) as total_profit FROM merged"
        data = self.db.execute_query(query).iloc[0]
        
        insight = f"Le profit total est de ${data['total_profit']:,.2f}"
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': None,
            'chart_type': 'none'
        }
    
    def _average_margin(self, question):
        """Marge moyenne"""
        query = "SELECT AVG(Profit_Margin_Percent) as avg_margin FROM merged WHERE Profit_Margin_Percent IS NOT NULL"
        data = self.db.execute_query(query).iloc[0]
        
        insight = f"La marge moyenne est de {data['avg_margin']:.2f}%"
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': None,
            'chart_type': 'none'
        }
    
    def _total_quantity(self, question):
        """Quantité totale vendue"""
        query = "SELECT SUM(Quantity) as total_quantity FROM merged"
        data = self.db.execute_query(query).iloc[0]
        
        insight = f"La quantité totale vendue est de {data['total_quantity']:,} unités"
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': None,
            'chart_type': 'none'
        }
    
    def _general_analysis(self, question):
        """Analyse générale si la question n'est pas reconnue"""
        query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(Sales) as total_sales,
                SUM(Profit) as total_profit,
                AVG(Profit_Margin_Percent) as avg_margin,
                SUM(Is_Returned) as total_returns
            FROM merged
        """
        data = self.db.execute_query(query).iloc[0]
        
        insight = f"Analyse globale: {data['total_orders']:,} commandes, ${data['total_sales']:,.0f} de CA, ${data['total_profit']:,.0f} de profit, {data['avg_margin']:.1f}% de marge moyenne"
        
        return {
            'question': question,
            'data': data,
            'insight': insight,
            'chart': None,
            'chart_type': 'none'
        }
    
    def get_suggested_questions(self):
        """Retourne des questions suggérées"""
        return [
            "Quelles sont les ventes par région?",
            "Quel est le profit par catégorie?",
            "Comment évoluent les ventes dans le temps?",
            "Quel est le taux de retour par marché?",
            "Quels sont les top produits rentables?",
            "Quel est le chiffre d'affaires total?",
            "Quelle est la marge moyenne?"
        ]

def main():
    # Test de l'IA
    bot = InsightBotAI()
    
    test_questions = [
        "Quelles sont les ventes par région?",
        "Quel est le profit par catégorie?",
        "Comment évoluent les ventes dans le temps?",
        "Quel est le taux de retour?"
    ]
    
    for question in test_questions:
        print(f"\n🤖 Question: {question}")
        result = bot.process_question(question)
        print(f"💡 Insight: {result['insight']}")
        print(f"📊 Données: {result['data'].head(3) if hasattr(result['data'], 'head') else result['data']}")

if __name__ == "__main__":
    main()