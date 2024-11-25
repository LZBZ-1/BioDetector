from analysis.data_fetch import (
    setup_entrez,
    fetch_pathogen_resistance_data,
    get_publication_details
)

from analysis.analysis_types import (
    analyze_resistance_patterns,
    analyze_multi_resistance,
    analyze_antibiotic_cooccurrence,
    analyze_temporal_trends,
    analyze_mic_by_region
)

from analysis.visualization import (
    create_resistance_visualizations,
    create_additional_visualizations
)

def main_analysis(pathogen="Escherichia coli", max_results=500):
    """
    Función principal que ejecuta todo el análisis
    """
    print(f"Iniciando análisis de resistencia antibiótica para {pathogen}...")

    # 1. Obtener datos
    id_list = fetch_pathogen_resistance_data(pathogen, max_results)
    if not id_list:
        print("No se encontraron resultados")
        return None

    # 2. Procesar publicaciones
    df = get_publication_details(id_list)
    if df.empty:
        print("No se pudieron procesar los detalles de las publicaciones")
        return None

    # 3. Analizar patrones
    analysis_results = analyze_resistance_patterns(df)

    # 4. Crear visualizaciones
    try:
        figs = create_resistance_visualizations(df, analysis_results)
        print("\nVisualizaciones generadas exitosamente")
    except Exception as e:
        print(f"\nError en la generación de visualizaciones: {str(e)}")
        figs = None

    # Análisis adicionales
    multi_resistance_df = analyze_multi_resistance(df)
    cooccurrence_df = analyze_antibiotic_cooccurrence(df)
    temporal_trends = analyze_temporal_trends(df)
    mic_analysis = analyze_mic_by_region(df)

    # Agregar los resultados al diccionario de retorno
    analysis_results.update({
        'multi_resistance': multi_resistance_df,
        'cooccurrence': cooccurrence_df,
        'temporal_trends': temporal_trends,
        'mic_analysis': mic_analysis
    })

    # Crear visualizaciones originales
    figs = create_resistance_visualizations(df, analysis_results)

    # Crear visualizaciones adicionales
    additional_figs = create_additional_visualizations(df, analysis_results)

    # Combinar todas las visualizaciones
    all_visualizations = {
        'original': figs,
        'additional': additional_figs
    }

    return df, analysis_results, all_visualizations