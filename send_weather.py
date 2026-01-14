import requests
import os
from datetime import datetime

# Configurações
OPENWEATHER_API_KEY = "ae915ec4ebfc5d9944943de20a49d04c"
WHATSAPP_PHONE = "+556299755774"
WHATSAPP_APIKEY = "nCrtF8f4S35L"

# Coordenadas de Goiânia, Goiás
LATITUDE = "-15.8942"
LONGITUDE = "-48.9293"

# URL da API OpenWeatherMap
WEATHER_URL = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"

# URL do TextMeBot
WHATSAPP_URL = "https://api.textmebot.com/send.php"

def get_weather():
    """Busca dados de previsão do tempo"""
    try:
        response = requests.get(WEATHER_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar clima: {e}")
        return None

def format_weather_message(weather_data):
    """Formata a mensagem com as informações do clima"""
    try:
        # Informações gerais
        city = weather_data['city']['name']
        
        # Previsão para os próximos dias (a cada 24h)
        message = f"🌤️ *Previsão do Tempo - {city}*\n\n"
        
        # Processa a previsão para os próximos 5 dias
        processed_days = set()
        
        for forecast in weather_data['list'][:40]:  # 5 dias de previsão
            dt = datetime.fromtimestamp(forecast['dt'])
            day_key = dt.strftime("%d/%m")
            
            # Evita duplicar o mesmo dia
            if day_key in processed_days:
                continue
            
            processed_days.add(day_key)
            
            # Informações do dia
            temp_max = forecast['main']['temp_max']
            temp_min = forecast['main']['temp_min']
            description = forecast['weather'][0]['description'].capitalize()
            humidity = forecast['main']['humidity']
            wind_speed = forecast['wind']['speed']
            
            day_name = dt.strftime("%A")
            day_names = {
                'Monday': 'Segunda',
                'Tuesday': 'Terça',
                'Wednesday': 'Quarta',
                'Thursday': 'Quinta',
                'Friday': 'Sexta',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            
            message += f"📅 *{day_names.get(day_name, day_name)} - {day_key}*\n"
            message += f"🌡️ Temp: {temp_min:.0f}°C - {temp_max:.0f}°C\n"
            message += f"☁️ {description}\n"
            message += f"💨 Vento: {wind_speed:.1f} m/s\n"
            message += f"💧 Umidade: {humidity}%\n\n"
        
        message += "Tenha um ótimo dia! ✨"
        return message
    
    except KeyError as e:
        print(f"Erro ao formatar mensagem: {e}")
        return "Erro ao processar dados do clima"

def send_whatsapp_message(message):
    """Envia mensagem via WhatsApp usando TextMeBot"""
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

def main():
    """Função principal"""
    print("🌦️ Iniciando busca de previsão do tempo...")
    
    # Busca o clima
    weather_data = get_weather()
    
    if not weather_data:
        print("Falha ao obter dados do clima")
        return
    
    # Formata a mensagem
    message = format_weather_message(weather_data)
    
    print("📝 Mensagem formatada:")
    print(message)
    
    # Envia via WhatsApp
    if send_whatsapp_message(message):
        print("✅ Processo concluído com sucesso!")
    else:
        print("❌ Falha ao enviar mensagem")

if __name__ == "__main__":
    main()
