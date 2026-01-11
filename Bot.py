import telebot
import requests
import json
from datetime import datetime

TOKEN = "8021856439:AAF4_5zZH5bBrL4Q6QhBPxrZSPKniq5_Y0U"
bot = telebot.TeleBot(TOKEN)
DEEPSEEK_API_KEY = "sk-88c71385b6594cfa8a35810243dcecd8"


# Экономия токенов

MAX_TOKENS = 200 #больше токенов больше ответ
API_URL = "https://api.deepseek.com/v1/chat/completions"

#потом заменить на базу
user_usage = {}



#Проверка лимитов. Увеличивает кол-во исп. вопросов + 1
def check_daily_limit(user_id):
    """Проверка лимита запросов в день"""
    today = datetime.now().date().isoformat()

    #Впервые зашел в бота
    if user_id not in user_usage:
        user_usage[user_id] = {'date': today, 'count': 1}
        return True
    #Если наступил след. день. сбросить лимит запросов
    if user_usage[user_id]['date'] != today:
        user_usage[user_id] = {'date': today, 'count': 1}
        return True

    #Если лимит исчерпан !!!!!!!
    if user_usage[user_id]['count'] >= 15:  # Максимум 10 вопросов в день
        return False

    user_usage[user_id]['count'] += 1
    return True



#Запрос к DeepSeek API с оптимизацией токенов
def askDeepseek(question):


    # Обрезаем вопрос если слишком длинный
    if len(question) > 300:
        question = question[:300] + "..."

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный помощник. Отвечай максимально кратко и по делу. Ограничь ответ 3-4 предложениями.Используй не "
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": MAX_TOKENS,  # Экономим токены
        "temperature": 0.5,  # Уменьшил температуру для более предсказуемых ответов
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Ошибка API: {response.status_code}, {response.text}")
            return f"Ошибка: {response.status_code}. Попробуйте позже."

    except requests.exceptions.Timeout:
        return "Время ожидания истекло. Попробуйте снова."
    except Exception as e:
        print(f"Ошибка в askDeepseek: {e}")
        return "Произошла ошибка при обработке запроса."



@bot.message_handler(commands=['start'])
def start(message):

    welcome_text = "Это бот-дипсик. Задай вопрос и получи ответ."
    "Используй команду /ai и напиши вопрос."
    bot.send_message(message.chat.id, welcome_text)



@bot.message_handler(commands=['ai'])
def deepseekSearch(message):
    """Обработчик команды /ai"""
    user_id = message.from_user.id

    # Проверяем лимит
    if not check_daily_limit(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Вы превысили дневной лимит в 10 вопросов. Попробуйте завтра!"
        )
        return

    # Получаем вопрос
    user_question = message.text.replace("/ai", "").strip()

    if not user_question:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, напишите вопрос после команды /ai\nПример: /ai Что такое ИИ?"
        )
        return

    # Отправляем статус "печатает"
    bot.send_chat_action(message.chat.id, 'typing')

    # Получаем ответ от DeepSeek
    deepseekAnswer = askDeepseek(user_question)

    # Отправляем ответ
    bot.send_message(message.chat.id, deepseekAnswer)


# @bot.message_handler(commands=['stats'])




bot.infinity_polling()


# def start(message):
#     """Обработчик команды /start"""
#     welcome_text = """🤖 Привет! Я AI-помощник на базе DeepSeek.
#
# 📝 Как использовать:
# • Просто напиши мне вопрос
# • Или используй команду /ai <вопрос>
#
# ⚡ Ответы будут краткими и по делу
# 📊 Лимит: 10 вопросов в день
#
# Задавай свой вопрос!"""
#     bot.send_message(message.chat.id, welcome_text)


# supabase = create_client(
#     "",
#     ""
# )


# @bot.message_handler(commands=['start'])
# def start(message):
#     user = message.from_user
#
#
#     supabase.table('users').insert({
#         'telegram_id': user.id,
#         'username': user.username,
#         'first_name': user.first_name
#     }).execute()


