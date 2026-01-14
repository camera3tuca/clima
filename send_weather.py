import requests
import os
from datetime import datetime

# Configurações
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')
WHATSAPP_APIKEY = os.getenv('WHATSAPP_APIKEY')

# Coordenadas precisas de Goiânia, Goiás
LATITUDE = "-15.8942"
LONGITUDE = "-48.9293"
CITY_NAME = "Goiânia"

# URLs das APIs
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
WHATSAPP_URL = "https://api.textmebot.com/send.php"

def get_weather():
    """Busca dados do tempo atual"""
    try:
        response = requests.get(WEATHER_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar clima: {e}")
        return None

def format_weather_message(weather_data):
    """Formata a mensagem com as informações do clima do dia"""
    try:
        # Informações básicas
        city = weather_data.get('name', CITY_NAME)
        country = weather_data.get('sys', {}).get('country', 'BR')
        
        # Temperatura
        temp_current = weather_data['main']['temp']
        temp_max = weather_data['main']['temp_max']
        temp_min = weather_data['main']['temp_min']
        feels_like = weather_data['main']['feels_like']
        
        # Umidade e pressão
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        
        # Vento
        wind_speed = weather_data['wind']['speed']
        wind_deg = weather_data['wind'].get('deg', 0)
        
        # Visibilidade
        visibility = weather_data.get('visibility', 0) / 1000  # converter para km
        
        # Nuvens
        cloudiness = weather_data['clouds']['all']
        
        # Descrição
        description = weather_data['weather'][0]['description'].capitalize()
        
        # Hora do nascer e pôr do sol
        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise'])
        sunset = datetime.fromtimestamp(weather_data['sys']['sunset'])
        
        # Hora atual
        now = datetime.now()
        
        # Direção do vento
        def get_wind_direction(degrees):
            val = int((degrees / 22.5) + 0.5)
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                    'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
            return dirs[val % 16]
        
        wind_dir = get_wind_direction(wind_deg)
        
        # Formata a mensagem
        message = f"🌦️ *PREVISÃO DO TEMPO - {city.upper()}, {country}*\n"
        message += f"📅 {now.strftime('%d de %B de %Y - %H:%M')}\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🌡️ *TEMPERATURA*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Atual: *{temp_current:.1f}°C*\n"
        message += f"Sensação térmica: {feels_like:.1f}°C\n"
        message += f"Máxima: *{temp_max:.1f}°C*\n"
        message += f"Mínima: *{temp_min:.1f}°C*\n\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"☁️ *CONDIÇÕES*\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"Status: {description}\n"
        message += f"Cobertura de nuvens: {cloudiness}%\n"
        message += f"Visibilidade: {visibility:.1f} km\n\n"
        
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
    """Envia mensagem de texto via WhatsApp usando TextMeBot"""
    try:
        params = {
            'phone': WHATSAPP_PHONE,
            'apikey': WHATSAPP_APIKEY,
            'text': message
        }
        
        response = requests.get(WHATSAPP_URL, params=params, timeout=10)
        response.raise_for_status()
        
        print("✅ Mensagem de texto enviada com sucesso!")
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
    """Envia imagem via WhatsApp usando TextMeBot"""
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
    """Remove arquivos temporários dos mapas"""
    try:
        os.remove('temp_map.png')
        os.remove('rain_map.png')
        print("✅ Limpeza de arquivos temporários concluída!")
    except Exception as e:
        print(f"⚠️ Aviso ao limpar arquivos: {e}")

def main():
    """Função principal"""
    print(f"🌦️ Iniciando busca de previsão do tempo para {CITY_NAME}...\n")
    
    # Busca o clima
    weather_data = get_weather()
    
    if not weather_data:
        print("Falha ao obter dados do clima")
        return
    
    print(f"✅ Dados obtidos com sucesso de: {weather_data.get('name', 'Desconhecido')}\n")
    
    # Formata e envia a mensagem de temperatura
    message = format_weather_message(weather_data)
    print("📝 Mensagem formatada:")
    print(message)
    print("\n")
    
    if send_whatsapp_message(message):
        print("✅ Mensagem de texto enviada com sucesso!\n")
    else:
        print("❌ Falha ao enviar mensagem de texto\n")
    
    # Gera e envia mapas
    print("🗺️ Gerando mapas do clima...\n")
    
    if generate_temperature_map():
        send_image_whatsapp('temp_map.png', '🌡️ Mapa de Temperatura do Brasil - Goiânia em foco')
    
    if generate_precipitation_map():
        send_image_whatsapp('rain_map.png', '🌧️ Mapa de Precipitação do Brasil - Goiânia em foco')
    
    # Limpa os arquivos temporários
    cleanup_maps()
    
    print("\n✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
