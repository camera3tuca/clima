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
        # Converte timestamp para datetime no fuso horário de Brasília
        dt = datetime.fromtimestamp(item['dt'], tz=BRT)
        
        # Se é hoje, coleta os dados
        if dt.date() == today:
            temps_today.append({
                'temp': item['main']['temp'],
                'temp_max': item['main']['temp_max'],
                'temp_min': item['main']['temp_min']
            })
            # Soma chuva (se houver)
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
        # Hora atual em Brasília
        now = datetime.now(BRT)
        
        # Informações básicas
        city = current_data.get('name', CITY_NAME)
        country = current_data.get('sys', {}).get('country', 'BR')
        
        # Temperatura atual
        temp_current = current_data['main']['temp']
        feels_like = current_data['main']['feels_like']
        
        # Usa temperaturas do forecast se disponível, senão usa do current
        if forecast_today:
            temp_max = forecast_today['temp_max']
            temp_min = forecast_today['temp_min']
            rain_total = forecast_today['rain_total']
        else:
            temp_max = current_data['main']['temp_max']
            temp_min = current_data['main']['temp_min']
            rain_total = 0
        
        # Umidade e pressão
        humidity = current_data['main']['humidity']
        pressure = current_data['main']['pressure']
        
        # Vento
        wind_speed = current_data['wind']['speed']
        wind_deg = current_data['wind'].get('deg', 0)
        
        # Visibilidade
        visibility = current_data.get('visibility', 0) / 1000
        
        # Nuvens
        cloudiness = current_data['clouds']['all']
        
        # Descrição
        description = current_data['weather'][0]['description'].capitalize()
        
        # Nascer e pôr do sol (convertido para horário de Brasília)
        sunrise = datetime.fromtimestamp(current_data['sys']['sunrise'], tz=BRT)
        sunset = datetime.fromtimestamp(current_data['sys']['sunset'], tz=BRT)
        
        # Direção do vento
        def get_wind_direction(degrees):
            val = int((degrees / 22.5) + 0.5)
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                    'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
            return dirs[val % 16]
        
        wind_dir = get_wind_direction(wind_deg)
        
        # Meses em português
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        # Formata a mensagem
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
        
        # Adiciona previsão de chuva
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
    """Envia mensagem via WhatsApp"""
    try:
        params = {
            'phone': WHATSAPP_PHONE,
            'apikey': WHATSAPP_APIKEY,
            'text': message
        }
        
        response = requests.get(WHATSAPP_URL, params=params, timeout=10)
        response.raise_for_status()
        
        print("✅ Mensagem enviada com sucesso!")
        print(f"Status: {response.status_code}")
        return True
    
    except requests.RequestException as e:
        print(f"❌ Erro ao enviar WhatsApp: {e}")
        return False

def generate_temperature_map():
    """Gera mapa de temperatura do Brasil com zoom em Goiânia"""
    try:
        bbox = "-73.99,-33.72,-35.21,-0.64"
        url = f"https://maps.openweathermap.org/maps/2.0/weather?layers=temp&bbox={bbox}&appid={OPENWEATHER_API_KEY}&use_tags=true"
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open('temp_map.png', 'wb') as f:
            f.write(response.content)
        
        print("✅ Mapa de temperatura gerado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar mapa de temperatura: {e}")
        return False

def generate_precipitation_map():
    """Gera mapa de precipitação do Brasil com zoom em Goiânia"""
    try:
        bbox = "-73.99,-33.72,-35.21,-0.64"
        url = f"https://maps.openweathermap.org/maps/2.0/weather?layers=precipitation&bbox={bbox}&appid={OPENWEATHER_API_KEY}&use_tags=true"
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        with open('rain_map.png', 'wb') as f:
            f.write(response.content)
        
        print("✅ Mapa de chuva gerado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar mapa de precipitação: {e}")
        return False

def send_image_whatsapp(image_path, caption):
    """Envia imagem via WhatsApp"""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            params = {
                'phone': WHATSAPP_PHONE,
                'apikey': WHATSAPP_APIKEY,
                'caption': caption
            }
            
            response = requests.post(WHATSAPP_URL, params=params, files=files, timeout=30)
            response.raise_for_status()
        
        print(f"✅ Imagem enviada: {image_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar imagem: {e}")
        return False

def cleanup_maps():
    """Remove arquivos temporários"""
    try:
        if os.path.exists('temp_map.png'):
            os.remove('temp_map.png')
        if os.path.exists('rain_map.png'):
            os.remove('rain_map.png')
        print("✅ Limpeza de arquivos temporários concluída!")
    except Exception as e:
        print(f"⚠️ Aviso ao limpar arquivos: {e}")

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
    
    # Formata e envia mensagem
    message = format_weather_message(current_data, forecast_today)
    print("📝 Mensagem formatada:")
    print(message)
    print("\n")
    
    if send_whatsapp_message(message):
        print("✅ Mensagem enviada com sucesso!\n")
    else:
        print("❌ Falha ao enviar mensagem\n")
    
    # Gera e envia mapas
    print("🗺️ Gerando mapas do clima...\n")
    
    if generate_temperature_map():
        send_image_whatsapp('temp_map.png', '🌡️ Mapa de Temperatura do Brasil - Goiânia')
    
    if generate_precipitation_map():
        send_image_whatsapp('rain_map.png', '🌧️ Mapa de Precipitação do Brasil - Goiânia')
    
    # Limpa arquivos temporários
    cleanup_maps()
    
    print("\n✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
