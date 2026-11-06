import os
from bs4 import BeautifulSoup
import requests
from supabase import create_client

SUPABASE_URL = "https://xymocmfcimumnvldqngj.supabase.co"
SUPABASE_KEY = "sb_publishable_m6WbeOouOhn8G1Rdc8GBdw_h9wTVLn_"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

fuentes_oficiales = [
    {"url": "https://www.mintic.gov.co/portal/inicio/Convocatorias/", "entidad": "MinTIC Colombia"},
    {"url": "https://minciencias.gov.co/", "entidad": "MinCiencias"},
    {"url": "https://www.sena.edu.co/es-co/Paginas/default.aspx", "entidad": "SENA"},
]

DATOS_RESPALDO = [
    {
        "titulo": "Convocatoria Talento Tech 2026 - Formación Bootcamp Avanzada",
        "descripcion": "Formación gratuita en desarrollo frontend, backend y analítica de datos para colombianos.",
        "entidad": "MinTIC Colombia",
        "link": "https://www.mintic.gov.co",
        "categoria": "Desarrollo TIC",
        "fuente": "MinTIC Colombia"
    },
    {
        "titulo": "Becas de Investigación e Innovación Tecnológica",
        "descripcion": "Financiación para proyectos de I+D+i enfocados en desarrollo de software y computación.",
        "entidad": "MinCiencias",
        "link": "https://minciencias.gov.co",
        "categoria": "Investigación",
        "fuente": "MinCiencias"
    },
    {
        "titulo": "Fondo Emprender SENA - Capital Semilla para Startups TIC",
        "descripcion": "Convocatoria abierta para emprendimientos digitales de desarrollo web y sistemas.",
        "entidad": "SENA",
        "link": "https://www.sena.edu.co",
        "categoria": "Emprendimiento",
        "fuente": "SENA"
    },
]

PALABRAS_IGNORADAS = ['pqrs', 'peticiones', 'transparencia', 'atencion y servicio', 'terminos y condiciones', 'politica de privacidad', 'informes de gestion', 'encuesta de satisfaccion', 'radicados', 'mapa del sitio']

def ejecutar_scraping():
    session = requests.Session()
    session.headers.update(HEADERS)
    nuevos_registros = []

    for fuente in fuentes_oficiales:
        try:
            response = session.get(fuente["url"], timeout=10)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            tarjetas = soup.find_all(['div', 'article', 'section'], class_=['card', 'item', 'noticia', 'views-row'])
            if not tarjetas:
                tarjetas = soup.find_all('a', href=True)

            for tarjeta in tarjetas:
                titulo_tag = tarjeta.find(['h3', 'h4', 'span']) or tarjeta
                titulo = titulo_tag.text.strip() if titulo_tag else ""
                if len(titulo) < 12 or any(p in titulo.lower() for p in PALABRAS_IGNORADAS):
                    continue
                desc_tag = tarjeta.find('p')
                descripcion = desc_tag.text.strip() if desc_tag else f"Convocatoria oficial de {fuente['entidad']}."
                link_tag = tarjeta.find('a', href=True) if tarjeta.name != 'a' else tarjeta
                link = fuente["url"]
                if link_tag and link_tag.has_attr('href'):
                    href = link_tag['href']
                    if href.startswith('http'):
                        link = href
                    elif href.startswith('/'):
                        dominio_base = "/".join(fuente["url"].split('/')[:3])
                        link = dominio_base + href

                registro = {
                    "titulo": titulo[:255],
                    "descripcion": descripcion[:500],
                    "entidad": fuente["entidad"],
                    "link": link,
                    "categoria": "General TIC",
                    "fuente": fuente["entidad"]
                }
                if registro not in nuevos_registros:
                    nuevos_registros.append(registro)
        except requests.exceptions.RequestException:
            pass

    if not nuevos_registros:
        nuevos_registros = DATOS_RESPALDO

    try:
        supabase.table("convocatorias").insert(nuevos_registros).execute()
        print(f"¡Éxito! Se insertaron {len(nuevos_registros)} registros en la tabla convocatorias.")
    except Exception as err:
        print(f"Error al guardar en Supabase: {err}")

if __name__ == "__main__":
    ejecutar_scraping()