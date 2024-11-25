import pandas as pd
from Bio import Entrez
import datetime
import warnings
warnings.filterwarnings('ignore')


def setup_entrez(email):
    Entrez.email = email
    return "Configuración de Entrez completada"


def fetch_pathogen_resistance_data(pathogen="Escherichia coli", max_results=500):
    """
    Recupera datos de resistencia antibiótica para diferentes patógenos

    Args:
        pathogen (str): Nombre del patógeno (default: "Escherichia coli")
        max_results (int): Número máximo de resultados a recuperar

    Returns:
        list: Lista de IDs de PubMed
    """
    current_date = datetime.datetime.now()
    two_years_ago = current_date - datetime.timedelta(days=730)
    date_string = two_years_ago.strftime("%Y/%m/%d")

    # Términos de búsqueda mejorados para resistencia antibiótica
    search_term = f"""({pathogen}[Organism]) AND 
                     (("antibiotic resistance"[Title/Abstract] OR 
                       "antimicrobial resistance"[Title/Abstract] OR
                       "drug resistance"[Title/Abstract] OR
                       "bacterial resistance"[Title/Abstract]) AND
                       ("minimum inhibitory concentration"[Text Word] OR
                        "MIC"[Text Word] OR
                        "susceptibility testing"[Text Word] OR
                        "resistance pattern"[Text Word])) AND
                     ("{date_string}"[Publication Date] : "3000"[Publication Date])"""

    # Verificación de resultados disponibles
    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=0)
    total_count = Entrez.read(handle)["Count"]
    handle.close()

    print(f"Total de artículos disponibles para {pathogen}: {total_count}")

    # Obtención de resultados
    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()

    return record["IdList"]


def clean_country_name(country):
    """Limpia y estandariza nombres de países"""
    if pd.isna(country) or not isinstance(country, str):
        return 'Unknown'

    # Limpieza básica inicial
    country = country.split('.')[0].split('@')[0].split('Electronic')[0].split(';')[0].strip()

    # Casos especiales que necesitan pre-procesamiento
    # Manejar todas las variantes de P.R. China
    if any(country.startswith(prefix) for prefix in ['P R', 'P.R', 'PR', 'P. R', 'P.']):
        return 'China'

    if country in ['U', 'U.K', 'UK', 'U. K', 'U.K.']:
        return 'United Kingdom'

    # Mapeo de países
    country_mapping = {
        # China y variantes
        'P.R. China': 'China',
        'PR China': 'China',
        'P. R. China': 'China',
        'P R China': 'China',
        "People's Republic of China": 'China',
        'PRC': 'China',
        'Republic of China': 'China',
        'Hong Kong': 'China',

        # Estados Unidos y variantes
        'USA': 'United States',
        'U.S.A': 'United States',
        'United States of America': 'United States',
        'Connecticut': 'United States',
        'Saskatchewan S7N 5B4 (Gow)': 'Canada',

        # Reino Unido y variantes
        'UK': 'United Kingdom',
        'U.K': 'United Kingdom',
        'U.K.': 'United Kingdom',
        'U': 'United Kingdom',

        # Corea y variantes
        'Republic of Korea': 'South Korea',
        'ROK': 'South Korea',
        'Korea': 'South Korea',
        'Sogang University Seoul': 'South Korea',

        # India y variantes
        'IND': 'India',
        'Republic of India': 'India',
        'Tamil Nadu India': 'India',
        '190006': 'India',  # kashmiruniversity.ac.in

        # Brasil y variantes
        'Brasil': 'Brazil',
        '36038-330': 'Brazil',  # dirección brasileña

        # Otros países con variaciones
        'Islamic Republic of Iran': 'Iran',
        'IR Iran': 'Iran',
        'Deutschland': 'Germany',
        'Universität Bern': 'Switzerland',
        'The Netherlands': 'Netherlands',
        'the Netherlands': 'Netherlands',
        'UAE': 'United Arab Emirates',
        'Türkiye': 'Turkey',
        'TURKEY': 'Turkey',
        'República de Chile': 'Chile',
        'México': 'Mexico',
        'Perú': 'Peru',
        'Czechia': 'Czech Republic',
        'SAU': 'Saudi Arabia',
        'EGY': 'Egypt',
        'NGA': 'Nigeria',
        'GRC': 'Greece',
        'SDN': 'Sudan',
        'NSW': 'Australia',
        'UKRAINE': 'Ukraine',
        'Karachi': 'Pakistan',
        'Selangor': 'Malaysia',
        'Ciudad Universitaria': 'Mexico',

        # Departamentos/Universidades que deben ser mapeados a sus países
        'Department of Microbiology University College of Medical Sciences and Guru Tag Bahadur Hospital Delhi 110095': 'India',
        'Department of Transfusion Medicine Mugdha Medical College and Hospital Dhaka Bangladesh': 'Bangladesh',
        'Department of Medical Laboratory Science University of Energy and Natural Resources Sunyani Ghana': 'Ghana',
        'Dow University of Health Sciences': 'Pakistan',
        'Kerala Veterinary and Animal Sciences University': 'India',
        'Sogang University Seoul 04107 Republic of Korea': 'South Korea',
        'Shahrekord Branch Islamic Azad University Shahrekord Iran': 'Iran'
    }

    if country in country_mapping:
        return country_mapping[country]

    # Para casos que contienen el nombre del país
    for key in ['China', 'India', 'Brazil', 'Iran', 'Egypt', 'Pakistan', 'Bangladesh']:
        if key in country:
            return key

    # Si es solo una letra o muy corto (como 'P'), marcar como Unknown
    if len(country) <= 1:
        return 'Unknown'

    # Si no encontramos ninguna coincidencia y el texto es muy largo o contiene caracteres especiales
    if len(country) > 30 or '@' in country:
        return 'Unknown'

    return country


def get_publication_details(id_list):
    """
    Obtiene y procesa detalles de las publicaciones con énfasis en resistencia
    """
    publications_data = []

    # Procesar los IDs en lotes para evitar timeouts
    batch_size = 100
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i + batch_size]
        try:
            handle = Entrez.efetch(db="pubmed", id=batch_ids, rettype="xml", retmode="xml")
            records = Entrez.read(handle)

            for article in records['PubmedArticle']:
                try:
                    article_data = article['MedlineCitation']['Article']

                    # Extraer abstract y afiliaciones
                    abstract = article_data.get('Abstract', {}).get('AbstractText', [''])[
                        0] if 'Abstract' in article_data else ''

                    # Extraer información de resistencia del abstract
                    resistance_info = extract_resistance_info(abstract)

                    # Extraer y limpiar el país usando la nueva función
                    country = 'Unknown'
                    if 'AuthorList' in article_data:
                        for author in article_data['AuthorList']:
                            if 'AffiliationInfo' in author:
                                for affiliation in author['AffiliationInfo']:
                                    if 'Affiliation' in affiliation:
                                        aff = affiliation['Affiliation']
                                        # Dividir por comas y tomar la última parte
                                        parts = [p.strip() for p in aff.split(',')]
                                        if parts:
                                            possible_country = parts[-1].strip('.')
                                            cleaned_country = clean_country_name(possible_country)
                                            if cleaned_country != 'Unknown':
                                                country = cleaned_country
                                                break

                    # Extraer fecha
                    date = article_data['Journal']['JournalIssue']['PubDate'].get('Year', 'Unknown')

                    pub_data = {
                        'pmid': article['MedlineCitation']['PMID'],
                        'title': article_data['ArticleTitle'],
                        'date': validate_date(date),
                        'country': country,
                        'journal': article_data['Journal']['Title'],
                        'abstract': abstract,
                        'antibiotics': list(resistance_info['antibiotics']),
                        'mic_values': resistance_info['mic_values'],
                        'resistance_patterns': resistance_info['resistance_patterns']
                    }

                    # Solo añadir si tenemos datos relevantes
                    if pub_data['date'] != 'Unknown':
                        publications_data.append(pub_data)

                except Exception as e:
                    print(f"Error processing article: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error fetching batch: {str(e)}")
            continue

    return pd.DataFrame(publications_data)


def extract_resistance_info(abstract):
    """
    Nueva función para extraer información sobre resistencia antibiótica

    Args:
        abstract (str): Texto del abstract

    Returns:
        dict: Información sobre resistencia encontrada
    """
    resistance_info = {
        'antibiotics': set(),
        'mic_values': [],
        'resistance_patterns': []
    }

    # Lista común de antibióticos
    common_antibiotics = [
        'ampicillin', 'amoxicillin', 'tetracycline', 'ciprofloxacin',
        'gentamicin', 'cefotaxime', 'ceftriaxone', 'imipenem',
        'meropenem', 'colistin', 'polymyxin'
    ]

    if not abstract:
        return resistance_info

    abstract = abstract.lower()

    # Buscar antibióticos mencionados
    for antibiotic in common_antibiotics:
        if antibiotic in abstract:
            resistance_info['antibiotics'].add(antibiotic)

    # Buscar valores MIC (Minimum Inhibitory Concentration)
    import re
    mic_pattern = r'mic[^\d]*(\d+(?:\.\d+)?)\s*(?:mg/[lL]|µg/[mM][lL])'
    mic_values = re.findall(mic_pattern, abstract)
    resistance_info['mic_values'] = mic_values

    # Buscar patrones de resistencia
    resistance_patterns = []
    if 'resistant to' in abstract:
        # Encontrar la frase completa que contiene "resistant to"
        sentences = abstract.split('.')
        for sentence in sentences:
            if 'resistant to' in sentence:
                resistance_patterns.append(sentence.strip())

    resistance_info['resistance_patterns'] = resistance_patterns

    return resistance_info

# validate_date() - se mantiene igual
def validate_date(date):
    try:
        year = int(date)
        current_year = datetime.datetime.now().year
        if year > current_year:
            return str(current_year)
        return date
    except:
        return 'Unknown'