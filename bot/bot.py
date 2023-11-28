import os
from datetime import datetime
import requests
from telebot import TeleBot
from telebot.types import Message

bot = TeleBot(token=os.getenv('TELEGRAM_TOKEN', None))


@bot.message_handler(commands=['start', 'help'])
def start(message: Message):
    bot.send_message(
        message.chat.id,
        'Привет Я бот, которые рассказывает о погоде в городах мирах.\n'
        'Напиши город, в которым ты хочешь узнать текущую погоду!'
    )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_weather(message: Message) -> None:
    current_time = datetime.now()
    city = message.text
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    response = requests.get(f'http://backend/weather?city={city}')
    message_to_send = f'Прогноз погоды для {city} на {formatted_time}\n'
    if response.status_code == 200:
        weather_data = response.json()
        message_to_send += (f'Температура: {weather_data.get("temp", None)}\n'
                            f'Атмосферное давление: {weather_data.get("pressure_mm", None)} мм рт.ст.\n'
                            f'Скорость ветра: {weather_data.get("wind_speed", None)} м/сек')
    else:
        message_to_send += ('На данный момент погода не известна, так как сервис не отвечает, '
                            'либо такой город не существует :(')
    bot.send_message(
        message.chat.id,
        message_to_send
    )


bot.infinity_polling()
