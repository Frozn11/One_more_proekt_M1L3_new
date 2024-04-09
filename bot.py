import telebot # библиотека telebot
import random
from setting import TOKEN, APPID # импорт токена
import requests
import time

bot = telebot.TeleBot(TOKEN) 


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я могу управлять чатом и другие вещи, используйте команду /help чтобы узнать другие команды")~
@bot.message_handler(commands=['help'])

def help(message):
    chat_id = message.chat.id 
    bot.send_message(chat_id, "Вы можете посмотреть погоду при использование команды /weather \n \n Вы можете кинуть монетку при использование команды /coin \n \n Вы можете проверить работает ли бот при использование команды /ping \n \n Вы можете забанить участника в чат при использование команды /ban (вам нужно быть администраторам) \n \n Вы можете кикнуть участника из чата при использование команды /kick (вам нужно быть администраторам) \n \n Вы можете убрать возможность пользователя писать в чат на время при использование команды /mute (вам нужно быть администраторам) \n \n Вы можете убрать mute если пользователя был в mute при использование команды /unmute (вам нужно быть администраторам)")


@bot.message_handler(commands=['coin'])
def coin_event(message):
    coin_list = ['орел', 'решка']
    coin_return = random.choice(coin_list)
    bot.reply_to(message, coin_return)

@bot.message_handler(commands=["ping"])
def on_ping(message):
    bot.reply_to(message, "Все ещё работаю!") 

#Я решил выключить потому что это может раздражать
# @bot.message_handler(content_types=['new_chat_members'])
# def make_some(message):
#     bot.send_message(message.chat.id, 'Добро пожаловать новой учасник!')
#     bot.approve_chat_join_request(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение 
        chat_id = message.chat.id # сохранение id чата
         # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status 
         # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно замутить администратора.")
        else:
            duration = 60 # Значение по умолчанию - 1 минута
            args = message.text.split()[1:]
            if args:
                try:
                    duration = int(args[0])
                except ValueError:
                    bot.reply_to(message, "Неправильный формат времени.")
                    return
                if duration < 1:
                    bot.reply_to(message, "Время должно быть положительным числом.")
                    return
                if duration > 1440:
                    bot.reply_to(message, "Максимальное время - 1 день.")
                    return
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time()+duration*60)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} замучен на {duration} минут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")


@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить.")

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно кикнуть администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть.")

@bot.message_handler(commands=['weather'])
def weather(message):
  sent = bot.send_message(message.chat.id, 'Please enter city name')
  bot.register_next_step_handler(sent, weatherNow)

def weatherNow(message): 

    chat_id = message.chat.id

    emojes = {
    "пасмурно": ["🌧"],
    "ясно": ["☀"],
    "облачно с прояснениями": ["🌥"],
    "дождь": ["🌧"],
    "переменная облачность": ["🌥"],
    "небольшой дождь": ["🌧"]
    }
    city_id = 0
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                params={'q': message.text, 'type': 'like', 'units': 'metric', 'APPID': APPID})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                for d in data['list']]
        print("city:", cities)
        city_id = data['list'][0]['id']
        print("success")
    except Exception as e:
        print("Exception (find):", e)
        pass
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                        params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': APPID})
        data = res.json()
        # print(data)
        word = data["weather"][0]['description']
        word = emojes.get(word, [])
        word =  "".join(word)
        if not word:
            print("no")
        bot.send_message(chat_id, f"температура: {data['main']['temp']}° \nпогода: {data['weather'][0]['description']} {word} \nмакс.температура: {data['main']['temp_min']}° \nмини.температура: {data['main']['temp_max']}°")
    except Exception as e:
        print("Exception (weather):", e)
        pass


bad_words = ['lol', 'https:/']
def check_message(message):
    for word in bad_words:
        if word in message.text.lower():
            return True
    return False

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # проверяем сообщение на наличие запрещенных слов
    if check_message(message):
        # если есть хотя бы одно запрещенное слово, кикаем пользователя
        # bot.kick_chat_member(message.chat.id, message.from_user.id)
        bot.send_message(message.chat.id, f"Пользователь {message.from_user.username} БАН")
    else:
        # если запрещенных слов нет, обрабатываем сообщение дальше
        print(message.text)



bot.infinity_polling(none_stop=True)
