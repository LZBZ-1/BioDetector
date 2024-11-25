from flask import Flask, render_template, request, redirect
import json
import plotly

from analysis import main_analysis, setup_entrez

app = Flask(__name__)

# Lista de bacterias disponibles para análisis
BACTERIAS = [
    {'id': 'ecoli', 'name': 'Escherichia coli'},
    {'id': 'saureus', 'name': 'Staphylococcus aureus'},
    {'id': 'paeruginosa', 'name': 'Pseudomonas aeruginosa'},
    {'id': 'kpneumoniae', 'name': 'Klebsiella pneumoniae'},
    {'id': 'senterica', 'name': 'Salmonella enterica'}
]

BACTERIA_MAP = {
    'ecoli': 'Escherichia coli',
    'saureus': 'Staphylococcus aureus',
    'paeruginosa': 'Pseudomonas aeruginosa',
    'kpneumoniae': 'Klebsiella pneumoniae',
    'senterica': 'Salmonella enterica'
}

# Configuración inicial
setup_entrez("tu_email@ejemplo.com")


@app.route('/')
def home():
    return render_template('index.html', bacterias=BACTERIAS)


@app.route('/analyze')
def analyze():
    bacteria_id = request.args.get('bacteria')
    if not bacteria_id or bacteria_id not in BACTERIA_MAP:
        return redirect('/')

    try:
        # Obtener el nombre científico de la bacteria
        bacteria_name = BACTERIA_MAP[bacteria_id]

        # Realizar el análisis
        df, analysis_results, all_visualizations = main_analysis(pathogen=bacteria_name, max_results= 10000)

        if df is None:
            return render_template('error.html',
                                   message="No se pudieron obtener datos para esta bacteria")

        # Preparar datos para las visualizaciones
        visualizations = {}

        # Procesar visualizaciones originales
        if 'original' in all_visualizations:
            fig_map, fig_antibiotics, fig_timeline = all_visualizations['original']
            visualizations['map'] = json.dumps(fig_map, cls=plotly.utils.PlotlyJSONEncoder)
            visualizations['antibiotics'] = json.dumps(fig_antibiotics, cls=plotly.utils.PlotlyJSONEncoder)
            visualizations['timeline'] = json.dumps(fig_timeline, cls=plotly.utils.PlotlyJSONEncoder)

        # Procesar visualizaciones adicionales
        if 'additional' in all_visualizations:
            for name, fig in all_visualizations['additional'].items():
                visualizations[name] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Preparar resumen estadístico
        # En app.py, actualizar el summary:
        summary = {
            'total_studies': len(df),
            'time_period': f"{df['date'].min()} - {df['date'].max()}",
            'countries': df['country'].nunique(),
            'multi_resistance': len(df[df['antibiotics'].apply(len) > 2]),
            'top_countries': df['country'].value_counts().head(3).to_dict(),
            'top_antibiotics': df['antibiotics'].explode().value_counts().head(3).to_dict(),
            'mic_studies': len(df[df['mic_values'].apply(len) > 0]),
            'total_patterns': sum(df['resistance_patterns'].apply(len))
        }

        return render_template(
            'dashboard.html',
            bacteria_name=bacteria_name,
            summary=summary,
            visualizations=visualizations
        )

    except Exception as e:
        return render_template('error.html',
                               message=f"Error en el análisis: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)