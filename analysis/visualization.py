import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_resistance_visualizations(df, analysis_results):
    """
    Crea visualizaciones usando los países ya normalizados
    """

    # Paleta de colores unificada
    color_scale = [
        [0, '#87CEEB'],  # Sky blue claro
        [0.2, '#4682B4'],  # Steel blue
        [0.4, '#0000CD'],  # Medium blue
        [0.6, '#00008B'],  # Dark blue
        [0.8, '#191970'],  # Midnight blue
        [1.0, '#000080']  # Navy
    ]

    # 1. Procesar datos para el mapa
    country_data = df['country'].value_counts()

    # Crear DataFrame base
    country_counts = pd.DataFrame({
        'country': country_data.index,
        'studies': country_data.values
    })

    # Mapeo expandido para códigos ISO
    iso_mapping = {
        'United States': 'USA', 'China': 'CHN', 'India': 'IND', 'United Kingdom': 'GBR',
        'Brazil': 'BRA', 'South Korea': 'KOR', 'Iran': 'IRN', 'Turkey': 'TUR',
        'Japan': 'JPN', 'Germany': 'DEU', 'France': 'FRA', 'Italy': 'ITA',
        'Spain': 'ESP', 'Canada': 'CAN', 'Australia': 'AUS', 'Mexico': 'MEX',
        'Egypt': 'EGY', 'Pakistan': 'PAK', 'Malaysia': 'MYS', 'Thailand': 'THA',
        'Netherlands': 'NLD', 'Switzerland': 'CHE', 'Sweden': 'SWE', 'Belgium': 'BEL',
        'Norway': 'NOR', 'Denmark': 'DNK', 'Finland': 'FIN', 'Austria': 'AUT',
        'Poland': 'POL', 'Greece': 'GRC', 'Portugal': 'PRT', 'Czech Republic': 'CZE',
        'Romania': 'ROU', 'Hungary': 'HUN', 'Ireland': 'IRL', 'Bulgaria': 'BGR',
        'Slovakia': 'SVK', 'Croatia': 'HRV', 'Slovenia': 'SVN', 'Estonia': 'EST',
        'Latvia': 'LVA', 'Lithuania': 'LTU', 'Cyprus': 'CYP', 'Malta': 'MLT',
        'Iceland': 'ISL', 'Luxembourg': 'LUX', 'Russia': 'RUS', 'Ukraine': 'UKR',
        'Belarus': 'BLR', 'Moldova': 'MDA', 'Georgia': 'GEO', 'Armenia': 'ARM',
        'Azerbaijan': 'AZE', 'Kazakhstan': 'KAZ', 'Uzbekistan': 'UZB', 'Turkmenistan': 'TKM',
        'Kyrgyzstan': 'KGZ', 'Tajikistan': 'TJK', 'Mongolia': 'MNG', 'North Korea': 'PRK',
        'Vietnam': 'VNM', 'Cambodia': 'KHM', 'Laos': 'LAO', 'Myanmar': 'MMR',
        'Bangladesh': 'BGD', 'Nepal': 'NPL', 'Sri Lanka': 'LKA', 'Bhutan': 'BTN',
        'Afghanistan': 'AFG', 'Iraq': 'IRQ', 'Syria': 'SYR', 'Lebanon': 'LBN',
        'Jordan': 'JOR', 'Israel': 'ISR', 'Palestine': 'PSE', 'Saudi Arabia': 'SAU',
        'Yemen': 'YEM', 'Oman': 'OMN', 'UAE': 'ARE', 'Qatar': 'QAT',
        'Bahrain': 'BHR', 'Kuwait': 'KWT', 'Algeria': 'DZA', 'Morocco': 'MAR',
        'Tunisia': 'TUN', 'Libya': 'LBY', 'Sudan': 'SDN', 'South Sudan': 'SSD',
        'Ethiopia': 'ETH', 'Eritrea': 'ERI', 'Djibouti': 'DJI', 'Somalia': 'SOM',
        'Kenya': 'KEN', 'Uganda': 'UGA', 'Rwanda': 'RWA', 'Burundi': 'BDI',
        'Tanzania': 'TZA', 'Angola': 'AGO', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE',
        'Mozambique': 'MOZ', 'Malawi': 'MWI', 'Madagascar': 'MDG', 'Namibia': 'NAM',
        'Botswana': 'BWA', 'South Africa': 'ZAF', 'Lesotho': 'LSO', 'Swaziland': 'SWZ',
        'Nigeria': 'NGA', 'Ghana': 'GHA', 'Ivory Coast': 'CIV', 'Niger': 'NER',
        'Mali': 'MLI', 'Burkina Faso': 'BFA', 'Senegal': 'SEN', 'Guinea': 'GIN',
        'Benin': 'BEN', 'Togo': 'TGO', 'Sierra Leone': 'SLE', 'Liberia': 'LBR',
        'Cameroon': 'CMR', 'Gabon': 'GAB', 'Congo': 'COG', 'DR Congo': 'COD',
        'Central African Republic': 'CAF', 'Chad': 'TCD', 'Argentina': 'ARG', 'Chile': 'CHL',
        'Uruguay': 'URY', 'Paraguay': 'PRY', 'Bolivia': 'BOL', 'Peru': 'PER',
        'Ecuador': 'ECU', 'Colombia': 'COL', 'Venezuela': 'VEN', 'Guyana': 'GUY',
        'Suriname': 'SUR', 'French Guiana': 'GUF', 'Panama': 'PAN', 'Costa Rica': 'CRI',
        'Nicaragua': 'NIC', 'Honduras': 'HND', 'El Salvador': 'SLV', 'Guatemala': 'GTM',
        'Belize': 'BLZ', 'Dominican Republic': 'DOM', 'Haiti': 'HTI', 'Cuba': 'CUB',
        'Jamaica': 'JAM', 'Trinidad and Tobago': 'TTO', 'Philippines': 'PHL',
        'Indonesia': 'IDN', 'Singapore': 'SGP', 'New Zealand': 'NZL', 'Taiwan': 'TWN'
    }

    country_counts['iso_alpha'] = country_counts['country'].map(iso_mapping)
    # Quitar solo Unknown y mantener todos los demás países
    country_counts = country_counts[country_counts['country'] != 'Unknown']

    # Crear el mapa coroplético
    fig_map = px.choropleth(
        data_frame=country_counts,
        locations='iso_alpha',
        locationmode='ISO-3',
        color='studies',
        color_continuous_scale=color_scale,
        range_color=[0, country_counts['studies'].max()],
        labels={'studies': 'N° de estudios'},
        hover_name='country'
    )

    # Modifica el formato del hover
    fig_map.update_traces(
        hovertemplate="<b>%{hovertext} (%{location})</b><br>" +
                      "N° de estudios: %{z}<br>" +
                      "<extra></extra>"
    )

    # 2. Gráfico de barras de antibióticos
    antibiotic_df = pd.DataFrame({
        'antibiotic': analysis_results['antibiotic_freq'].index,
        'count': analysis_results['antibiotic_freq'].values
    }).head(10)

    fig_antibiotics = px.bar(
        antibiotic_df,
        x='count',
        y='antibiotic',
        orientation='h',
        title='Top 10 Antibióticos Más Estudiados',
        labels={'count': 'N° de estudios', 'antibiotic': 'Antibiótico'},
        color='count',
        color_continuous_scale=color_scale
    )

    # 3. Gráfico temporal
    fig_timeline = px.bar(
        x=analysis_results['yearly_studies'].index,
        y=analysis_results['yearly_studies'].values,
        title='Evolución Temporal de Estudios de Resistencia',
        labels={'x': 'Año', 'y': 'N° de estudios'},
        color=analysis_results['yearly_studies'].values,
        color_continuous_scale=color_scale
    )

    fig_timeline.update_layout(
        xaxis=dict(
            tickmode='linear',
            dtick=1
        ),
        yaxis=dict(
            title='N° de estudios',
            showgrid=True
        )
    )

    return fig_map, fig_antibiotics, fig_timeline


def create_additional_visualizations(df, analysis_results):
    """
    Crea visualizaciones adicionales para el análisis de resistencia
    """

    visualizations = {}

    # 1. Heatmap de co-ocurrencia de antibióticos
    cooccurrence_matrix = pd.pivot_table(
        analysis_results['cooccurrence'],
        values='count',
        index='antibiotic_1',
        columns='antibiotic_2',
        fill_value=0
    )

    fig_cooccurrence = px.imshow(
        cooccurrence_matrix,
        title='Patrones de Co-ocurrencia de Antibióticos',
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    fig_cooccurrence.update_layout(
        xaxis_title="Antibiótico 1",
        yaxis_title="Antibiótico 2"
    )
    visualizations['cooccurrence'] = fig_cooccurrence

    # 2. Gráfico de burbujas para multi-resistencia por país
    multi_resistance_by_country = analysis_results['multi_resistance'].groupby(
        ['country', 'num_antibiotics']
    ).size().reset_index(name='count')

    fig_bubble = px.scatter(
        multi_resistance_by_country,
        x='country',
        y='num_antibiotics',
        size='count',
        title='Multi-resistencia por País',
        color='num_antibiotics',
        hover_data=['count']
    )
    visualizations['multi_resistance'] = fig_bubble

    # 3. Gráfico de líneas para tendencias temporales
    fig_trends = go.Figure()
    top_antibiotics = analysis_results['antibiotic_freq'].head(5).index

    for antibiotic in top_antibiotics:
        yearly_counts = df[df['antibiotics'].apply(lambda x: antibiotic in x)].groupby('date').size()
        fig_trends.add_trace(go.Scatter(
            x=yearly_counts.index,
            y=yearly_counts.values,
            name=antibiotic,
            mode='lines+markers'
        ))

    fig_trends.update_layout(
        title='Tendencias Temporales por Antibiótico',
        xaxis_title='Año',
        yaxis_title='Número de Estudios',
        hovermode='x unified'
    )
    visualizations['trends'] = fig_trends

    # 4. Box plots de valores MIC por región
    if not analysis_results['mic_analysis'].empty:
        fig_mic = px.box(
            analysis_results['mic_analysis'],
            x='country',
            y='mic_value',
            title='Distribución de Valores MIC por País',
            log_y=True  # MIC suelen tener distribución log-normal
        )
        visualizations['mic_distribution'] = fig_mic

    # 5. Sunburst para jerarquía de resistencia
    hierarchy_data = df.explode('antibiotics').groupby(
        ['country', 'date', 'antibiotics']
    ).size().reset_index(name='count')

    fig_sunburst = px.sunburst(
        hierarchy_data,
        path=['country', 'date', 'antibiotics'],
        values='count',
        title='Jerarquía de Estudios de Resistencia'
    )
    visualizations['hierarchy'] = fig_sunburst

    # 6. Mapa de calor temporal
    temporal_matrix = pd.pivot_table(
        df.explode('antibiotics'),
        values='pmid',
        index='date',
        columns='antibiotics',
        aggfunc='count',
        fill_value=0
    )

    fig_temporal_heat = px.imshow(
        temporal_matrix,
        title='Evolución Temporal de Estudios por Antibiótico',
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    visualizations['temporal_heat'] = fig_temporal_heat

    return visualizations