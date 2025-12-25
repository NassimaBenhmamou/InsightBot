import duckdb
import pandas as pd
from pathlib import Path
import logging

class DatabaseManager:
    def __init__(self):
        """
        Initialise le gestionnaire de base de données avec des chemins relatifs
        pour garantir la portabilité sur n'importe quel ordinateur.
        """
        # --- DÉTECTION DYNAMIQUE DU CHEMIN DU PROJET ---
        # Path(__file__) donne le chemin vers database_manager.py
        # .parent.parent.parent remonte de 'core' -> 'src' -> 'InsightBot' (racine)
        self.project_root = Path(__file__).parent.parent.parent
        
        # Définition des dossiers de données par rapport à la racine du projet
        self.base_path = self.project_root
        self.db_dir = self.base_path / "data" / "database"
        self.db_path = self.db_dir / "insightbot.db"
        
        # Création automatique du dossier de la base de données s'il n'existe pas
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        
    def connect(self):
        """Établit la connexion DuckDB avec gestion d'erreur améliorée"""
        try:
            self.conn = duckdb.connect(str(self.db_path))
            print(f"✅ Connecté à DuckDB : {self.db_path}")
            return self.conn
        except Exception as e:
            error_msg = str(e)
            if "utilisé par un autre processus" in error_msg or "used by another process" in error_msg:
                print(f"⚠️ Base de données déjà ouverte. Création d'une connexion temporaire...")
                try:
                    # Créer une connexion temporaire en mémoire
                    import tempfile
                    import os
                    temp_db = os.path.join(tempfile.gettempdir(), 'insightbot_temp.db')
                    self.conn = duckdb.connect(temp_db)
                    
                    # Copier les données depuis les CSV directement
                    print(f"✅ Connexion temporaire créée : {temp_db}")
                    print("📊 Chargement des données CSV directement...")
                    
                    # Charger les tables depuis les CSV
                    self._load_csv_tables_directly()
                    
                    return self.conn
                except Exception as e2:
                    print(f"❌ Impossible de créer connexion temporaire : {e2}")
                    return None
            else:
                print(f"❌ Erreur lors de la connexion à DuckDB : {e}")
                return None
    
    def _load_csv_tables_directly(self):
        """Charge les tables directement depuis les CSV quand la DB principale est occupée"""
        try:
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
                    try:
                        # Créer la table temporaire
                        self.conn.execute(f"""
                            CREATE OR REPLACE TABLE {table_name} AS 
                            SELECT * FROM read_csv_auto('{str(file_path)}')
                        """)
                        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                        print(f"  ✅ Table {table_name} chargée : {row_count} lignes")
                    except Exception as e:
                        print(f"  ❌ Erreur chargement {table_name} : {e}")
                else:
                    print(f"  ⚠️ Fichier manquant : {filename}")
        except Exception as e:
            print(f"❌ Erreur chargement CSV direct : {e}")
    
    def create_tables(self):
        """Crée les tables à partir des fichiers CSV situés dans data/processed"""
        processed_path = self.base_path / "data" / "processed"
        
        # Vérifier si le dossier des CSV existe
        if not processed_path.exists():
            print(f"⚠️ Dossier introuvable : {processed_path}")
            print("Veuillez vous assurer que vos fichiers CSV sont dans 'data/processed/'")
            return

        tables = {
            'orders': 'cleaned_orders.csv',
            'returns': 'cleaned_returns.csv', 
            'peoples': 'cleaned_peoples.csv',
            'merged': 'cleaned_merged.csv'
        }
        
        for table_name, filename in tables.items():
            file_path = processed_path / filename
            if file_path.exists():
                try:
                    # Crée ou remplace la table à partir du CSV
                    self.conn.execute(f"""
                        CREATE OR REPLACE TABLE {table_name} AS 
                        SELECT * FROM read_csv_auto('{str(file_path)}')
                    """)
                    row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    print(f"✅ Table {table_name} créée : {row_count} lignes")
                except Exception as e:
                    print(f"❌ Erreur lors de la création de la table {table_name} : {e}")
            else:
                print(f"⚠️ Fichier manquant : {filename}")
    
    def execute_query(self, query):
        """Exécute une requête SQL et retourne un DataFrame avec gestion d'erreur"""
        try:
            if self.conn is None:
                print("⚠️ Connexion non établie, tentative de connexion...")
                self.connect()
                if self.conn is None:
                    print("❌ Impossible d'établir la connexion")
                    return None
            
            result = self.conn.execute(query).fetchdf()
            return result
        except Exception as e:
            print(f"❌ Erreur requête : {e}")
            return None
    
    def get_table_info(self, table_name):
        """Récupère les informations (colonnes, types) d'une table"""
        try:
            info = self.conn.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """).fetchall()
            return info
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du schéma : {e}")
            return []
        
    def get_tables(self) -> list:
        """Récupère la liste des tables disponibles dans la base de données"""
        try:
            if self.conn is None:
                self.connect()
            
            # On récupère les noms des tables
            res = self.conn.execute("SHOW TABLES").fetchall()
            return [row[0] for row in res]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des tables : {e}")
            return []
    
    def test_insightbot_queries(self):
        """Teste des requêtes types pour vérifier le bon fonctionnement"""
        print("\n🧪 TEST DES REQUÊTES INSIGHTBOT :")
        
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
            """
        }
        
        for name, query in test_queries.items():
            print(f"\n📊 {name} :")
            result = self.execute_query(query)
            if result is not None and not result.empty:
                print(result.head())
            else:
                print("Aucune donnée retournée.")
    
    def close(self):
        """Ferme la connexion DuckDB"""
        if self.conn:
            self.conn.close()
            print("✅ Connexion DuckDB fermée")

def main():
    db = DatabaseManager()
    db.connect()
    db.create_tables()
    db.test_insightbot_queries()
    
    # Affichage de la structure pour vérification
    print(f"\n📋 STRUCTURE DE LA BASE :")
    tables = ['orders', 'returns', 'peoples', 'merged']
    for table in tables:
        info = db.get_table_info(table)
        if info:
            print(f"\n🏷️  {table.upper()} ({len(info)} colonnes) :")
            for col_name, col_type in info[:5]: 
                print(f"   - {col_name} : {col_type}")
            if len(info) > 5:
                print(f"   - ... et {len(info) - 5} autres colonnes")
    
    db.close()

if __name__ == "__main__":
    main()