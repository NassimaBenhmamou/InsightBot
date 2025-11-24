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
        self.base_path = Path(r"C:\Users\NASSIMA\insightbot")
        self.raw_data_path = self.base_path / "data" / "raw"
        self.processed_data_path = self.base_path / "data" / "processed"
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        self.datasets = {}
        self.cleaned_datasets = {}
        
        logger.info("🧹 Initialisation du DataCleaner")
    
    def load_raw_data(self):
        """Charge tous les datasets bruts"""
        logger.info("📥 Chargement des données brutes...")
        
        try:
            # Chargement des fichiers CSV
            self.datasets['orders'] = pd.read_csv(self.raw_data_path / "global_superstore_2016_orders.csv")
            self.datasets['returns'] = pd.read_csv(self.raw_data_path / "global_superstore_2016_returns.csv")
            self.datasets['peoples'] = pd.read_csv(self.raw_data_path / "global_superstore_2016_peoples.csv")
            
            logger.info("✅ Données brutes chargées avec succès")
            self._log_dataset_info()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement: {e}")
            return False
    
    def _log_dataset_info(self):
        """Log les informations basiques des datasets"""
        for name, df in self.datasets.items():
            logger.info(f"📊 {name}: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    def clean_orders_data(self):
        """Nettoie la table orders - C'EST LA PLUS IMPORTANTE"""
        logger.info("🧹 Nettoyage de la table Orders...")
        df = self.datasets['orders'].copy()
        
        # 1. NETTOYAGE DES COLONNES NUMÉRIQUES (Problème principal)
        logger.info("1. Nettoyage des colonnes numériques...")
        df = self._clean_numeric_columns(df)
        
        # 2. NETTOYAGE DES DATES
        logger.info("2. Nettoyage des dates...")
        df = self._clean_date_columns(df)
        
        # 3. GESTION DES VALEURS MANQUANTES
        logger.info("3. Gestion des valeurs manquantes...")
        df = self._handle_missing_values(df)
        
        # 4. STANDARDISATION DES TEXTES
        logger.info("4. Standardisation des textes...")
        df = self._standardize_text_columns(df)
        
        # 5. AJOUT DE COLONNES CALCULÉES (Pour InsightBot)
        logger.info("5. Ajout de colonnes calculées...")
        df = self._add_calculated_columns(df)
        
        # 6. GESTION DES OUTLIERS (Optionnel)
        logger.info("6. Gestion des outliers...")
        df = self._handle_outliers(df)
        
        # 7. VÉRIFICATION DE LA QUALITÉ
        logger.info("7. Vérification de la qualité...")
        self._validate_data_quality(df, 'orders')
        
        self.cleaned_datasets['orders'] = df
        logger.info(f"✅ Orders nettoyé: {df.shape}")
        return df
    
    def _clean_numeric_columns(self, df):
        """Nettoie les colonnes numériques problématiques"""
        # Colonnes à nettoyer (Sales et Profit sont en texte avec $)
        numeric_clean_mapping = {
            'Sales': {
                'original_dtype': df['Sales'].dtype,
                'action': 'remove_currency'
            },
            'Profit': {
                'original_dtype': df['Profit'].dtype,
                'action': 'remove_currency'
            }
        }
        
        for col, info in numeric_clean_mapping.items():
            if col in df.columns:
                logger.info(f"   - Nettoyage de {col} ({info['original_dtype']} -> float64)")
                
                if info['action'] == 'remove_currency':
                    # Enlève $ et , puis convertit en float
                    df[col] = (df[col].astype(str)
                                .str.replace('$', '', regex=False)
                                .str.replace(',', '', regex=False)
                                .str.strip())
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Vérification après nettoyage
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    logger.warning(f"     {null_count} valeurs non converties dans {col}")
        
        return df
    
    def _clean_date_columns(self, df):
        """Nettoie les colonnes de dates"""
        date_columns = ['Order Date', 'Ship Date']
        
        for col in date_columns:
            if col in df.columns:
                logger.info(f"   - Conversion de {col} en datetime")
                
                # Essayer différents formats de date
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Vérifier les conversions échouées
                failed_conversions = df[col].isnull().sum()
                if failed_conversions > 0:
                    logger.warning(f"     {failed_conversions} dates non converties dans {col}")
        
        return df
    
    def _handle_missing_values(self, df):
        """Gère les valeurs manquantes"""
        missing_before = df.isnull().sum().sum()
        
        # Stratégie par colonne
        missing_strategy = {
            'Postal Code': 'fill_unknown',  # 80% manquants → on remplace
            'Sales': 'drop',                # Trop important, on supprime
            'Profit': 'drop',               # Trop important, on supprime
            'default': 'fill_unknown'       # Stratégie par défaut
        }
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                strategy = missing_strategy.get(col, missing_strategy['default'])
                
                if strategy == 'fill_unknown':
                    if df[col].dtype == 'object':
                        df[col] = df[col].fillna('Unknown')
                    else:
                        df[col] = df[col].fillna(0)
                    logger.info(f"   - {col}: {null_count} valeurs manquantes → remplacées")
                
                elif strategy == 'drop':
                    df = df.dropna(subset=[col])
                    logger.info(f"   - {col}: {null_count} valeurs manquantes → lignes supprimées")
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"   Valeurs manquantes: {missing_before} → {missing_after}")
        
        return df
    
    def _standardize_text_columns(self, df):
        """Standardise les colonnes texte"""
        text_columns = ['Ship Mode', 'Segment', 'Category', 'Sub-Category', 
                       'Order Priority', 'Region', 'Market', 'Country', 'State', 'City']
        
        for col in text_columns:
            if col in df.columns and df[col].dtype == 'object':
                # Standardisation : Premier caractère en majuscule, reste en minuscule
                df[col] = df[col].str.title()
                
                # Supprimer les espaces excédentaires
                df[col] = df[col].str.strip()
        
        logger.info("   Textes standardisés")
        return df
    
    def _add_calculated_columns(self, df):
        """Ajoute des colonnes calculées pour l'analyse"""
        logger.info("   Ajout de colonnes calculées...")
        
        # 1. Métriques de profitabilité
        df['Profit_Margin_Percent'] = (df['Profit'] / df['Sales'] * 100).round(2)
        
        # 2. Délai de livraison
        df['Processing_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
        
        # 3. Catégorisation des ventes
        df['Sales_Category'] = pd.cut(
            df['Sales'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Very Large'],
            right=False
        )
        
        # 4. Rentabilité binaire
        df['Is_Profitable'] = df['Profit'] > 0
        
        # 5. Année et mois pour l'analyse temporelle
        df['Order_Year'] = df['Order Date'].dt.year
        df['Order_Month'] = df['Order Date'].dt.month
        df['Order_YearMonth'] = df['Order Date'].dt.to_period('M')
        
        logger.info("   ✅ Colonnes calculées ajoutées")
        return df
    
    def _handle_outliers(self, df):
        """Gère les outliers extrêmes"""
        numeric_cols = ['Sales', 'Profit', 'Quantity', 'Discount', 'Shipping Cost']
        
        for col in numeric_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.01)  # 1er percentile
                Q3 = df[col].quantile(0.99)  # 99ème percentile
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Compter les outliers
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                
                if outliers > 0:
                    logger.info(f"   - {col}: {outliers} outliers détectés")
                    # Pour l'instant, on garde les outliers car ils peuvent être intéressants
        
        return df
    
    def _validate_data_quality(self, df, dataset_name):
        """Valide la qualité des données après nettoyage"""
        logger.info(f"   Validation de la qualité pour {dataset_name}...")
        
        checks = {
            'Lignes vides': len(df) > 0,
            'Sales numérique': pd.api.types.is_numeric_dtype(df['Sales']),
            'Profit numérique': pd.api.types.is_numeric_dtype(df['Profit']),
            'Dates valides': df['Order Date'].notna().all(),
            'Valeurs manquantes': df.isnull().sum().sum() == 0
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"     {status} {check}")
        
        return all(checks.values())
    
    def clean_returns_data(self):
        """Nettoie la table returns"""
        logger.info("🧹 Nettoyage de la table Returns...")
        df = self.datasets['returns'].copy()
        
        # Standardisation simple
        df['Returned'] = df['Returned'].str.title().str.strip()
        df['Region'] = df['Region'].str.title().str.strip()
        
        # Ajouter un indicateur booléen
        df['Is_Returned'] = True
        
        self.cleaned_datasets['returns'] = df
        logger.info(f"✅ Returns nettoyé: {df.shape}")
        return df
    
    def clean_peoples_data(self):
        """Nettoie la table peoples"""
        logger.info("🧹 Nettoyage de la table Peoples...")
        df = self.datasets['peoples'].copy()
        
        # Standardisation
        df['Region'] = df['Region'].str.title().str.strip()
        df['Person'] = df['Person'].str.title().str.strip()
        
        # Renommer pour plus de clarté
        df = df.rename(columns={'Person': 'Regional_Manager'})
        
        self.cleaned_datasets['peoples'] = df
        logger.info(f"✅ Peoples nettoyé: {df.shape}")
        return df
    
    def create_merged_dataset(self):
        """Crée un dataset fusionné pour InsightBot"""
        logger.info("🔗 Création du dataset fusionné...")
        
        orders = self.cleaned_datasets['orders']
        returns = self.cleaned_datasets['returns']
        peoples = self.cleaned_datasets['peoples']
        
        # 1. Fusion avec les retours
        merged_df = orders.merge(
            returns[['Order ID', 'Is_Returned']],
            on='Order ID',
            how='left'
        )
        merged_df['Is_Returned'] = merged_df['Is_Returned'].fillna(False)
        
        # 2. Fusion avec les responsables régionaux
        merged_df = merged_df.merge(
            peoples,
            on='Region',
            how='left'
        )
        
        # 3. Ajout de métriques finales
        merged_df['Total_Cost'] = merged_df['Sales'] - merged_df['Profit']
        merged_df['Return_Rate_Flag'] = merged_df['Is_Returned'].astype(int)
        
        self.cleaned_datasets['merged'] = merged_df
        logger.info(f"✅ Dataset fusionné créé: {merged_df.shape}")
        return merged_df
    
    def save_cleaned_data(self):
        """Sauvegarde tous les datasets nettoyés"""
        logger.info("💾 Sauvegarde des données nettoyées...")
        
        for name, df in self.cleaned_datasets.items():
            filename = f"cleaned_{name}.csv"
            filepath = self.processed_data_path / filename
            
            df.to_csv(filepath, index=False)
            logger.info(f"   ✅ {filename} sauvegardé ({df.shape})")
    
    def generate_cleaning_report(self):
        """Génère un rapport de nettoyage détaillé"""
        logger.info("\n" + "="*60)
        logger.info("📋 RAPPORT DE NETTOYAGE - INSIGHTBOT")
        logger.info("="*60)
        
        if 'merged' in self.cleaned_datasets:
            df = self.cleaned_datasets['merged']
            
            report = {
                "Dataset Final": f"{df.shape[0]:,} lignes, {df.shape[1]} colonnes",
                "Période": f"{df['Order Date'].min().strftime('%Y-%m-%d')} to {df['Order Date'].max().strftime('%Y-%m-%d')}",
                "Métriques Clés": f"CA: ${df['Sales'].sum():,.0f} | Profit: ${df['Profit'].sum():,.0f}",
                "Qualité Données": f"Valeurs manquantes: {df.isnull().sum().sum()}",
                "Colonnes Calculées": f"{len([col for col in df.columns if col.endswith('_Percent') or col.startswith('Is_')])} ajoutées",
                "Retours": f"{df['Is_Returned'].sum():,} commandes retournées"
            }
            
            for key, value in report.items():
                logger.info(f"   {key}: {value}")
        
        logger.info("\n🎯 PRÊT POUR INSIGHTBOT!")
        logger.info("Prochaines étapes: Base de données → IA → Interface")
    
    def run_complete_cleaning(self):
        """Exécute le pipeline complet de nettoyage"""
        logger.info("🚀 DÉMARRAGE DU NETTOYAGE COMPLET")
        logger.info("="*50)
        
        try:
            # 1. Chargement
            if not self.load_raw_data():
                return False
            
            # 2. Nettoyage individuel
            self.clean_orders_data()
            self.clean_returns_data()
            self.clean_peoples_data()
            
            # 3. Fusion
            self.create_merged_dataset()
            
            # 4. Sauvegarde
            self.save_cleaned_data()
            
            # 5. Rapport
            self.generate_cleaning_report()
            
            logger.info("🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage: {e}")
            return False

def main():
    """Fonction principale pour tester le nettoyage"""
    cleaner = DataCleaner()
    success = cleaner.run_complete_cleaning()
    
    if success and 'merged' in cleaner.cleaned_datasets:
        # Aperçu des données nettoyées
        df = cleaner.cleaned_datasets['merged']
        print("\n👀 APERÇU DES DONNÉES NETTOYÉES:")
        print(f"Shape: {df.shape}")
        print(f"Colonnes: {list(df.columns)}")
        print(f"\n3 premières lignes:")
        print(df.head(3))
        print(f"\nTypes de données:")
        print(df.dtypes)
        
        return cleaner
    else:
        print("❌ Le nettoyage a échoué")
        return None

if __name__ == "__main__":
    cleaner = main()