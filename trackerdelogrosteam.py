import requests
import time

#configuracion 

API_KEY = 'TU_APIKEY_DE_STEAM'
STEAM_ID = 'TU_STEAM_ID'
UMBRAL_PROGRESO = 70 

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
    except:
        pass
    return None

def obtener_detalles_reales(appid):
    # l=spanish fuerza a que las descripciones vengan en español si el juego las tiene
    url = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={API_KEY}&appid={appid}&l=spanish"
    try:
        res = requests.get(url).json()
        if 'game' in res and 'availableGameStats' in res['game']:
            stats = res['game']['availableGameStats']
            if 'achievements' in stats:
                return {ach['name']: ach for ach in stats['achievements']}
    except:
        pass
    return {}

def obtener_porcentajes_globales(appid):
    url = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}"
    try:
        res = requests.get(url).json()
        if 'achievementpercentages' in res:
            return {ach['name']: ach['percent'] for ach in res['achievementpercentages']['achievements']}
    except:
        pass
    return {}

def main():
    print("Conectando con la API de Steam y analizando biblioteca...\n")
    juegos = obtener_juegos_comprados()
    
    if not juegos:
        print("No se encontraron juegos o el perfil es privado.")
        return

    juegos_casi_platinados = []
    
    for juego in juegos:
        appid = juego['appid']
        nombre_juego = juego['name']
        logros = obtener_logros_juego(appid)
        
        if logros:
            total_logros = len(logros)
            desbloqueados = sum(1 for logro in logros if logro['achieved'] == 1)
            
            if total_logros > 0:
                porcentaje = (desbloqueados / total_logros) * 100
                if UMBRAL_PROGRESO <= porcentaje < 100:
                    faltantes = [l['apiname'] for l in logros if l['achieved'] == 0]
                    juegos_casi_platinados.append({
                        'appid': appid,
                        'nombre': nombre_juego,
                        'porcentaje': porcentaje,
                        'desbloqueados': desbloqueados,
                        'total': total_logros,
                        'faltantes': faltantes
                    })
        time.sleep(0.1)

    juegos_casi_platinados.sort(key=lambda x: x['porcentaje'], reverse=True)

    print("=" * 60)
    print("🏆 JUEGOS MÁS CERCANOS AL PLATINO 🏆")
    print("=" * 60 + "\n")

    for j in juegos_casi_platinados:
        appid = j['appid']
        print(f"🎮 {j['nombre']}")
        print(f"   Progreso: {j['porcentaje']:.1f}% ({j['desbloqueados']}/{j['total']} logros)")
        
        detalles = obtener_detalles_reales(appid)
        globales = obtener_porcentajes_globales(appid)
        
        print(f"   Mostrando los primeros 10 trofeos faltantes:")
        
        for apiname in j['faltantes'][:10]:
            info_real = detalles.get(apiname, {})
            
            # Extraemos el valor y forzamos su conversión a decimal (float)
            valor_api = globales.get(apiname, 0.0)
            try:
                pct_comunidad = float(valor_api)
            except (ValueError, TypeError):
                pct_comunidad = 0.0
            
            nombre_bonito = info_real.get('displayName', apiname)
            desc = info_real.get('description', 'Logro oculto (Steam no revela la descripción).')
            
            print(f"   🔸 {nombre_bonito} [{pct_comunidad:.1f}% de jugadores lo tiene]")
            print(f"      - {desc}")
            
        print("-" * 60)

if __name__ == "__main__":
    main()