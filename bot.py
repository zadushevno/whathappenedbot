import flask
import telebot  # импортируем модуль pyTelegramBotAPI
from telebot import types
import conf     # импортируем наш секретный токен
import markov_model
import time
from models import search_similar_corpora
from models import search_similar
from models import flect
import pymorphy2
import random
from string import punctuation

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)  # бесплатный аккаунт pythonanywhere запрещает работу с несколькими тредами

# удаляем предыдущие вебхуки, если они были
bot.remove_webhook()

# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

emoji_list = ["\u2757", "\u203c\ufe0f", "\u26a1", '']
heads_list = [" Новости прошедшего часа:\n", " Главные новости к этому часу:\n", ""]

morph = pymorphy2.MorphAnalyzer()
f = open('titles.txt', 'r', encoding="utf-8")
data  = [line.strip() for line in f] 


n_of_wins = 0
number_of_games = 0

def play_game():
    seed = random.choice(data).split()
    res = []
    for s in seed:
        right_form = ""
        word = s.strip(punctuation)
        ana = morph.parse(word)[0]
        nf = ana.normal_form
        pos = ana.tag.POS
        most_similar = search_similar(nf, pos)
        m = search_similar_corpora(nf, pos)
        if most_similar != None:
            right_form = most_similar
        elif m != None:
            right_form = m
        else:
            right_form = word
        flected_word = flect(word, right_form, pos)
        if flected_word != None:
            res.append(flected_word)
        else:
            res.append(right_form)
    return (' '.join(seed), ' '.join(res))
@bot.message_handler(commands=["start"])
def welcome(message):

    keyboard = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(text="Сводка свежих новостей", callback_data="fresh_news")
    button2 = types.InlineKeyboardButton(text="Сгенерировать новость", callback_data="generate")
    button3 = types.InlineKeyboardButton(text="Интерфакс или компьютер?", callback_data="game")
    button4 = types.InlineKeyboardButton(text="Посмотреть статистику новостей", callback_data="stats")
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)

    bot.send_message(message.chat.id, "Этот бот всегда в курсе самых свежих новостей!", reply_markup=keyboard)

    while True:
        molniya = emoji_list[2] + " Молния\n" + markov_model.text_model.make_sentence(min_words=7)
        bot.send_message(message.chat.id, molniya)
        time.sleep(random.uniform(30.0, 100.0))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'stats':
            photo = open("wordcloud.png", "rb")
            bot.send_photo(call.message.chat.id, photo)
            bot.send_message(call.message.chat.id, 'Так выглядит облако слов данных, на которых учился бот.')
        if call.data == "fresh_news":
            msg = random.choice(emoji_list) + random.choice(heads_list) + ' '
            for i in range(random.randint(2, 6)):
                t = markov_model.text_model.make_sentence(min_words=7)
                msg = msg + t + '\n\n'
            bot.send_message(call.message.chat.id, msg)
        if call.data == "generate":
            bot.send_message(call.message.chat.id, "Новость о чем хотите узнать?")
        if call.data == "game":
            global number_of_games 
            number_of_games += 1
            q = play_game()
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton(text=str(q[0]), callback_data="r")
            button2 = types.InlineKeyboardButton(text=str(q[1]), callback_data="w")
            keyboard.add(button1)
            keyboard.add(button2)
            bot.send_message(call.message.chat.id, "Какая новость настоящая?", reply_markup=keyboard)
            keyboard.add(button1)
            keyboard.add(button2)
        if call.data == 'r':
            global n_of_wins 
            n_of_wins += 1
            bot.send_message(call.message.chat.id, "Верно! Это настоящая новость.")
            keyboard = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="Да", callback_data="game")
            button2 = types.InlineKeyboardButton(text="Нет", callback_data="stop")
            keyboard.add(button1)
            keyboard.add(button2)
            bot.send_message(call.message.chat.id, "Играем дальше?", reply_markup=keyboard)
        if call.data == 'w':
            bot.send_message(call.message.chat.id, "Неверно: эту новость создала модель.")
            keyboard = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="Да", callback_data="game")
            button2 = types.InlineKeyboardButton(text="Нет", callback_data="stop")
            keyboard.add(button1)
            keyboard.add(button2)
            bot.send_message(call.message.chat.id, "Играем дальше?", reply_markup=keyboard)
        if call.data == 'stop':
            bot.send_message(call.message.chat.id, f"Правильных ответов {n_of_wins} из {number_of_games}")
            number_of_games = 0
            n_of_wins = 0
            keyboard = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="Сводка свежих новостей", callback_data="fresh_news")
            button2 = types.InlineKeyboardButton(text="Сгенерировать новость", callback_data="generate")
            button3 = types.InlineKeyboardButton(text="Интерфакс или компьютер?", callback_data="game")
            button4 = types.InlineKeyboardButton(text="Посмотреть статистику новостей", callback_data="stats")
            keyboard.add(button1)
            keyboard.add(button2)
            keyboard.add(button3)
            keyboard.add(button4)
            bot.send_message(call.message.chat.id, "Хорошо. Вот что я еще умею:", reply_markup=keyboard)


@bot.message_handler(func=lambda m: True)
def start_with(message):
    try:
        bot.send_message(message.chat.id, markov_model.text_model.make_sentence_with_start(message.text))
    except:
        bot.send_message(message.chat.id, 'Я с такими словами новостей не знаю. Введите другое.') 

# пустая главная страничка для проверки
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм 
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
