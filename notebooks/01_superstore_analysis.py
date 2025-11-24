import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Style pour les plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedSuperstoreAnalyzer:
    def __init__(self):
        self.base_path = r"C:\Users\NASSIMA\insightbot"
        self.data_path = f"{self.base_path}/data/raw"
        self.datasets = {}
        self.cleaned_data = {}
        
    def load_data(self):
        """Charge tous les datasets"""
        print("CHARGEMENT DES DONNEES...")
        
        try:
            self.datasets['orders'] = pd.read_csv(f"{self.data_path}/global_superstore_2016_orders.csv")
            self.datasets['returns'] = pd.read_csv(f"{self.data_path}/global_superstore_2016_returns.csv")
            self.datasets['peoples'] = pd.read_csv(f"{self.data_path}/global_superstore_2016_peoples.csv")
            
            print("✅ Donnees chargees avec succes!")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False
    
    def clean_numeric_data(self):
        """Nettoie les colonnes numeriques"""
        print("\nNETTOYAGE DES DONNEES NUMERIQUES...")
        df = self.datasets['orders'].copy()
        
        # Nettoyage Sales et Profit
        df['Sales'] = pd.to_numeric(
            df['Sales'].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        )
        df['Profit'] = pd.to_numeric(
            df['Profit'].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        )
        
        # Nettoyage dates
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
        
        self.cleaned_data = df
        print("✅ Donnees nettoyees!")
        return df
    
    def analyze_missing_values(self):
        """Analyse detaillee des valeurs manquantes"""
        print("\nANALYSE DES VALEURS MANQUANTES")
        print("=" * 50)
        
        df = self.datasets['orders']
        
        # Calcul des valeurs manquantes
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'Colonne': missing_data.index,
            'Valeurs_Manquantes': missing_data.values,
            'Pourcentage': missing_percent.values
        }).sort_values('Valeurs_Manquantes', ascending=False)
        
        # Filtrer seulement les colonnes avec valeurs manquantes
        missing_df = missing_df[missing_df['Valeurs_Manquantes'] > 0]
        
        if len(missing_df) > 0:
            print("Colonnes avec valeurs manquantes:")
            for _, row in missing_df.iterrows():
                print(f"  - {row['Colonne']}: {row['Valeurs_Manquantes']} ({row['Pourcentage']:.1f}%)")
            
            # Visualisation des valeurs manquantes
            self.plot_missing_values(missing_df)
        else:
            print("✅ Aucune valeur manquante trouvee!")
    
    def plot_missing_values(self, missing_df):
        """Plot les valeurs manquantes"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar plot
        bars = ax1.bar(missing_df['Colonne'], missing_df['Pourcentage'], color='coral')
        ax1.set_title('Pourcentage de Valeurs Manquantes par Colonne', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Pourcentage (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Ajouter les valeurs sur les bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Pie chart (seulement si pas trop de colonnes)
        if len(missing_df) <= 10:
            ax2.pie(missing_df['Valeurs_Manquantes'], labels=missing_df['Colonne'], autopct='%1.1f%%')
            ax2.set_title('Repartition des Valeurs Manquantes')
        
        plt.tight_layout()
        plt.show()
    
    def analyze_duplicates(self):
        """Analyse des doublons"""
        print("\nANALYSE DES DOUBLONS")
        print("=" * 50)
        
        df = self.datasets['orders']
        
        # Doublons complets
        complete_duplicates = df.duplicated().sum()
        print(f"Doublons complets: {complete_duplicates}")
        
        # Doublons partiels (Order ID)
        order_duplicates = df.duplicated(subset=['Order ID']).sum()
        print(f"Commandes dupliquees (Order ID): {order_duplicates}")
        
        # Doublons partiels (Customer ID)
        customer_duplicates = df.duplicated(subset=['Customer ID']).sum()
        print(f"Clients dupliques (Customer ID): {customer_duplicates}")
        
        if complete_duplicates > 0:
            print("\nExemple de doublons complets:")
            print(df[df.duplicated()].head())
    
    def descriptive_statistics(self):
        """Statistiques descriptives detaillees"""
        print("\nSTATISTIQUES DESCRIPTIVES")
        print("=" * 50)
        
        df = self.cleaned_data
        
        # Colonnes numeriques
        numeric_cols = ['Sales', 'Profit', 'Quantity', 'Discount', 'Shipping Cost']
        numeric_df = df[numeric_cols]
        
        print("Statistiques numeriques:")
        stats = numeric_df.describe().round(2)
        print(stats)
        
        # Visualisation des distributions
        self.plot_numeric_distributions(numeric_df)
        
        # Analyse des outliers
        self.detect_outliers(numeric_df)
    
    def plot_numeric_distributions(self, numeric_df):
        """Plot les distributions des variables numeriques"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, col in enumerate(numeric_df.columns):
            if i < len(axes):
                # Histogramme
                axes[i].hist(numeric_df[col], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
                axes[i].set_title(f'Distribution de {col}', fontweight='bold')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequence')
                
                # Ajouter ligne de moyenne
                mean_val = numeric_df[col].mean()
                axes[i].axvline(mean_val, color='red', linestyle='--', label=f'Moyenne: {mean_val:.2f}')
                axes[i].legend()
        
        # Cacher les axes non utilises
        for i in range(len(numeric_df.columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def detect_outliers(self, numeric_df):
        """Detection des outliers avec boxplots"""
        print("\nDETECTION DES OUTLIERS")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.ravel()
        
        for i, col in enumerate(numeric_df.columns):
            if i < len(axes):
                # Boxplot
                bp = axes[i].boxplot(numeric_df[col], patch_artist=True)
                bp['boxes'][0].set_facecolor('lightblue')
                axes[i].set_title(f'Boxplot de {col}', fontweight='bold')
                axes[i].set_ylabel(col)
                
                # Calcul des outliers
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = numeric_df[(numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)]
                print(f"  - {col}: {len(outliers)} outliers ({len(outliers)/len(numeric_df)*100:.2f}%)")
        
        # Cacher les axes non utilises
        for i in range(len(numeric_df.columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_categorical_data(self):
        """Analyse des donnees categorielles"""
        print("\nANALYSE DES DONNEES CATEGORIELLES")
        print("=" * 50)
        
        df = self.cleaned_data
        
        categorical_cols = ['Ship Mode', 'Segment', 'Category', 'Sub-Category', 'Region', 'Market', 'Order Priority']
        
        for col in categorical_cols:
            if col in df.columns:
                value_counts = df[col].value_counts()
                print(f"\n{col}:")
                for value, count in value_counts.head(10).items():
                    percentage = (count / len(df)) * 100
                    print(f"  - {value}: {count} ({percentage:.1f}%)")
        
        # Visualisations categorielles
        self.plot_categorical_distributions(df, categorical_cols)
    
    def plot_categorical_distributions(self, df, categorical_cols):
        """Plot les distributions categorielles"""
        # Selectionner les 4 premieres colonnes categorielles pour la visualisation
        plot_cols = categorical_cols[:4]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.ravel()
        
        for i, col in enumerate(plot_cols):
            if i < len(axes):
                value_counts = df[col].value_counts().head(10)  # Top 10 seulement
                
                # Bar plot
                bars = axes[i].bar(value_counts.index, value_counts.values, color='lightgreen')
                axes[i].set_title(f'Distribution de {col}', fontweight='bold')
                axes[i].set_ylabel('Nombre')
                axes[i].tick_params(axis='x', rotation=45)
                
                # Ajouter les pourcentages
                total = len(df)
                for j, (value, count) in enumerate(value_counts.items()):
                    percentage = (count / total) * 100
                    axes[i].text(j, count + total * 0.01, f'{percentage:.1f}%', 
                                ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def financial_analysis(self):
        """Analyse financiere detaillee"""
        print("\nANALYSE FINANCIERE DETAILLEE")
        print("=" * 50)
        
        df = self.cleaned_data
        
        # KPIs financiers
        total_sales = df['Sales'].sum()
        total_profit = df['Profit'].sum()
        avg_profit_margin = (df['Profit'] / df['Sales']).mean() * 100
        
        print(f"Chiffre d'affaires total: ${total_sales:,.2f}")
        print(f"Profit total: ${total_profit:,.2f}")
        print(f"Marge moyenne: {avg_profit_margin:.2f}%")
        print(f"Quantite totale vendue: {df['Quantity'].sum():,}")
        print(f"Remise moyenne: {df['Discount'].mean() * 100:.2f}%")
        
        # Profitabilite
        profitable_orders = len(df[df['Profit'] > 0])
        loss_orders = len(df[df['Profit'] < 0])
        profit_ratio = (profitable_orders / len(df)) * 100
        
        print(f"Commandes profitables: {profitable_orders} ({profit_ratio:.1f}%)")
        print(f"Commandes en perte: {loss_orders} ({(100 - profit_ratio):.1f}%)")
        
        # Visualisations financieres
        self.plot_financial_metrics(df)
    
    def plot_financial_metrics(self, df):
        """Plot les metriques financieres"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sales vs Profit', 'Distribution des Marges', 
                          'Profit par Categorie', 'Evolution des Ventes Mensuelles'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Sales vs Profit (scatter)
        fig.add_trace(
            go.Scatter(x=df['Sales'], y=df['Profit'], mode='markers', 
                      marker=dict(size=3, opacity=0.5), name='Sales vs Profit'),
            row=1, col=1
        )
        
        # 2. Distribution des marges
        profit_margin = (df['Profit'] / df['Sales'] * 100).replace([np.inf, -np.inf], np.nan).dropna()
        fig.add_trace(
            go.Histogram(x=profit_margin, nbinsx=50, name='Distribution Marges'),
            row=1, col=2
        )
        
        # 3. Profit par categorie
        profit_by_category = df.groupby('Category')['Profit'].sum()
        fig.add_trace(
            go.Bar(x=profit_by_category.index, y=profit_by_category.values, 
                  name='Profit par Categorie'),
            row=2, col=1
        )
        
        # 4. Evolution des ventes mensuelles
        monthly_sales = df.set_index('Order Date').resample('M')['Sales'].sum()
        fig.add_trace(
            go.Scatter(x=monthly_sales.index, y=monthly_sales.values, 
                      mode='lines', name='Ventes Mensuelles'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text="Tableau de Bord Financier")
        fig.show()
    
    def correlation_analysis(self):
        """Analyse des correlations"""
        print("\nANALYSE DES CORRELATIONS")
        print("=" * 50)
        
        df = self.cleaned_data
        
        # Selectionner les colonnes numeriques
        numeric_cols = ['Sales', 'Profit', 'Quantity', 'Discount', 'Shipping Cost']
        correlation_matrix = df[numeric_cols].corr()
        
        print("Matrice de correlation:")
        print(correlation_matrix.round(3))
        
        # Heatmap de correlation
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Matrice de Correlation des Variables Numeriques', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        # Analyser les correlations fortes
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.5:  # Correlation forte
                    strong_correlations.append((
                        correlation_matrix.columns[i],
                        correlation_matrix.columns[j],
                        corr
                    ))
        
        if strong_correlations:
            print("\nCorrelations fortes (|r| > 0.5):")
            for var1, var2, corr in strong_correlations:
                print(f"  - {var1} <-> {var2}: {corr:.3f}")
    
    def generate_summary_report(self):
        """Genere un rapport de synthese"""
        print("\n" + "="*70)
        print("RAPPORT DE SYNTHESE - GLOBAL SUPERSTORE 2016")
        print("="*70)
        
        df = self.cleaned_data
        
        summary = {
            "Volume Donnees": f"{len(df):,} commandes, {len(df.columns)} colonnes",
            "Periode Couverte": f"{df['Order Date'].min().strftime('%Y-%m-%d')} to {df['Order Date'].max().strftime('%Y-%m-%d')}",
            "Performance Financiere": f"CA: ${df['Sales'].sum():,.0f} | Profit: ${df['Profit'].sum():,.0f}",
            "Couverture Geographique": f"{df['Country'].nunique()} pays, {df['Region'].nunique()} regions",
            "Base Clients": f"{df['Customer ID'].nunique():,} clients uniques",
            "Portfolio Produits": f"{df['Product ID'].nunique():,} produits, {df['Category'].nunique()} categories",
            "Qualite Donnees": f"Valeurs manquantes: {df.isnull().sum().sum()} | Doublons: {df.duplicated().sum()}"
        }
        
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        print("\nRECOMMANDATIONS POUR INSIGHTBOT:")
        recommendations = [
            "✅ Dataset bien adapte pour analyses e-commerce",
            "✅ Metriques financieres completes (Sales, Profit, etc.)",
            "✅ Dimensions riches (Geographie, Produits, Clients)",
            "✅ Donnees temporelles pour analyses de trends",
            "⚠️  Nettoyer colonnes Sales/Profit (format texte)",
            "⚠️  Gerer valeurs manquantes Postal Code",
            "🎯 Ideal pour demonstration InsightBot!"
        ]
        
        for rec in recommendations:
            print(f"  {rec}")

def main():
    analyzer = AdvancedSuperstoreAnalyzer()
    
    print("DEMARRAGE DE L'ANALYSE AVANCEE GLOBAL SUPERSTORE")
    print("=" * 70)
    
    # 1. Chargement des donnees
    if not analyzer.load_data():
        return
    
    # 2. Nettoyage des donnees
    analyzer.clean_numeric_data()
    
    # 3. Analyses completes
    analyzer.analyze_missing_values()
    analyzer.analyze_duplicates()
    analyzer.descriptive_statistics()
    analyzer.analyze_categorical_data()
    analyzer.financial_analysis()
    analyzer.correlation_analysis()
    
    # 4. Rapport final
    analyzer.generate_summary_report()
    
    print("\nANALYSE TERMINEE!")
    print("Prochaines etapes: Nettoyage automatique -> Base de donnees -> InsightBot")

if __name__ == "__main__":
    main()