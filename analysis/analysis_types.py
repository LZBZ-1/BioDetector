import pandas as pd
from itertools import combinations


def analyze_resistance_patterns(df):
    """
    Analiza patrones de resistencia antibiótica
    """
    print("\nAnálisis de Resistencia Antibiótica:")
    print("=" * 50)

    # 1. Análisis de antibióticos mencionados
    all_antibiotics = []
    for antibiotics in df['antibiotics']:
        all_antibiotics.extend(antibiotics)

    antibiotic_freq = pd.Series(all_antibiotics).value_counts()

    print("\n1. Antibióticos más frecuentemente estudiados:")
    print(antibiotic_freq.head().to_string())

    # 2. Análisis temporal de resistencia mejorado
    df['year'] = pd.to_numeric(df['date'])
    # Asegurar que tenemos todos los años en el rango
    year_range = range(df['year'].min(), df['year'].max() + 1)
    yearly_studies = df['year'].value_counts().reindex(year_range, fill_value=0).sort_index()

    # 3. Análisis geográfico
    print("\n3. Distribución geográfica de estudios:")
    print(df['country'].value_counts().head().to_string())

    # 4. Análisis de patrones de resistencia
    print("\n4. Patrones de resistencia más comunes:")
    resistance_patterns = []
    for patterns in df['resistance_patterns']:
        resistance_patterns.extend(patterns)

    if resistance_patterns:
        pattern_freq = pd.Series(resistance_patterns).value_counts()
        print(pattern_freq.head().to_string())

    return {
        'antibiotic_freq': antibiotic_freq,
        'yearly_studies': yearly_studies,
        'pattern_freq': pattern_freq if resistance_patterns else None
    }


def analyze_multi_resistance(df):
    """
    Analiza patrones de multi-resistencia en las publicaciones
    """
    multi_resistance = []
    for _, row in df.iterrows():
        if len(row['antibiotics']) > 2:  # Consideramos multi-resistencia si hay más de 2 antibióticos
            resistance_data = {
                'pmid': row['pmid'],
                'num_antibiotics': len(row['antibiotics']),
                'antibiotics': row['antibiotics'],
                'country': row['country'],
                'year': row['date']
            }
            multi_resistance.append(resistance_data)

    return pd.DataFrame(multi_resistance)


def analyze_antibiotic_cooccurrence(df):
    """
    Analiza qué antibióticos tienden a aparecer juntos en los estudios
    """

    cooccurrences = {}
    for antibiotics in df['antibiotics']:
        if len(antibiotics) > 1:
            for pair in combinations(sorted(antibiotics), 2):
                if pair in cooccurrences:
                    cooccurrences[pair] += 1
                else:
                    cooccurrences[pair] = 1

    return pd.DataFrame([
        {'antibiotic_1': pair[0],
         'antibiotic_2': pair[1],
         'count': count}
        for pair, count in cooccurrences.items()
    ]).sort_values('count', ascending=False)


def analyze_temporal_trends(df):
    """
    Analiza tendencias temporales de resistencia por antibiótico
    """
    trends = {}
    for year in df['date'].unique():
        year_data = df[df['date'] == year]
        antibiotic_counts = {}
        for antibiotics in year_data['antibiotics']:
            for antibiotic in antibiotics:
                antibiotic_counts[antibiotic] = antibiotic_counts.get(antibiotic, 0) + 1
        trends[year] = antibiotic_counts

    return pd.DataFrame(trends).fillna(0)


def analyze_mic_by_region(df):
    """
    Analiza valores MIC por región geográfica
    """
    mic_analysis = []
    for _, row in df.iterrows():
        if row['mic_values']:
            for mic in row['mic_values']:
                try:
                    mic_float = float(mic)
                    mic_data = {
                        'country': row['country'],
                        'mic_value': mic_float,
                        'antibiotics': row['antibiotics']
                    }
                    mic_analysis.append(mic_data)
                except ValueError:
                    continue

    return pd.DataFrame(mic_analysis)

def extract_resistance_genes(abstract):
    """
    Extrae menciones de genes de resistencia del abstract
    """
    common_genes = ['mcr-1', 'ndm', 'ctx-m', 'tem', 'shv', 'oxa', 'vim', 'kpc']
    found_genes = []

    if abstract:
        abstract_lower = abstract.lower()
        for gene in common_genes:
            if gene in abstract_lower:
                found_genes.append(gene)

    return found_genes