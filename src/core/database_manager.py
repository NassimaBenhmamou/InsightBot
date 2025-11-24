import duckdb
import pandas as pd
from pathlib import Path
import logging

class DatabaseManager:
    def __init__(self):
        self.base_path = Path(r"C:\Users\NASSIMA\insightbot")
        self.db_path = self.base_path / "data" / "database" / "insightbot.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        """Établit la connexion DuckDB"""
        self.conn = duckdb.connect(str(self.db_path))
        print(f"✅ Connecté à DuckDB: {self.db_path}")
        return self.conn
    
    def create_tables(self):
        """Crée les tables à partir des CSV nettoyés"""
        processed_path = self.base_path / "data" / "processed"
        
        tables = {
            'orders': 'cleaned_orders.csv',
            'returns': 'cleaned_returns.csv', 
            'peoples': 'cleaned_peoples.csv',
            'merged': 'cleaned_merged.csv'
        }
        
        for table_name, filename in tables.items():
            file_path = processed_path / filename
            if file_path.exists():
                # Crée la table à partir du CSV
                self.conn.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS 
                    SELECT * FROM read_csv_auto('{file_path}')
                """)
                row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                print(f"✅ Table {table_name} créée: {row_count} lignes")
    
    def execute_query(self, query):
        """Exécute une requête SQL"""
        try:
            result = self.conn.execute(query).fetchdf()
            return result
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
            return None
    
    def get_table_info(self, table_name):
        """Récupère les infos d'une table"""
        info = self.conn.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """).fetchall()
        return info
    
    def test_insightbot_queries(self):
        """Teste des requêtes types pour InsightBot"""
        print("\n🧪 TEST DES REQUÊTES INSIGHTBOT:")
        
        test_queries = {
            "Ventes par région": """
                SELECT Region, SUM(Sales) as total_sales
                FROM merged 
                GROUP BY Region 
                ORDER BY total_sales DESC
                LIMIT 10
            """,
            "Profit par catégorie": """
                SELECT Category, SUM(Profit) as total_profit
                FROM merged 
                GROUP BY Category 
                ORDER BY total_profit DESC
            """,
            "Top produits rentables": """
                SELECT 
                    "Product Name" as Product_Name,
                    SUM(Sales) as total_sales,
                    SUM(Profit) as total_profit,
                    AVG(Profit_Margin_Percent) as avg_margin
                FROM merged 
                GROUP BY "Product Name"
                HAVING total_profit > 0
                ORDER BY total_profit DESC
                LIMIT 5
            """,
            "Évolution mensuelle": """
                SELECT 
                    Order_YearMonth,
                    SUM(Sales) as monthly_sales,
                    SUM(Profit) as monthly_profit
                FROM merged 
                GROUP BY Order_YearMonth
                ORDER BY Order_YearMonth
            """,
            "Taux de retour par marché": """
                SELECT 
                    Market,
                    COUNT(*) as total_orders,
                    SUM(Is_Returned) as returned_orders,
                    (SUM(Is_Returned) * 100.0 / COUNT(*)) as return_rate
                FROM merged
                GROUP BY Market
                ORDER BY return_rate DESC
            """
        }
        
        for name, query in test_queries.items():
            print(f"\n📊 {name}:")
            result = self.execute_query(query)
            if result is not None:
                print(result.head())
    
    def close(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            print("✅ Connexion DuckDB fermée")

def main():
    db = DatabaseManager()
    db.connect()
    db.create_tables()
    db.test_insightbot_queries()
    
    # Info sur les tables
    print(f"\n📋 STRUCTURE DE LA BASE:")
    tables = ['orders', 'returns', 'peoples', 'merged']
    for table in tables:
        info = db.get_table_info(table)
        print(f"\n🏷️  {table.upper()} ({len(info)} colonnes):")
        for col_name, col_type in info[:5]:  # Premieres 5 colonnes
            print(f"   - {col_name}: {col_type}")
        if len(info) > 5:
            print(f"   - ... et {len(info) - 5} autres colonnes")
    
    db.close()

if __name__ == "__main__":
    main()