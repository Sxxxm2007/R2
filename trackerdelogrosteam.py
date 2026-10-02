import requests
import time
#Configuracion cambia la vaina del api_key y del Steam Id por los tuyos para que te muestre los logros
API_KEY = 'PEGA_AQUI_TU_API_KEY'
STEAM_ID = 'PEGA_AQUI_TU_STEAM_ID64'
UMBRAL_PROGRESO = 50 #% de logros completados entre mas bajo mas rango de juegos segun tengas los losgros

def obtener_juegos_comprados():
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json&include_appinfo=1"
    respuesta = requests.get(url).json()
    
    if 'response' in respuesta and 'games' in respuesta['response']:
        return respuesta['response']['games']
    return []

def obtener_logros_juego(appid):
    url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={API_KEY}&steamid={STEAM_ID}"
    try:
        respuesta = requests.get(url).json()
        if 'playerstats' in respuesta and 'achievements' in respuesta['playerstats']:
            return respuesta['playerstats']['achievements']
    except requests.exceptions.RequestException:
        pass # ignora fallos de conexion
    return None

def main():
    print("Conectando con la API de Steam...\n")
    juegos = obtener_juegos_comprados()
    
    if not juegos:
        print("No se encontraron juegos o el perfil es privado.")
        return

    print(f"Se encontraron {len(juegos)} juegos en la cuenta. Buscando logros...\n")
    
    for juego in juegos:
        appid = juego['appid']
        nombre_juego = juego['name']
        
        logros = obtener_logros_juego(appid)
        
        if logros:
            total_logros = len(logros)
            logros_desbloqueados = sum(1 for logro in logros if logro['achieved'] == 1)
            
            if total_logros > 0:
                porcentaje = (logros_desbloqueados / total_logros) * 100
                
                # muestra juegos que estan avanzados pero no platinados
                if UMBRAL_PROGRESO <= porcentaje < 100:
                    print(f" {nombre_juego}")
                    print(f" Progreso: {porcentaje:.1f}% ({logros_desbloqueados}/{total_logros} logros)")
                    
                    # 
                    faltantes = [l['apiname'] for l in logros if l['achieved'] == 0]
                    print(f"   Faltan {len(faltantes)} trofeos. Algunos de ellos:")
                    for faltante in faltantes[:30]:
                        print(f"   - {faltante}")
                    print("-" * 40)
        
        # pausa para no saturar la api key y que se bloquee 
        time.sleep(0.2)

if __name__ == "__main__":
    main()