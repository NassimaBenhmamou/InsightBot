import os
import pandas as pd
from pathlib import Path

def find_csv_files():
    """Trouve tous les fichiers CSV dans le projet"""
    print("🔍 RECHERCHE DES FICHIERS CSV...")
    
    csv_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv'):
                full_path = os.path.join(root, file)
                csv_files.append(full_path)
                print(f"✅ Trouvé: {full_path}")
    
    return csv_files

def explore_file(file_path):
    """Explore un fichier CSV"""
    print(f"\n{'='*60}")
    print(f"📊 EXPLORATION: {file_path}")
    print(f"{'='*60}")
    
    try:
        # Essayer différents encodages
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"✅ Encodage réussi: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("❌ Impossible de lire le fichier avec les encodages courants")
            return None
        
        # Infos de base
        print(f"📁 Shape: {df.shape} (lignes: {df.shape[0]}, colonnes: {df.shape[1]})")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Aperçu des données
        print(f"\n👀 Aperçu des données:")
        print(df.head(3))
        
        # Types de données
        print(f"\n🎯 Types de données:")
        print(df.dtypes)
        
        # Valeurs manquantes
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"\n⚠️  Valeurs manquantes:")
            print(missing[missing > 0])
        else:
            print(f"\n✅ Aucune valeur manquante")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur avec {file_path}: {e}")
        return None

def main():
    # 1. Trouver tous les fichiers CSV
    csv_files = find_csv_files()
    
    if not csv_files:
        print("❌ Aucun fichier CSV trouvé!")
        print("\n📝 Conseil: Place tes fichiers dans:")
        print("   - insightbot/data/raw/")
        print("   - Ou à la racine du projet")
        return
    
    print(f"\n🎯 {len(csv_files)} fichiers CSV trouvés")
    
    # 2. Explorer chaque fichier
    all_data = {}
    for file_path in csv_files:
        df = explore_file(file_path)
        if df is not None:
            filename = os.path.basename(file_path)
            all_data[filename] = df
    
    # 3. Créer la structure de dossier si nécessaire
    if all_data and not os.path.exists('data/raw'):
        os.makedirs('data/raw', exist_ok=True)
        print(f"\n📁 Dossier 'data/raw' créé")
    
    return all_data

if __name__ == "__main__":
    main()