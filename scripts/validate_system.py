"""
Script de validation du système InsightBot
"""
import sys
import os
from pathlib import Path
import logging

# Ajout du chemin src au PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_system():
    """Valide tous les composants du système"""
    print("🔍 Validation du système InsightBot...")
    print(f"📁 Répertoire projet: {project_root}")
    print(f"📁 Chemin src: {src_path}")
    
    # 1. Vérification des imports
    print("\n1. Vérification des imports...")
    try:
        from core.database_manager import DatabaseManager
        print("✅ DatabaseManager importé")
        
        #from core.nosql_manager import NoSQLManager
        print("✅ NoSQLManager importé")
        
        from core.ai_provider import AIProvider
        print("✅ AIProvider importé")
        
        from core.insightbot_gpt import InsightBotGPT
        print("✅ InsightBotGPT importé")
        
        print("✅ Tous les imports réussis")
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("Traceback complet:")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. Vérification des chemins
    print("\n2. Vérification des chemins...")
    paths_to_check = [
        (project_root / "data/database/insightbot.db", "Fichier base de données"),
        (project_root / "data/json/", "Répertoire JSON"),
        (project_root / "src/core/", "Répertoire core"),
        (project_root / "src/app/", "Répertoire app"),
        (project_root / "config/", "Répertoire config"),
    ]
    
    all_paths_ok = True
    for path, description in paths_to_check:
        if path.exists():
            print(f"✅ {description}: {path}")
        else:
            print(f"❌ {description} manquant: {path}")
            all_paths_ok = False
    
    if not all_paths_ok:
        print("⚠️ Certains chemins manquent, création...")
        for path, _ in paths_to_check:
            if not path.exists():
                if path.suffix:  # C'est un fichier
                    path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"  Créé répertoire parent pour: {path}")
                else:  # C'est un répertoire
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"  Créé répertoire: {path}")
    
    # 3. Vérification des fichiers JSON
    print("\n3. Vérification fichiers JSON...")
    json_dir = project_root / "data/json"
    if json_dir.exists():
        json_files = list(json_dir.glob("*.json"))
        if json_files:
            print(f"✅ {len(json_files)} fichiers JSON trouvés:")
            for json_file in json_files:
                print(f"  • {json_file.name}")
        else:
            print("⚠️ Aucun fichier JSON trouvé")
    else:
        print("❌ Répertoire JSON manquant")
    
    # 4. Vérification de la base de données
    print("\n4. Vérification base de données...")
    try:
        db = DatabaseManager()
        success = db.connect()
        
        if success:
            # Test requête simple
            try:
                result = db.execute_query("SELECT 1 as test")
                if not result.empty:
                    print(f"✅ Base de données accessible (shape: {result.shape})")
                    
                    # Liste des tables
                    try:
                        tables_result = db.execute_query(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                        if not tables_result.empty:
                            tables = tables_result['name'].tolist()
                            print(f"✅ Tables trouvées: {', '.join(tables)}")
                    except Exception as e:
                        print(f"⚠️ Impossible de lister les tables: {e}")
                else:
                    print("⚠️ Base de données retourne des résultats vides")
            except Exception as e:
                print(f"❌ Erreur requête test: {e}")
        else:
            print("❌ Impossible de se connecter à la base de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False
    
    # 5. Vérification NoSQL
    print("\n5. Vérification NoSQL...")
    try:
        nosql = NoSQLManager()
        nosql.load_all_json(sample_size=10)
        collections = nosql.get_available_collections()
        if collections:
            print(f"✅ {len(collections)} collections NoSQL chargées:")
            for collection in collections:
                doc_count = len(nosql.json_collections.get(collection, []))
                print(f"  • {collection}: {doc_count} documents")
        else:
            print("⚠️ Aucune collection NoSQL trouvée")
    except Exception as e:
        print(f"❌ Erreur NoSQL: {e}")
        return False
    
    # 6. Vérification IA
    print("\n6. Vérification IA...")
    try:
        ai = AIProvider()
        status = ai.get_status()
        print(f"✅ Fournisseur IA actif: {status.get('active_provider', 'Aucun')}")
        print(f"  Ollama: {'✅' if status.get('ollama') else '❌'}")
        print(f"  OpenAI: {'✅' if status.get('openai') else '❌'}")
        print(f"  Local: {'✅' if status.get('local') else '❌'}")
    except Exception as e:
        print(f"❌ Erreur IA: {e}")
        return False
    
    # 7. Test InsightBotGPT
    print("\n7. Test InsightBotGPT...")
    try:
        bot = InsightBotGPT()
        if bot.initialize():
            print("✅ InsightBotGPT initialisé avec succès")
            
            status = bot.get_status()
            print(f"  SQL: {'✅' if status['sql']['available'] else '❌'}")
            print(f"  NoSQL: {'✅' if status['nosql']['available'] else '❌'}")
            print(f"  IA: {status['ai']['active_provider']}")
        else:
            print("❌ Échec initialisation InsightBotGPT")
            return False
    except Exception as e:
        print(f"❌ Erreur InsightBotGPT: {e}")
        return False
    
    print("\n" + "="*50)
    print("🎉 VALIDATION COMPLÈTE ! Le système est prêt.")
    print("="*50)
    
    # Recommandations
    print("\n📋 Prochaines étapes:")
    print("1. Lancer l'application: streamlit run src/app/chat_ultimate_app.py")
    print("2. Vérifier que Ollama est démarré si vous voulez utiliser l'IA locale")
    print("3. Configurer votre clé OpenAI dans .env si besoin")
    
    return True

def check_ollama_status():
    """Vérifie le statut d'Ollama"""
    print("\n🔧 Vérification Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("✅ Ollama est démarré")
                print(f"📦 Modèles disponibles:")
                for model in models:
                    print(f"  • {model.get('name')}")
                return True
            else:
                print("⚠️ Ollama démarré mais aucun modèle chargé")
                return False
        else:
            print("❌ Ollama ne répond pas")
            return False
    except Exception as e:
        print(f"❌ Impossible de contacter Ollama: {e}")
        print("💡 Astuce: Lancez Ollama avec: ollama serve")
        return False

if __name__ == "__main__":
    print("="*50)
    print("InsightBot - Validation Système")
    print("="*50)
    
    # Vérification Ollama (optionnel)
    check_ollama = input("\nVoulez-vous vérifier Ollama? (o/n): ").lower() == 'o'
    if check_ollama:
        check_ollama_status()
    
    # Validation principale
    success = validate_system()
    sys.exit(0 if success else 1)