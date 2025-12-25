"""
Script de configuration de l'environnement InsightBot
"""
import sys
import os
from pathlib import Path
import subprocess

def setup_environment():
    """Configure l'environnement du projet"""
    print("🔧 Configuration de l'environnement InsightBot...")
    
    # 1. Déterminer le répertoire racine
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    print(f"📁 Répertoire projet: {project_root}")
    
    # 2. Créer la structure de répertoires
    directories = [
        project_root / "data/database",
        project_root / "data/json",
        project_root / "data/raw",
        project_root / "data/processed",
        project_root / "logs",
        project_root / "exports"
    ]
    
    print("\n📂 Création de la structure de répertoires...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory.relative_to(project_root)}")
    
    # 3. Vérifier l'environnement virtuel
    print("\n🐍 Vérification de l'environnement virtuel...")
    venv_dir = project_root / ".venv"
    
    if venv_dir.exists():
        print(f"  ✅ Environnement virtuel trouvé: {venv_dir}")
    else:
        print("  ⚠️ Environnement virtuel non trouvé")
        create_venv = input("  Créer un environnement virtuel? (o/n): ").lower() == 'o'
        if create_venv:
            try:
                subprocess.run([sys.executable, "-m", "venv", ".venv"], 
                             cwd=project_root, check=True)
                print("  ✅ Environnement virtuel créé")
            except Exception as e:
                print(f"  ❌ Erreur création venv: {e}")
    
    # 4. Vérifier les dépendances
    print("\n📦 Vérification des dépendances...")
    requirements_file = project_root / "requirements.txt"
    
    if requirements_file.exists():
        print(f"  ✅ Fichier requirements trouvé")
        
        # Liste des packages requis
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"  📋 {len(packages)} packages requis")
        
        install = input("  Installer/rafraîchir les dépendances? (o/n): ").lower() == 'o'
        if install:
            try:
                # Utiliser pip du venv s'il existe
                pip_executable = venv_dir / "Scripts" / "pip.exe" if os.name == 'nt' else venv_dir / "bin" / "pip"
                
                if pip_executable.exists():
                    subprocess.run([str(pip_executable), "install", "-r", "requirements.txt"], 
                                 cwd=project_root, check=True)
                    print("  ✅ Dépendances installées")
                else:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                 cwd=project_root, check=True)
                    print("  ✅ Dépendances installées (pip système)")
            except Exception as e:
                print(f"  ❌ Erreur installation: {e}")
    else:
        print("  ⚠️ Fichier requirements.txt non trouvé")
        create_req = input("  Créer un fichier requirements.txt par défaut? (o/n): ").lower() == 'o'
        if create_req:
            default_requirements = """streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
duckdb>=0.9.0
requests>=2.31.0
pyyaml>=6.0
python-dotenv>=1.0.0
faker>=20.0.0
"""
            with open(requirements_file, 'w') as f:
                f.write(default_requirements)
            print("  ✅ Fichier requirements.txt créé")
    
    # 5. Configurer le fichier .env
    print("\n🔐 Configuration des variables d'environnement...")
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("  ⚠️ Fichier .env non trouvé")
        create_env = input("  Créer un fichier .env par défaut? (o/n): ").lower() == 'o'
        if create_env:
            default_env = """# Configuration InsightBot

# Base de données
DB_PATH=data/database/insightbot.db

# OpenAI (optionnel)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Application
DEBUG=False
CACHE_TTL=300
MAX_HISTORY=50

# Langue par défaut
DEFAULT_LANGUAGE=fr
"""
            with open(env_file, 'w') as f:
                f.write(default_env)
            print("  ✅ Fichier .env créé")
            print("  ⚠️ N'oubliez pas de configurer votre clé OpenAI si besoin")
    else:
        print("  ✅ Fichier .env trouvé")
    
    # 6. Vérifier la configuration
    print("\n⚙️ Vérification de la configuration...")
    config_file = project_root / "config" / "settings.py"
    
    if config_file.exists():
        print("  ✅ Fichier de configuration trouvé")
    else:
        print("  ⚠️ Fichier de configuration manquant")
    
    # 7. Exemple de données
    print("\n📊 Vérification des données d'exemple...")
    json_dir = project_root / "data/json"
    json_files = list(json_dir.glob("*.json"))
    
    if json_files:
        print(f"  ✅ {len(json_files)} fichiers JSON trouvés")
    else:
        print("  ⚠️ Aucun fichier JSON trouvé")
        create_samples = input("  Créer des fichiers JSON d'exemple? (o/n): ").lower() == 'o'
        if create_samples:
            create_sample_json_files(json_dir)
    
    print("\n" + "="*50)
    print("🎉 CONFIGURATION TERMINÉE !")
    print("="*50)
    
    print("\n📋 Prochaines étapes:")
    print("1. Activez l'environnement virtuel:")
    print("   Windows: .venv\\Scripts\\activate")
    print("   Mac/Linux: source .venv/bin/activate")
    print("2. Lancez la validation: python scripts/validate_system.py")
    print("3. Démarrez l'application: streamlit run src/app/chat_ultimate_app.py")
    
    return True

def create_sample_json_files(json_dir):
    """Crée des fichiers JSON d'exemple"""
    import json
    
    # Produits
    products = [
        {
            "id": "P001",
            "name": "Ordinateur Portable Pro",
            "category": "Électronique",
            "price": 1299.99,
            "stock": 15,
            "brand": "TechCorp"
        },
        {
            "id": "P002",
            "name": "Smartphone Elite",
            "category": "Téléphonie",
            "price": 899.99,
            "stock": 25,
            "brand": "PhoneMaster"
        }
    ]
    
    # Utilisateurs
    users = [
        {
            "id": "U001",
            "name": "Jean Dupont",
            "email": "jean@example.com",
            "location": "Paris",
            "subscription": "premium"
        },
        {
            "id": "U002",
            "name": "Marie Martin",
            "email": "marie@example.com",
            "location": "Lyon",
            "subscription": "basic"
        }
    ]
    
    # Commandes
    orders = [
        {
            "order_id": "ORD001",
            "user_id": "U001",
            "date": "2024-01-15",
            "total": 1299.99,
            "status": "delivered"
        }
    ]
    
    # Sauvegarder
    files = {
        "products.json": products,
        "users.json": users,
        "orders.json": orders
    }
    
    for filename, data in files.items():
        filepath = json_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Créé: {filename}")

if __name__ == "__main__":
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n\n⚠️ Configuration interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de la configuration: {e}")
        sys.exit(1)