import os
from datetime import datetime
import requests
from telebot import TeleBot
from telebot.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from cache import RedisContextManager

bot = TeleBot(token=os.getenv('TELEGRAM_TOKEN', None))

BUTTON_NAME = 'Узнать погоду'


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Узнать погоду")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Привет! Я бот, который может помочь узнать погоду. Напиши город, который тебе интересен"
        "и нажми кнопку BUTTON_NAME",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def set_user_current_city(message: Message) -> None:
    """Сохраняем город, который указал юзер"""
    if message.text != BUTTON_NAME:
        with RedisContextManager() as cache:
            return cache.set(message.from_user.id, message.text)
    else:
        get_weather(message)


def get_user_current_city(user_id) -> str or None:
    """Получаем город, который указал юзер"""
    with RedisContextManager() as cache:
        return cache.get(user_id)


def get_weather_data(city) -> dict | int:
    """Получаем данные о погоде"""
    response = requests.get(f'http://backend/weather?city={city}')
    match response.status_code:
        case 200:
            weather_data = response.json()
        case _:
            weather_data = response.status_code
    return weather_data


def get_weather(message: Message) -> None:
    """Получаем сообщение о погоде"""
    if message.text == BUTTON_NAME:
        current_time = datetime.now()
        city = get_user_current_city(message.from_user.id)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        weather_data = None
        if city:
            weather_data = get_weather_data(city)
        match weather_data:
            case dict():
                message_to_send = (f'Прогноз погоды для {city} на {formatted_time}\n'
                                   f'Температура: {weather_data.get("temp", None)}\n'
                                   f'Атмосферное давление: {weather_data.get("pressure_mm", None)} мм рт.ст.\n'
                                   f'Скорость ветра: {weather_data.get("wind_speed", None)} м/сек')
            case 404:
                message_to_send = 'Такого города не существует :('
            case 403:
                message_to_send = 'На данный момент погода не известна, так как сервис не отвечает :('
            case _:
                message_to_send = 'Пожалуйста, укажите город :('
        bot.send_message(
            message.chat.id,
            message_to_send
        )


bot.infinity_polling()
