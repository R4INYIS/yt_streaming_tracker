from curl_cffi import requests
import re
import json
import csv
import os
import random
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
URL_DIRECTO = 'https://www.youtube.com/watch?v=7EtlujOpQu0'
NOMBRE_ARCHIVO = 'tracker_youtube.csv'

def obtener_datos():
    print(f"--- EJECUTANDO TRACKER ---")
    
    # Cabeceras reales para parecer un navegador humano
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        # Usamos chrome110 para mejor compatibilidad
        response = requests.get(URL_DIRECTO, headers=headers, impersonate='chrome110', timeout=20)
        
        # Búsqueda del dato en el HTML
        patron = r'var ytInitialData = ({.*?});'
        match = re.search(patron, response.text)

        if match:
            data = json.loads(match.group(1))
            
            # Navegación profunda segura
            try:
                contents = data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
                primary = contents[0]['videoPrimaryInfoRenderer']
                view_info = primary['viewCount']['videoViewCountRenderer']
                
                # Intentar sacar el número crudo
                if 'originalViewCount' in view_info:
                    return view_info['originalViewCount']
                
                # Si no está el crudo, buscamos el texto (ej: "250.300 watching")
                if 'viewCount' in view_info:
                    texto = view_info['viewCount']['runs'][0]['text']
                    # Limpiamos el texto para dejar solo números
                    nums = re.sub(r'[^\d]', '', texto)
                    return nums

                return "OFFLINE"
            except (KeyError, IndexError):
                # Si falla la estructura, puede que el directo haya acabado
                return "OFFLINE"
        else:
            return "ERROR_BLOQUEO"

    except Exception as e:
        print(f"Error de conexión: {e}")
        return "ERROR_RED"

def guardar(dato):
    # Hora España (UTC+1)
    ahora = datetime.utcnow() + timedelta(hours=1)
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M')
    
    # Preparar fila
    fila = [fecha, hora, dato]
    
    # Escribir en CSV
    existe = os.path.isfile(NOMBRE_ARCHIVO)
    
    with open(NOMBRE_ARCHIVO, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Hora', 'Viewers'])
        writer.writerow(fila)
    
    print(f"✅ Guardado: {fecha} {hora} -> {dato}")

if __name__ == "__main__":
    viewers = obtener_datos()
    guardar(viewers)
