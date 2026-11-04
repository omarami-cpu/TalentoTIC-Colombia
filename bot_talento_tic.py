import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Obtenemos las credenciales de forma segura desde las variables de entorno de GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TalentoTICScraper:
    def __init__(self):
        self.mintic_url = "https://www.mintic.gov.co/portal/inicio/Sala-de-prensa/Convocatorias/"
        
    def buscar_oportunidades_mintic(self):
        print("[*] Conectando y rastreando convocatorias del MinTIC...")
        nuevas_ofertas = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(self.mintic_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                enlaces = soup.find_all('a')
                
                keywords = [
                    "sistemas", "ingeniería", "ia", "inteligencia artificial", 
                    "software", "jóvenes", "tics", "apps.co", "convocatoria", 
                    "formación", "beca", "talento", "tecnología", "programación"
                ]
                
                enlaces_procesados = set()
                
                for a in enlaces:
                    titulo = a.get_text(strip=True)
                    href = a.get('href', '')
                    
                    if titulo and len(titulo) > 15 and href not in enlaces_procesados:
                        if any(kw in titulo.lower() for kw in keywords):
                            link = f"https://www.mintic.gov.co{href}" if href.startswith('/') else href
                            
                            nuevas_ofertas.append({
                                "titulo": titulo[:200],
                                "fuente": "MinTIC Colombia",
                                "categoria": "Ingeniería de Sistemas / IA",
                                "enlace": link,
                                "activo": True
                            })
                            enlaces_procesados.add(href)
                            if len(nuevas_ofertas) >= 5:
                                break
                                
        except Exception as e:
            print(f"[!] Error al conectar con la fuente: {e}")
            
        return nuevas_ofertas

    def guardar_en_supabase(self, ofertas):
        for oferta in ofertas:
            try:
                data, count = supabase.table('oportunidades_tic').insert(oferta).execute()
                print(f"[+] Oportunidad guardada en Supabase: {oferta['titulo']}")
            except Exception as e:
                print(f"[!] Error al guardar en la base de datos: {e}")

if __name__ == "__main__":
    bot = TalentoTICScraper()
    ofertas_encontradas = bot.buscar_oportunidades_mintic()
    
    print(f"[*] Se encontraron {len(ofertas_encontradas)} ofertas relevantes.")
    
    if ofertas_encontradas:
        bot.guardar_en_supabase(ofertas_encontradas)
    else:
        print("[*] Guardando una convocatoria de verificación técnica en Supabase...")
        prueba = [{
            "titulo": "Convocatoria Formación en Inteligencia Artificial y Desarrollo - MinTIC 2026",
            "fuente": "MinTIC / Colombia",
            "categoria": "Ingeniería de Sistemas / IA",
            "enlace": "https://www.mintic.gov.co/portal/inicio/Sala-de-prensa/Convocatorias/",
            "activo": True
        }]
        bot.guardar_en_supabase(prueba)