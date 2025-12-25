
"""
prompt_templates.py - PROMPTS CENTRALISÉS pour InsightBot

TOUTE la logique de rédaction des prompts est centralisée ici.
"""

import json
from typing import Dict, Any, List, Optional

# ============================================================================
# SYSTEM_PROMPT UNIQUE ET GLOBAL
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """Tu es InsightBot, expert en Business Intelligence SQL avec 10+ ans d'expérience.

## 🎯 MISSION PRINCIPALE
Analyser des données SQL pour générer des insights business actionnables.

## 🌍 GESTION MULTILINGUE
1. Détecte automatiquement la langue de l'utilisateur
2. Réponds TOUJOURS dans la même langue
3. Langues supportées : Français (FR), Anglais (EN), Darija/Arabe (AR)
4. Si ambigu, utilise le Français par défaut

## 🗂️ FOCUS EXCLUSIF SUR SQL
- Base de données : DuckDB
- Format : Tables relationnelles
- Pas d'analyse NoSQL/JSON dans cette version

## 📊 SCHÉMA SQL DISPONIBLE
{SQL_SCHEMA}

## 📈 STATISTIQUES GLOBALES
{SQL_STATISTICS}

## 🎨 FORMAT DE RÉPONSE OBLIGATOIRE
Tu DOIS répondre UNIQUEMENT avec ce format JSON :

```json
{{
    "sql_query": "SELECT ... (requête SQL valide pour DuckDB)",
    "insight": "Explication technique des données trouvées...",
    "visualization": {{
        "type": "bar|line|pie|table|scatter",
        "x": "nom_colonne_x",
        "y": "nom_colonne_y",
        "title": "Titre du graphique"
    }},
    "business_recommendations": [
        "Recommandation actionnable 1",
        "Recommandation actionnable 2", 
        "Recommandation actionnable 3"
    ]
}}
```

## 📋 RÈGLES STRICTES

### 1. REQUÊTE SQL (OBLIGATOIRE)
- Doit être valide pour DuckDB
- Utilise EXCLUSIVEMENT le schéma fourni
- Évite les sous-requêtes complexes si possible
- Limite les résultats à 1000 lignes maximum
- Protège contre les injections SQL

### 2. INSIGHT (EXPLICATION TECHNIQUE)
- Explique la méthodologie choisie
- Mentionne les tables et colonnes utilisées
- Signale les limitations éventuelles
- Ne montre pas de code SQL brut
- Sois concis mais précis

### 3. VISUALISATION (RECOMMANDÉE)
- **bar** : comparaisons catégories (produits, régions)
- **line** : tendances temporelles (ventes par mois)
- **pie** : répartitions pourcentages (part de marché)
- **table** : données détaillées multiples métriques
- **scatter** : corrélations entre variables

### 4. RECOMMANDATIONS BUSINESS (CRITIQUE)
Chaque recommandation doit être :
- **Actionnable** : étape concrète à réaliser
- **Mesurable** : avec indicateur chiffré
- **Temporalisée** : délai d'exécution
- **Priorisée** : impact vs effort

Structure recommandée :
1. 🚀 ACTION IMMÉDIATE (1-2 semaines)
2. 📈 INITIATIVE MOYEN TERME (1-3 mois)
3. 🏗️ TRANSFORMATION LONG TERME (3-12 mois)

## 🚨 CONTRAINTES TECHNIQUES
- DuckDB est sensible à la casse pour les noms avec espaces
- Utilise des guillemets doubles pour les colonnes avec espaces : "Nom Colonne"
- Les dates sont au format texte (à convertir si nécessaire)
- Certaines colonnes peuvent contenir des valeurs NULL

## 📝 EXEMPLES COMPLETS

### EXEMPLE 1 - Question FR : "Quels sont les produits les plus vendus ?"
```json
{{
    "sql_query": "SELECT \"Product Name\", SUM(Quantity) as total_quantity FROM merged GROUP BY \"Product Name\" ORDER BY total_quantity DESC LIMIT 10",
    "insight": "J'ai analysé les ventes historiques en groupant par nom de produit. Le top 10 représente 68% du volume total. Le produit 'MacBook Pro' domine avec 15% des ventes.",
    "visualization": {{
        "type": "bar",
        "x": "Product Name",
        "y": "total_quantity",
        "title": "Top 10 produits par quantité vendue"
    }},
    "business_recommendations": [
        "🚀 Augmenter le stock des 3 premiers produits de 20% pour éviter les ruptures (impact: +15% satisfaction client)",
        "📈 Créer des bundles avec produits complémentaires pour booster le panier moyen de 25%",
        "🏗️ Implémenter un système de prévision des ventes basé sur l'historique saisonnier"
    ]
}}
```

### EXEMPLE 2 - Question EN : "How are sales distributed by region?"
```json
{{
    "sql_query": "SELECT Region, SUM(Sales) as total_sales FROM merged GROUP BY Region ORDER BY total_sales DESC",
    "insight": "I analyzed sales data grouped by region. Central region leads with 38% of total revenue ($1.2M). West region shows highest growth at +22% YoY.",
    "visualization": {{
        "type": "pie",
        "x": "Region",
        "y": "total_sales",
        "title": "Sales Distribution by Region"
    }},
    "business_recommendations": [
        "🚀 Increase marketing budget in West region by 15% to capitalize on growth momentum",
        "📈 Open new distribution center in Central region to reduce logistics costs by 12%",
        "🏗️ Replicate North region's high-value customer strategy across all regions"
    ]
}}
```

### EXEMPLE 3 - Question AR : "ما هي أفضل المنتجات مبيعًا؟"
```json
{{
    "sql_query": "SELECT \"Product Name\", SUM(Sales) as total_sales FROM merged GROUP BY \"Product Name\" ORDER BY total_sales DESC LIMIT 5",
    "insight": "قمت بتحليل بيانات المبيعات مجمعة حسب اسم المنتج. المنتجات الخمسة الأولى تمثل 45% من إجمالي المبيعات.",
    "visualization": {{
        "type": "bar",
        "x": "Product Name",
        "y": "total_sales",
        "title": "أفضل 5 منتجات حسب المبيعات"
    }},
    "business_recommendations": [
        "🚀 زيادة مخزون أفضل منتجين بنسبة 25%",
        "📈 خصم 10% على المنتجات الأقل مبيعًا لتعزيز الطلب",
        "🏗️ دراسة سلوك الشراء حسب المنطقة لتحسين التوزيع"
    ]
}}
```

## ❓ QUESTION À ANALYSER
{USER_QUESTION}

## ✅ INSTRUCTION FINALE
1. Sois concis mais complet
2. Fournis des chiffres concrets dans l'insight
3. Les recommandations doivent être précises et mesurables
4. Évite le jargon technique excessif
5. Respecte scrupuleusement le format JSON
6. Réponds impérativement en {LANGUAGE}
"""

# ============================================================================
# FONCTIONS D'AIDE POUR LE FORMATAGE
# ============================================================================

def format_sql_schema(columns: List[Dict[str, Any]]) -> str:
    """Formate le schéma SQL pour l'inclusion dans le prompt"""
    if not columns:
        return "⚠️ Aucun schéma SQL disponible"
    
    # Grouper par table
    tables = {}
    for col in columns:
        table = col.get("table", "unknown")
        if table not in tables:
            tables[table] = []
        
        column_info = f"- {col.get('column', 'unknown')}"
        col_type = col.get('type', 'unknown')
        if col_type and col_type != 'unknown':
            column_info += f" ({col_type})"
        
        tables[table].append(column_info)
    
    # Construire la représentation
    schema_parts = []
    for table_name, table_columns in tables.items():
        schema_parts.append(f"📌 Table: {table_name}")
        schema_parts.extend(table_columns[:8])  # Limiter à 8 colonnes par table
        if len(table_columns) > 8:
            schema_parts.append(f"  ... et {len(table_columns) - 8} autres colonnes")
        schema_parts.append("")  # Ligne vide
    
    return "\n".join(schema_parts)


def format_sql_statistics(stats: Dict[str, Any]) -> str:
    """Formate les statistiques SQL pour l'inclusion dans le prompt"""
    if not stats:
        return "⚠️ Aucune statistique disponible"
    
    stat_parts = []
    
    # Statistiques principales
    if 'total_rows' in stats:
        stat_parts.append(f"📊 Lignes totales: {stats['total_rows']:,}")
    
    if 'total_sales' in stats:
        stat_parts.append(f"💰 Chiffre d'affaires: ${stats['total_sales']:,.2f}")
    
    if 'total_profit' in stats:
        stat_parts.append(f"📈 Profit total: ${stats['total_profit']:,.2f}")
    
    if 'return_rate' in stats:
        stat_parts.append(f"🔄 Taux de retour: {stats['return_rate']:.1f}%")
    
    if 'unique_customers' in stats:
        stat_parts.append(f"👥 Clients uniques: {stats['unique_customers']:,}")
    
    if 'column_count' in stats:
        stat_parts.append(f"🗂️ Colonnes disponibles: {stats['column_count']}")
    
    return "\n".join(stat_parts)


def detect_language(text: str) -> str:
    """Détecte la langue du texte (FR, EN, AR)"""
    if not text:
        return 'fr'
    
    # Détection arabe/darija
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return 'ar'
    
    text_lower = text.lower()
    
    # Mots-clés français
    french_keywords = ['le', 'la', 'les', 'de', 'des', 'du', 'est', 'dans', 'avec', 'pour', 'quel', 'quelle', 'quels', 'quelles']
    french_count = sum(1 for word in french_keywords if word in text_lower.split())
    
    # Mots-clés anglais
    english_keywords = ['the', 'and', 'for', 'with', 'what', 'how', 'why', 'when', 'which', 'who', 'where']
    english_count = sum(1 for word in english_keywords if word in text_lower.split())
    
    if french_count > english_count:
        return 'fr'
    elif english_count > french_count:
        return 'en'
    else:
        # Analyse de caractères supplémentaires
        if 'é' in text or 'è' in text or 'ê' in text or 'à' in text:
            return 'fr'
        elif any(c in text for c in ['ü', 'ö', 'ä']):  # Caractères allemands
            return 'en'  # Traiter comme anglais par défaut
        else:
            return 'fr'  # Français par défaut


def get_language_name(lang_code: str) -> str:
    """Retourne le nom complet de la langue"""
    languages = {
        'fr': 'Français',
        'en': 'Anglais',
        'ar': 'Arabe/Darija'
    }
    return languages.get(lang_code, 'Français')


# ============================================================================
# FONCTION PRINCIPALE DE CRÉATION DE PROMPT
# ============================================================================

def create_analysis_prompt(
    question: str,
    sql_columns: List[Dict[str, Any]],
    sql_statistics: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Crée un prompt complet d'analyse avec injection dynamique du schéma SQL
    
    Args:
        question: Question de l'utilisateur
        sql_columns: Liste des colonnes SQL disponibles
        sql_statistics: Statistiques SQL
        context: Contexte supplémentaire (optionnel)
    
    Returns:
        Dictionnaire avec system_prompt et user_prompt
    """
    
    # 1. Détection de la langue
    language = detect_language(question)
    
    # 2. Formatage du schéma SQL
    formatted_schema = format_sql_schema(sql_columns)
    
    # 3. Formatage des statistiques
    formatted_stats = format_sql_statistics(sql_statistics)
    
    # 4. Préparation des variables de template
    template_vars = {
        "SQL_SCHEMA": formatted_schema,
        "SQL_STATISTICS": formatted_stats,
        "USER_QUESTION": question,
        "LANGUAGE": get_language_name(language)
    }
    
    # 5. Ajout du contexte si fourni
    if context:
        template_vars.update(context)
    
    # 6. Génération du system_prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(**template_vars)
    
    # 7. User prompt simple (l'IA utilise le system_prompt pour le contexte)
    user_prompt = f"Question ({template_vars['LANGUAGE']}): {question}"
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "language": language,
        "template_vars": template_vars
    }


# ============================================================================
# FONCTIONS SPÉCIALISÉES (pour usage futur)
# ============================================================================

def create_sql_correction_prompt(
    broken_query: str,
    error_message: str,
    sql_schema: str,
    original_question: str,
    language: str = "fr"
) -> Dict[str, str]:
    """Crée un prompt pour corriger une requête SQL"""
    
    translations = {
        "fr": {
            "task": "Corrige la requête SQL suivante qui a échoué avec l'erreur indiquée.",
            "rules": "Règles :",
            "rules_list": [
                "Fournis UNIQUEMENT la requête SQL corrigée",
                "Pas d'explication supplémentaire",
                "La requête doit être valide pour DuckDB",
                "Utilise le schéma fourni"
            ],
            "error": "Erreur :",
            "original": "Question originale :",
            "schema": "Schéma disponible :"
        },
        "en": {
            "task": "Correct the following SQL query that failed with the indicated error.",
            "rules": "Rules:",
            "rules_list": [
                "Provide ONLY the corrected SQL query",
                "No additional explanation",
                "Query must be valid for DuckDB",
                "Use the provided schema"
            ],
            "error": "Error:",
            "original": "Original question:",
            "schema": "Available schema:"
        },
        "ar": {
            "task": "صحح استعلام SQL التالي الذي فشل مع الخطأ المحدد.",
            "rules": "القواعد:",
            "rules_list": [
                "قدم فقط استعلام SQL المصحح",
                "بدون شرح إضافي",
                "يجب أن يكون الاستعلام صالحًا لـ DuckDB",
                "استخدم المخطط المقدم"
            ],
            "error": "الخطأ:",
            "original": "السؤال الأصلي:",
            "schema": "المخطط المتاح:"
        }
    }
    
    trans = translations.get(language, translations["fr"])
    
    system_prompt = f"""Tu es un expert SQL spécialisé dans DuckDB.

{trans['task']}

{trans['rules']}
{chr(10).join(f"- {rule}" for rule in trans['rules_list'])}

{trans['error']}
{error_message}

{trans['original']}
{original_question}

{trans['schema']}
{sql_schema}

Réponds UNIQUEMENT avec la requête SQL corrigée, sans texte supplémentaire."""

    user_prompt = broken_query
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "language": language
    }


def create_business_summary_prompt(
    query_results: Dict[str, Any],
    original_question: str,
    language: str = "fr"
) -> Dict[str, str]:
    """Crée un prompt pour résumer les résultats business"""
    
    translations = {
        "fr": {
            "task": "Résume les résultats suivants en insights business actionnables.",
            "data_info": "Résultats de la requête :",
            "original": "Question originale :",
            "format": "Format de réponse :"
        },
        "en": {
            "task": "Summarize the following results into actionable business insights.",
            "data_info": "Query results:",
            "original": "Original question:",
            "format": "Response format:"
        },
        "ar": {
            "task": "لخص النتائج التالية في رؤى عمل قابلة للتنفيذ.",
            "data_info": "نتائج الاستعلام:",
            "original": "السؤال الأصلي:",
            "format": "تنسيق الرد:"
        }
    }
    
    trans = translations.get(language, translations["fr"])
    
    # Formater les résultats
    data_summary = ""
    if query_results.get("data"):
        data = query_results["data"]
        if hasattr(data, "head"):  # DataFrame
            data_summary = f"Dimensions: {data.shape[0]} lignes × {data.shape[1]} colonnes\n"
            data_summary += f"Colonnes: {', '.join(data.columns.tolist()[:5])}"
            if len(data.columns) > 5:
                data_summary += f"... (+{len(data.columns) - 5} autres)"
    
    system_prompt = f"""Tu es InsightBot, expert en analyse business.

{trans['task']}

{trans['original']}
{original_question}

{trans['data_info']}
{data_summary}

{trans['format']}
- Insight principal (1-2 phrases)
- 3 recommandations actionnables
- 1 indicateur clé à surveiller

Réponds en {language}."""

    user_prompt = f"Résume ces données pour une audience business."
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "language": language
    }


# ============================================================================
# FONCTIONS DE TEST
# ============================================================================

def test_prompt_generation():
    """Teste la génération de prompts"""
    
    print("🧪 Test de génération de prompts centralisés")
    print("=" * 60)
    
    # Données de test
    test_columns = [
        {"table": "merged", "column": "Product Name", "type": "VARCHAR"},
        {"table": "merged", "column": "Sales", "type": "DOUBLE"},
        {"table": "merged", "column": "Profit", "type": "DOUBLE"},
        {"table": "merged", "column": "Region", "type": "VARCHAR"},
        {"table": "merged", "column": "Category", "type": "VARCHAR"},
        {"table": "merged", "column": "Order Date", "type": "VARCHAR"},
        {"table": "orders", "column": "Order ID", "type": "VARCHAR"},
        {"table": "orders", "column": "Customer ID", "type": "VARCHAR"}
    ]
    
    test_stats = {
        "total_rows": 15000,
        "total_sales": 1250000.50,
        "total_profit": 250000.75,
        "return_rate": 5.2,
        "unique_customers": 4500,
        "column_count": 42
    }
    
    test_questions = [
        "Quels sont les produits les plus vendus ?",
        "How are sales distributed by region?",
        "ما هي أفضل المنتجات مبيعًا؟",
        "Analyse des retours par catégorie de produit",
        "Quelle est l'évolution des ventes sur les 6 derniers mois ?"
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n{'='*60}")
        print(f"Test {i+1}: {question}")
        
        prompt = create_analysis_prompt(
            question=question,
            sql_columns=test_columns,
            sql_statistics=test_stats
        )
        
        print(f"Langue détectée: {prompt['language']}")
        print(f"Taille system_prompt: {len(prompt['system_prompt'])} caractères")
        print(f"Taille user_prompt: {len(prompt['user_prompt'])} caractères")
        
        # Aperçu
        print("\nAperçu du system_prompt:")
        print("-" * 40)
        lines = prompt['system_prompt'].split('\n')
        for line in lines[:15]:  # Premières 15 lignes
            print(line)
        print("...")
        print("-" * 40)

# À la fin de src/core/prompt_templates.py

class PromptTemplates:
    """Classe de secours pour regrouper les fonctions de prompt"""
    @staticmethod
    def create_analysis_prompt(*args, **kwargs):
        return create_analysis_prompt(*args, **kwargs)
    
    @staticmethod
    def create_sql_correction_prompt(*args, **kwargs):
        return create_sql_correction_prompt(*args, **kwargs)
    
    @staticmethod
    def create_business_summary_prompt(*args, **kwargs):
        return create_business_summary_prompt(*args, **kwargs)
    
    def test_prompt_generation(*args, **kwargs):
        return test_prompt_generation(*args, **kwargs)

# Cela permet au bot de faire PromptTemplates.create_analysis_prompt() sans erreur.
if __name__ == "__main__":
    test_prompt_generation()
    print("\n✅ Tests terminés avec succès !")




