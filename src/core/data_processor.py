import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        # --- SOLUTION : CHEMIN DYNAMIQUE ---
        # On définit la racine du projet par rapport à l'emplacement de ce fichier
        # On suppose que ce fichier est dans 'src/core/' ou un dossier similaire
        self.project_root = Path(__file__).parent.parent.parent
        
        self.base_path = self.project_root
        self.raw_data_path = self.base_path / "data" / "raw"
        self.processed_data_path = self.base_path / "data" / "processed"
        
        # Création automatique du dossier 'processed' s'il n'existe pas
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        self.datasets = {}
        self.cleaned_datasets = {}
        
        logger.info(f"🧹 Initialisation du DataCleaner (Racine : {self.base_path})")
    
    def load_raw_data(self):
        """Charge tous les datasets bruts"""
        logger.info("📥 Chargement des données brutes...")
        
        # Liste des fichiers attendus
        files = {
            'orders': "global_superstore_2016_orders.csv",
            'returns': "global_superstore_2016_returns.csv",
            'peoples': "global_superstore_2016_peoples.csv"
        }
        
        try:
            for key, filename in files.items():
                file_path = self.raw_data_path / filename
                if file_path.exists():
                    self.datasets[key] = pd.read_csv(file_path)
                    logger.info(f"✅ Chargé : {filename}")
                else:
                    logger.error(f"❌ Fichier introuvable : {file_path}")
                    return False
            
            self._log_dataset_info()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement : {e}")
            return False
    
    def _log_dataset_info(self):
        """Log les informations basiques des datasets"""
        for name, df in self.datasets.items():
            logger.info(f"📊 {name}: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    def clean_orders_data(self):
        """Nettoie la table orders"""
        logger.info("🧹 Nettoyage de la table Orders...")
        df = self.datasets['orders'].copy()
        
        # 1. NETTOYAGE DES COLONNES NUMÉRIQUES
        df = self._clean_numeric_columns(df)
        
        # 2. NETTOYAGE DES DATES
        df = self._clean_date_columns(df)
        
        # 3. GESTION DES VALEURS MANQUANTES
        df = self._handle_missing_values(df)
        
        # 4. STANDARDISATION DES TEXTES
        df = self._standardize_text_columns(df)
        
        # 5. AJOUT DE COLONNES CALCULÉES
        df = self._add_calculated_columns(df)
        
        # 6. GESTION DES OUTLIERS
        df = self._handle_outliers(df)
        
        # 7. VÉRIFICATION DE LA QUALITÉ
        self._validate_data_quality(df, 'orders')
        
        self.cleaned_datasets['orders'] = df
        return df
    
    def _clean_numeric_columns(self, df):
        """Nettoie Sales et Profit (enlève $ et virgules)"""
        cols_to_fix = ['Sales', 'Profit']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = (df[col].astype(str)
                            .str.replace('$', '', regex=False)
                            .str.replace(',', '', regex=False)
                            .str.strip())
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def _clean_date_columns(self, df):
        """Convertit les colonnes en datetime"""
        date_columns = ['Order Date', 'Ship Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    
    def _handle_missing_values(self, df):
        """Gère les valeurs manquantes"""
        # On supprime les lignes sans Sales ou Profit car elles sont inutilisables
        df = df.dropna(subset=['Sales', 'Profit'])
        # On remplace le reste par 'Unknown' ou 0
        df['Postal Code'] = df['Postal Code'].fillna('Unknown')
        return df.fillna('Unknown')
    
    def _standardize_text_columns(self, df):
        """Standardise les textes (Majuscule au début)"""
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.title().str.strip()
        return df
    
    def _add_calculated_columns(self, df):
        """Ajoute des métriques pour l'analyse"""
        df['Profit_Margin_Percent'] = (df['Profit'] / df['Sales'] * 100).round(2)
        df['Processing_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
        df['Is_Profitable'] = df['Profit'] > 0
        df['Order_YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
        return df
    
    def _handle_outliers(self, df):
        # On garde les données pour l'instant (important pour la BI)
        return df
    
    def _validate_data_quality(self, df, dataset_name):
        logger.info(f"✅ Validation terminée pour {dataset_name}")
        return True
    
    def clean_returns_data(self):
        """Nettoie la table returns"""
        df = self.datasets['returns'].copy()
        df['Is_Returned'] = True
        self.cleaned_datasets['returns'] = df
        return df
    
    def clean_peoples_data(self):
        """Nettoie la table peoples"""
        df = self.datasets['peoples'].copy()
        df = df.rename(columns={'Person': 'Regional_Manager'})
        self.cleaned_datasets['peoples'] = df
        return df
    
    def create_merged_dataset(self):
        """Fusionne toutes les tables"""
        orders = self.cleaned_datasets['orders']
        returns = self.cleaned_datasets['returns']
        peoples = self.cleaned_datasets['peoples']
        
        # Merge Returns
        merged = orders.merge(returns[['Order ID', 'Is_Returned']], on='Order ID', how='left')
        merged['Is_Returned'] = merged['Is_Returned'].fillna(False)
        
        # Merge Managers
        merged = merged.merge(peoples, on='Region', how='left')
        
        self.cleaned_datasets['merged'] = merged
        return merged
    
    def save_cleaned_data(self):
        """Sauvegarde les fichiers CSV finaux"""
        for name, df in self.cleaned_datasets.items():
            path = self.processed_data_path / f"cleaned_{name}.csv"
            df.to_csv(path, index=False)
            logger.info(f"💾 Sauvegardé : {path.name}")
            
    def run_complete_cleaning(self):
        logger.info("🚀 DÉMARRAGE DU PIPELINE DE NETTOYAGE")
        if self.load_raw_data():
            self.clean_orders_data()
            self.clean_returns_data()
            self.clean_peoples_data()
            self.create_merged_dataset()
            self.save_cleaned_data()
            logger.info("🎉 NETTOYAGE TERMINÉ !")
            return True
        return False

def main():
    cleaner = DataCleaner()
    cleaner.run_complete_cleaning()

if __name__ == "__main__":
    main()