# 🤖 InsightBot - Assistant d'Analyse Business Intelligence

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Transformez vos questions en insights actionnables avec l'IA**

[Fonctionnalités](#-fonctionnalités) • [Installation](#-installation) • [Utilisation](#-utilisation) • [Structure](#-structure-du-projet)

</div>

## 🎯 Présentation

**InsightBot** est un assistant intelligent qui combine l'IA (OpenAI GPT) et l'analyse de données pour transformer vos questions en langage naturel en insights business visuels et actionnables.

### ✨ Ce que fait InsightBot
- **🤖 Comprend** vos questions en français naturel
- **📊 Analyse** automatiquement vos données e-commerce
- **📈 Génère** des graphiques interactifs
- **💡 Produit** des insights business intelligents
- **💬 Interface** conversationnelle intuitive

## 🚀 Fonctionnalités

### 🔍 Analyse Avancée
| Fonctionnalité | Description |
|---------------|-------------|
| 📊 **Tableau de bord** | KPIs en temps réel avec métriques business |
| 📈 **Visualisations** | Graphiques interactifs (barres, lignes, camemberts) |
| 🔄 **Analyse temporelle** | Tendances et évolutions mensuelles |
| 💰 **Profitabilité** | Analyse par catégorie, région et produit |
| 📉 **Performance** | Taux de retour et analyse par marché |

### 🤖 Intelligence Artificielle
| Composant | Avantage |
|-----------|----------|
| 🧠 **GPT intégré** | Compréhension du langage naturel avancée |
| 🗣️ **SQL automatique** | Génération de requêtes depuis vos questions |
| 💡 **Insights contextuels** | Analyses intelligentes et actionnables |
| 📋 **Suggestions** | Questions pertinentes suggérées |

### 🛠️ Features Techniques
| Technologie | Bénéfice |
|-------------|----------|
| 🗄️ **DuckDB** | Base de données haute performance |
| 🎨 **Streamlit** | Interface moderne et responsive |
| 📁 **Processing auto** | Nettoyage et préparation automatique des données |
| 🔒 **Environnement sécurisé** | Variables d'environnement pour les clés API |

## 📦 Installation

### Prérequis
- 🐍 **Python 3.8 à 3.11** (Éviter Python 3.12 pour l'instant en raison de problèmes de compatibilité des bibliothèques)
- 📦 **Git**
- 🌐 **Connexion Internet** (pour OpenAI GPT)

### 🛠️ Installation Pas à Pas

```bash
# 1. Cloner le repository
git clone https://github.com/NassimaBenhmamou/InsightBot.git
cd InsightBot

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur Mac/Linux:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt
```

### ⚙️ Configuration

1. **Créez un fichier `.env`** à la racine du projet :
```env
OPENAI_API_KEY=sk-votre-cle-api-openai-ici
```

2. **Obtenez une clé API OpenAI** :
   - Allez sur [OpenAI Platform](https://platform.openai.com)
   - Créez un compte et générez une clé API
   - Collez-la dans le fichier `.env`

## 🎮 Utilisation

### 🚀 Lancement Rapide

```bash
# 1. Préparer les données (première fois seulement)
python src/core/data_processor.py

# 2. Créer la base de données
python src/core/database_manager.py

# 3. Lancer l'application principale
streamlit run src/app/streamlit_app.py
```

### 💬 Comment utiliser InsightBot

1. **Lancez l'application** : L'interface s'ouvre dans votre navigateur
2. **Posez une question** comme :
   - *"Quelles sont les ventes par région ?"*
   - *"Comment évolue le profit par catégorie ?"*
   - *"Quel est le taux de retour par marché ?"*
3. **Obtenez instantanément** :
   - 📊 Un graphique interactif
   - 💡 Un insight business intelligent
   - 📈 Les données sous forme de tableau

### 🎯 Exemples de Questions

| Type d'analyse | Question exemple |
|----------------|------------------|
| **Ventes** | "Quelles sont les ventes par région ?" |
| **Profit** | "Quel est le profit par catégorie ?" |
| **Tendances** | "Comment évoluent les ventes dans le temps ?" |
| **Performance** | "Quels sont les produits les plus rentables ?" |
| **Clients** | "Qui sont les clients les plus fidèles ?" |

## 📊 Structure du Projet

```
insightbot/
├── 📁 data/                         # Données et base de données
│   ├── 📁 raw/                      # Données brutes originales
│   ├── 📁 processed/                # Données nettoyées et transformées
│   └── 📁 database/                 # Base de données DuckDB
├── 📁 src/                          # Code source
│   ├── 📁 core/                     # Cœur de l'application
│   │   ├── 🐍 database_manager.py   # Gestion base de données
│   │   ├── 🐍 data_processor.py     # Traitement des données
│   │   └── 🐍 insightbot_ai.py      # Intelligence artificielle
│   ├── 📁 app/                      # Applications
│   │   └── 🐍 streamlit_app.py      # Interface utilisateur
│   └── 📁 utils/                    # Utilitaires
├── 📄 requirements.txt              # Dépendances Python
├── 📄 .env.example                  # Exemple de configuration
└── 📄 README.md                     # Cette documentation
```

## 🔧 Développement

### 🛠️ Commandes de Développement

```bash
# Exécuter les tests
python -m pytest src/tests/

# Vérifier la qualité du code
flake8 src/

# Formatter le code
black src/

# Mettre à jour les dépendances
pip freeze > requirements.txt
```

### 📋 Workflow Git

```bash
# Contribuer au projet
git checkout -b feature/ma-nouvelle-fonctionnalite
git add .
git commit -m "feat: ajout de la nouvelle fonctionnalité"
git push origin feature/ma-nouvelle-fonctionnalite
```

## 🐛 Dépannage

### Problèmes Courants

| Problème | Solution |
|----------|----------|
| **Module non trouvé** | `pip install -r requirements.txt` |
| **Erreur API OpenAI** | Vérifiez votre clé dans `.env` |
| **Données non chargées** | Exécutez `data_processor.py` d'abord |
| **Port déjà utilisé** | `streamlit run app.py --server.port 8502` |

### 📚 Ressources Utiles
- [Documentation Streamlit](https://docs.streamlit.io)
- [Documentation OpenAI](https://platform.openai.com/docs)
- [Documentation DuckDB](https://duckdb.org/docs/)

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. 🍴 Fork le projet
2. 🌿 Créez votre branche feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push sur la branche (`git push origin feature/AmazingFeature`)
5. 🔃 Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **Nassima Benhmamou** - *Développeuse principale* - [GitHub](https://github.com/NassimaBenhmamou)
- **Sanae Achahboun** - *Développeuse principale* - [GitHub](https://github.com/Achahboun-Sanae)

## 🙏 Remerciements

- [OpenAI](https://openai.com) pour l'API GPT
- [Streamlit](https://streamlit.io) pour l'interface utilisateur
- [DuckDB](https://duckdb.org) pour la base de données performante

---

<div align="center">



</div>