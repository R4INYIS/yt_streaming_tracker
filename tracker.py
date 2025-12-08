from curl_cffi import requests
import re
import json
import csv
import os
import sys
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
URL_DIRECTO = 'https://www.youtube.com/watch?v=7EtlujOpQu0'
NOMBRE_ARCHIVO = 'tracker_youtube.csv'

def obtener_datos_stream():
    print(f"--- INICIANDO DIAGNÓSTICO ---")
    print(f"Conectando a {URL_DIRECTO}...")
    
    try:
        # Usamos chrome para variar la huella digital
        response = requests.get(URL_DIRECTO, impersonate='chrome110', timeout=15)
        print(f"Código de respuesta: {response.status_code}")
        
        # 1. Comprobamos si nos han bloqueado o pedido cookies
        if "consent" in response.url or "cookie" in response.text.lower():
            print("❌ BLOQUEO: YouTube pide aceptación de cookies/consentimiento.")
            return "ERROR_COOKIES"
            
        if "verify you're human" in response.text.lower():
            print("❌ BLOQUEO: YouTube pide captcha.")
            return "ERROR_CAPTCHA"

        # 2. Buscamos el JSON
        patron = r'var ytInitialData = ({.*?});'
        match = re.search(patron, response.text)

        if match:
            print("✅ Objeto ytInitialData encontrado.")
            data_json = json.loads(match.group(1))
            try:
                # Intentamos ruta estándar
                contents = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents']
                primary_info = contents[0]['videoPrimaryInfoRenderer']
                view_info = primary_info['viewCount']['videoViewCountRenderer']
                
                # Extraemos datos
                viewers_raw = view_info.get('originalViewCount', '0')
                is_live = view_info.get('isLive', False)
                
                print(f"Datos extraídos -> Live: {is_live}, Viewers: {viewers_raw}")
                
                if not is_live:
                    return "OFFLINE"
                
                return viewers_raw

            except KeyError as e:
                print(f"⚠️ Estructura JSON no coincide. Clave faltante: {e}")
                # Imprimimos un trozo del JSON para ver qué está pasando (solo en logs)
                print(str(data_json)[:500]) 
                return "ERROR_ESTRUCTURA"
        else:
            print("❌ No se encontró 'var ytInitialData'. Posible cambio de HTML.")
            return "ERROR_NO_JSON"

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return "ERROR_RED"

def guardar_csv(viewers):
    # Ajuste horario UTC+1
    ahora = datetime.utcnow() + timedelta(hours=1)
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M')
    
    archivo_existe = os.path.isfile(NOMBRE_ARCHIVO)
    
    with open(NOMBRE_ARCHIVO, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not archivo_existe:
            writer.writerow(['Fecha', 'Hora', 'Viewers'])
        
        # GUARDAMOS SIEMPRE, AUNQUE SEA UN ERROR
        # Esto forzará a GitHub a detectar un cambio y actualizar el archivo
        writer.writerow([fecha, hora, viewers])
        
    print(f"💾 Guardado en CSV: {fecha} {hora} -> {viewers}")

def main():
    viewers = obtener_datos_stream()
    guardar_csv(viewers)

if __name__ == "__main__":
    main()
