import requests
import os
from datetime import datetime, timedelta, timezone

# Configurações
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')
WHATSAPP_APIKEY = os.getenv('WHATSAPP_APIKEY')

# Coordenadas EXATAS de Goiânia, Goiás (Centro da cidade)
LATITUDE = "-16.6869"
LONGITUDE = "-49.2648"
CITY_NAME = "Goiânia"

# Fuso horário de Brasília (GMT-3)
BRT = timezone(timedelta(hours=-3))

# URLs das APIs
CURRENT_WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
FORECAST_URL = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
WHATSAPP_URL = "https://api.textmebot.com/send.php"

def get_current_weather():
    """Busca dados do tempo atual"""
    try:
        response = requests.get(CURRENT_WEATHER_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar clima atual: {e}")
        return None

def get_forecast():
    """Busca previsão do tempo (5 dias)"""
    try:
        response = requests.get(FORECAST_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar previsão: {e}")
        return None

def get_today_forecast(forecast_data):
    """Extrai dados do dia atual da previsão"""
    if not forecast_data or 'list' not in forecast_data:
        return None
    
    now = datetime.now(BRT)
    today = now.date()
    
    temps_today = []
    rain_today = 0
    
    for item in forecast_data['list']:
        dt = datetime.fromtimestamp(item['dt'], tz=BRT)
        
        if dt.date() == today:
            temps_today.append({
                'temp': item['main']['temp'],
                'temp_max': item['main']['temp_max'],
                'temp_min': item['main']['temp_min']
            })
            if 'rain' in item and '3h' in item['rain']:
                rain_today += item['rain']['3h']
    
    if temps_today:
        return {
            'temp_max': max(t['temp_max'] for t in temps_today),
            'temp_min': min(t['temp_min'] for t in temps_today),
            'rain_total': rain_today
        }
    return None

def format_weather_message(current_data, forecast_today):
    """Formata a mensagem com as informações do clima"""
    try:
        now = datetime.now(BRT)
        
        city = current_data.get('name', CITY_NAME)
        country = current_data.get('sys', {}).get('country', 'BR')
        
        temp_current = current_data['main']['temp']
        feels_like = current_data['main']['feels_like']
        
        if forecast_today:
            temp_max = forecast_today['temp_max']
            temp_min = forecast_today['temp_min']
            rain_total = forecast_today['rain_total']
        else:
            temp_max = current_data['main']['temp_max']
            temp_min = current_data['main']['temp_min']
            rain_total = 0
        
        humidity = current_data['main']['humidity']
        pressure = current_data['main']['pressure']
        wind_speed = current_data['wind']['speed']
        wind_deg = current_data['wind'].get('deg', 0)
        visibility = current_data.get('visibility', 0) / 1000
        cloudiness = current_data['clouds']['all']
        description = current_data['weather'][0]['description'].capitalize()
        
        sunrise = datetime.fromtimestamp(current_data['sys']['sunrise'], tz=BRT)
        sunset = datetime.fromtimestamp(current_data['sys']['sunset'], tz=BRT)
        
        def get_wind_direction(degrees):
            val = int((degrees / 22.5) + 0.5)
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                    'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
            return dirs[val % 16]
        
        wind_dir = get_wind_direction(wind_deg)
        
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        message = f"🌦️ *PREVISÃO DO TEMPO - {city.upper()}, {country}*\n"
        message += f"📅 {now.day} de {meses[now.month]} de {now.year} - {now.strftime('%H:%M')}\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🌡️ *TEMPERATURA*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Atual: *{temp_current:.1f}°C*\n"
        message += f"Sensação térmica: {feels_like:.1f}°C\n"
        message += f"Máxima prevista: *{temp_max:.1f}°C*\n"
        message += f"Mínima prevista: *{temp_min:.1f}°C*\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"☁️ *CONDIÇÕES*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Status: {description}\n"
        message += f"Cobertura de nuvens: {cloudiness}%\n"
        message += f"Visibilidade: {visibility:.1f} km\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🌧️ *CHUVA PREVISTA HOJE*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        if rain_total > 0:
            message += f"Acumulado previsto: *{rain_total:.1f} mm*\n"
            if rain_total < 5:
                message += f"Possibilidade: Chuva fraca\n\n"
            elif rain_total < 25:
                message += f"Possibilidade: Chuva moderada\n\n"
            else:
                message += f"Possibilidade: Chuva forte\n\n"
        else:
            message += f"Sem previsão de chuva ☀️\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"💨 *VENTO*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Velocidade: {wind_speed:.1f} m/s ({wind_speed * 3.6:.1f} km/h)\n"
        message += f"Direção: {wind_dir} ({wind_deg}°)\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"💧 *UMIDADE E PRESSÃO*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Umidade: {humidity}%\n"
        message += f"Pressão: {pressure} hPa\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"☀️ *SOL*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Nascer: {sunrise.strftime('%H:%M')}\n"
        message += f"Pôr: {sunset.strftime('%H:%M')}\n\n"
        
        message += "Tenha um ótimo dia! ✨"
        
        return message
    
    except (KeyError, TypeError) as e:
        print(f"Erro ao formatar mensagem: {e}")
        return "Erro ao processar dados do clima"

def send_whatsapp_message(message):
    """Envia mensagem via WhatsApp com debug completo"""
    print("\n" + "="*50)
    print("🔍 DEBUG - ENVIO WHATSAPP")
    print("="*50)
    
    # Valida variáveis de ambiente
    if not WHATSAPP_PHONE:
        print("❌ ERRO: WHATSAPP_PHONE não configurado!")
        return False
    
    if not WHATSAPP_APIKEY:
        print("❌ ERRO: WHATSAPP_APIKEY não configurado!")
        return False
    
    print(f"📱 Telefone: {WHATSAPP_PHONE}")
    print(f"🔑 API Key: {WHATSAPP_APIKEY[:10]}...{WHATSAPP_APIKEY[-4:]}")
    print(f"📝 Tamanho da mensagem: {len(message)} caracteres")
    print(f"🌐 URL da API: {WHATSAPP_URL}")
    
    try:
        params = {
            'phone': WHATSAPP_PHONE,
            'apikey': WHATSAPP_APIKEY,
            'text': message
        }
        
        print("\n📤 Enviando requisição...")
        response = requests.get(WHATSAPP_URL, params=params, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text[:500]}")
        
        response.raise_for_status()
        
        print("\n✅ Mensagem enviada com sucesso!")
        print("="*50 + "\n")
        return True
    
    except requests.RequestException as e:
        print(f"\n❌ ERRO ao enviar WhatsApp:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status Code: {e.response.status_code}")
            print(f"   Response: {e.response.text[:500]}")
        print("="*50 + "\n")
        return False

def main():
    """Função principal"""
    print(f"🌦️ Iniciando busca de previsão do tempo para {CITY_NAME}...\n")
    
    # Busca clima atual
    current_data = get_current_weather()
    if not current_data:
        print("❌ Falha ao obter dados do clima atual")
        return
    
    print(f"✅ Dados atuais obtidos: {current_data.get('name', 'Desconhecido')}\n")
    
    # Busca previsão
    forecast_data = get_forecast()
    forecast_today = None
    
    if forecast_data:
        print("✅ Dados de previsão obtidos\n")
        forecast_today = get_today_forecast(forecast_data)
        if forecast_today:
            print(f"✅ Previsão do dia processada:")
            print(f"   Máxima: {forecast_today['temp_max']:.1f}°C")
            print(f"   Mínima: {forecast_today['temp_min']:.1f}°C")
            print(f"   Chuva: {forecast_today['rain_total']:.1f} mm\n")
    else:
        print("⚠️ Não foi possível obter previsão, usando apenas dados atuais\n")
    
    # Formata mensagem
    message = format_weather_message(current_data, forecast_today)
    print("📝 Mensagem formatada:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Envia mensagem com debug completo
    if send_whatsapp_message(message):
        print("\n🎉 Processo concluído com SUCESSO!")
    else:
        print("\n⚠️ Processo concluído com ERROS no envio do WhatsApp")

if __name__ == "__main__":
    main()
