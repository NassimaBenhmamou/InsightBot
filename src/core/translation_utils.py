# core/translation_utils.py

TRANSLATION_MAP = {
    'fr': {
        'Sales': 'Ventes',
        'Profit': 'Profit',
        'Category': 'Catégorie',
        'Region': 'Région',
        'Market': 'Marché',
        'Order Date': 'Date de Commande',
        'total_sales': 'Ventes Totales',
        'total_profit': 'Profit Total',
        'monthly_sales': 'Ventes Mensuelles',
        'monthly_profit': 'Profit Mensuel',
        'return_rate': 'Taux de Retour',
        'avg_margin': 'Marge Moyenne',
        'Region': 'Région',
        'Segment': 'Segment',
        'Quantity': 'Quantité',
        'Discount': 'Remise',
        'Profit_Margin_Percent': 'Pourcentage de Marge',
        'Is_Returned': 'Retourné',
        'Product Name': 'Nom du Produit',
        'Customer Name': 'Nom du Client',
        'Order_YearMonth': 'Année-Mois',
        'Processing_Days': 'Jours de Traitement',
        # Nouveaux termes business
        'Revenue': 'Revenus',
        'Cost': 'Coût',
        'Margin': 'Marge',
        'Growth': 'Croissance',
        'Trend': 'Tendance',
        'Performance': 'Performance',
        'Efficiency': 'Efficacité',
        'Optimization': 'Optimisation',
        'Strategy': 'Stratégie',
        'Analysis': 'Analyse',
        'Insights': 'Insights',
        'KPIs': 'KPIs',
        'Metrics': 'Métriques',
        'Benchmark': 'Référence',
        'Target': 'Objectif',
        'Goal': 'But',
        'ROI': 'ROI',
        'Conversion': 'Conversion',
        'Retention': 'Rétention',
        'Churn': 'Attrition',
        'LTV': 'VL',
        'CAC': 'CAC',
        'CLV': 'VC',
        'Segmentation': 'Segmentation',
        'Clustering': 'Clustering',
        'Forecasting': 'Prévision',
        'Prediction': 'Prédiction'
    },
    'en': {
        # Anglais (base) - garder les mêmes noms
        'Sales': 'Sales',
        'Profit': 'Profit',
        'Category': 'Category',
        'Region': 'Region',
        'Market': 'Market',
        'total_sales': 'Total Sales',
        'total_profit': 'Total Profit',
        'monthly_sales': 'Monthly Sales',
        'monthly_profit': 'Monthly Profit',
        'return_rate': 'Return Rate'
    },
    'ar': {
        'Sales': 'المبيعات',
        'Profit': 'الربح',
        'Category': 'الفئة',
        'Region': 'المنطقة',
        'Market': 'السوق',
        'total_sales': 'إجمالي المبيعات',
        'total_profit': 'إجمالي الربح',
        'monthly_sales': 'المبيعات الشهرية',
        'monthly_profit': 'الربح الشهري',
        'return_rate': 'معدل الإرجاع',
        # Nouveaux termes en arabe
        'Revenue': 'الإيرادات',
        'Cost': 'التكلفة',
        'Margin': 'الهامش',
        'Growth': 'النمو',
        'Trend': 'الاتجاه',
        'Performance': 'الأداء',
        'Efficiency': 'الكفاءة',
        'Optimization': 'التحسين',
        'Strategy': 'الاستراتيجية',
        'Analysis': 'التحليل',
        'Insights': 'الرؤى',
        'KPIs': 'المؤشرات الرئيسية',
        'Metrics': 'المقاييس',
        'Benchmark': 'المعيار المرجعي',
        'Target': 'الهدف',
        'Goal': 'الغاية',
        'ROI': 'عائد الاستثمار',
        'Conversion': 'التحويل',
        'Retention': 'الاحتفاظ',
        'Churn': 'التسرب',
        'LTV': 'قيمة العمر',
        'CAC': 'تكلفة الاكتساب',
        'CLV': 'قيمة العميل',
        'Segmentation': 'التجزئة',
        'Clustering': 'التجميع',
        'Forecasting': 'التنبؤ',
        'Prediction': 'التنبؤ'
    }
}

def translate_label(label: str, target_lang: str) -> str:
    """Traduit un label (colonne ou métrique) dans la langue cible."""
    if target_lang not in TRANSLATION_MAP:
        target_lang = 'en'
    
    lang_map = TRANSLATION_MAP.get(target_lang, TRANSLATION_MAP['en'])
    
    # Essayer de trouver la traduction exacte d'abord
    if label in lang_map:
        return lang_map[label]
    
    # Essayer de trouver par correspondance partielle (insensible à la casse)
    label_lower = label.lower()
    for key, value in lang_map.items():
        if key.lower() == label_lower:
            return value
    
    # Si aucune traduction trouvée, retourner le label original
    return label

def translate_column_names(df, target_lang: str):
    """Traduit les noms de colonnes d'un DataFrame."""
    if target_lang == 'en':
        return df
    
    df_translated = df.copy()
    new_columns = []
    
    for col in df.columns:
        translated_col = translate_label(str(col), target_lang)
        new_columns.append(translated_col)
    
    df_translated.columns = new_columns
    return df_translated

def detect_language(text: str) -> str:
    """Détection basique de la langue pour l'UI."""
    text_lower = text.lower()
    
    # Détection de l'arabe (caractères arabes)
    arabic_chars = any('\u0600' <= char <= '\u06FF' for char in text)
    if arabic_chars:
        return 'ar'
    
    # Détection du français (mots courants français)
    french_keywords = ['ventes', 'profit', 'montre', 'quels', 'comment', 'quelle', 'quelles', 'dans', 'pour', 'avec', 'les', 'des', 'une']
    if any(keyword in text_lower for keyword in french_keywords):
        return 'fr'
    
    # Détection de l'anglais (mots courants anglais)
    english_keywords = ['sales', 'profit', 'show', 'what', 'how', 'which', 'for', 'with', 'the', 'a', 'an']
    if any(keyword in text_lower for keyword in english_keywords):
        return 'en'
    
    # Par défaut : anglais
    return 'en'

def get_chart_labels(chart_type: str, target_lang: str) -> dict:
    """Retourne les labels pour les graphiques dans la langue cible."""
    labels = {
        'fr': {
            'bar': 'Diagramme à Barres',
            'line': 'Graphique Linéaire',
            'pie': 'Camembert',
            'table': 'Tableau',
            'kpi': 'Indicateur Clé'
        },
        'en': {
            'bar': 'Bar Chart',
            'line': 'Line Chart',
            'pie': 'Pie Chart',
            'table': 'Table',
            'kpi': 'KPI'
        },
        'ar': {
            'bar': 'مخطط شريطي',
            'line': 'مخطط خطي',
            'pie': 'مخطط دائري',
            'table': 'جدول',
            'kpi': 'مؤشر رئيسي'
        }
    }
    
    lang_labels = labels.get(target_lang, labels['en'])
    return {
        'chart_type': lang_labels.get(chart_type, chart_type),
        'x_axis': translate_label('X', target_lang),
        'y_axis': translate_label('Y', target_lang)
    }