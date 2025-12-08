from curl_cffi import requests
import re
import json
import csv
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
URL_DIRECTO = 'https://www.youtube.com/watch?v=7EtlujOpQu0'
NOMBRE_ARCHIVO = 'tracker_youtube.csv'

def obtener_datos_stream():
    """Realiza la petición y extrae los viewers."""
    print(f"Conectando a {URL_DIRECTO}...")
    try:
        # Timeout de 10s para que no se quede colgado
        response = requests.get(URL_DIRECTO, impersonate='firefox135', timeout=10)
        
        patron = r'var ytInitialData = ({.*?});'
        match = re.search(patron, response.text)

        if match:
            data_json = json.loads(match.group(1))
            try:
                # Navegamos por el JSON de YouTube
                primary_info = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
                view_info = primary_info['viewCount']['videoViewCountRenderer']
                
                # Extraemos datos
                viewers = view_info.get('originalViewCount', '0')
                is_live = view_info.get('isLive', False)
                
                if not is_live:
                    return "OFFLINE"
                
                return viewers

            except KeyError:
                # A veces la estructura cambia si el video ya no es live
                return "OFFLINE" 
        else:
            return "ERROR_NO_JSON"

    except Exception as e:
        print(f"Error de conexión: {e}")
        return "ERROR_RED"

def guardar_csv(viewers):
    """Guarda la fecha, hora y viewers en el archivo CSV."""
    
    # --- AJUSTE HORARIO ---
    # GitHub funciona en UTC (Londres). Sumamos 1 hora para España Invierno.
    ahora = datetime.utcnow() + timedelta(hours=1)
    
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M:%S')
    
    archivo_existe = os.path.isfile(NOMBRE_ARCHIVO)
    
    with open(NOMBRE_ARCHIVO, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Si es la primera vez, escribimos los títulos
        if not archivo_existe:
            writer.writerow(['Fecha', 'Hora', 'Viewers'])
            
        writer.writerow([fecha, hora, viewers])
        
    print(f"✅ [{hora}] Dato guardado con éxito: {viewers} espectadores.")

def main():
    # 1. Obtener dato
    viewers = obtener_datos_stream()
    
    # 2. Validar y Guardar
    if viewers == "OFFLINE":
        print("⚠️ El directo está OFFLINE. No se guardan datos.")
    elif viewers.startswith("ERROR"):
        print(f"❌ Ocurrió un error: {viewers}")
    else:
        guardar_csv(viewers)

if __name__ == "__main__":
    main()
