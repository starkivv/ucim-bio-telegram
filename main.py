import random
import requests
import telebot
from telebot import types
import json

# Токен бота
TOKEN = '6772342964:AAHFSewz3tTNuautnHIKrJxc8saqdGHBcpc'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Функция для определения правильного склонения существительного "балл"
def plural_form(number):
    if number % 10 == 1 and number % 100 != 11:
        return "балл"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "балла"
    else:
        return "баллов"

# Загрузка данных из JSON файла
def load_data():
    url = 'https://api.npoint.io/e46681033248a4aec181'
    response = requests.get(url)
    data = response.json()
    return data

# Загрузка результатов из файла score
def load_scores():
    try:
        with open('score.json', 'r') as file:
            scores = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []
    return scores

# Сохранение результатов в файл score
def save_scores(scores):
    with open('score.json', 'w') as file:
        json.dump(scores, file)

# Загрузка результатов из файла fullscore
def load_fullscores():
    try:
        with open('fullscore.json', 'r') as file:
            scores = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []
    return scores

# Сохранение результатов в файл fullscore
def save_fullscores(fullscores):
    with open('fullscore.json', 'w') as file:
        json.dump(fullscores, file)

#файла record.txt, а также для перезаписи данных в файл:
def load_record():
    try:
        with open("record.txt", 'r') as file:
            record = file.read()
    except (FileNotFoundError, json.JSONDecodeError):
        record = 0
    return record


def save_record(record):
    with open("record.txt", 'w') as file:
        file.write(str(record))

# Отправка рандомного приветственного сообщения с кнопками
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_messages = [
        'Добро пожаловать в мир биологических знаний! Готовы проверить свои интеллектуальные способности в игре по биологии? Скажите "Начать" для старта.',
        'Приветствую тебя, будущий биолог! Жаждешь новых знаний? Тогда давай играть и расширять свой ум вместе! Скажите "Начать" для старта.',
        'Привет! Есть ли у тебя острый ум и знания в области биологии? Докажи это, сыграв с нами в интеллектуальную игру! Скажите "Начать" для старта.',
        'Добро пожаловать в биологический мир игры! Уверены, ты сможешь ответить на вопросы и стать настоящим экспертом по биологии! Скажите "Начать" для старта.',
        'Привет! Погрузись в увлекательный мир науки и биологии через нашу игру. Докажи свои знания и стань чемпионом! Скажите "Начать" для старта.'
    ]
    random_message = random.choice(welcome_messages)
    start_button = types.KeyboardButton('Начать')
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(start_button)
    bot.send_message(message.chat.id, random_message, reply_markup=markup)

# Обработка команды "Начать"
@bot.message_handler(func=lambda message: message.text == 'Начать' or message.text == 'Да' or message.text == 'Следующий вопрос')
def start_game(message):
    data = load_data()
    random_definition = random.choice(data)
    bot.send_message(message.chat.id, random_definition['definition'])

    # Загрузка прошлых результатов
    scores = load_scores()

    # Проверка, есть ли пользователь с таким ID в прошлых результатах
    user_id = str(message.from_user.id)
    user_score = next((score for score in scores if score['user_id'] == user_id), None)

    if user_score:
        # Если пользователь уже играл ранее, то показываем его прошлый результат
        score = user_score['score']
        bot.send_message(message.chat.id, f"У Вас сейчас: {score} {plural_form(score)}.")
    else:
        # Если пользователь новый или ранее не играл, то инициализируем его результат
        fullscore = 0

    bot.register_next_step_handler(message, check_answer, random_definition, score, scores)


# Проверка ответа пользователя
def check_answer(message, random_definition, fullscore, scores):
    user_answer = message.text.lower()
    correct_answer = str(random_definition['term']).lower()
    score = 0  # Инициализация score значением 0

    if user_answer == correct_answer:
        reply = f"Молодец! \nПояснение: {random_definition['description']}"
        next_button = 'Следующий вопрос'
        score = 1  # Устанавливаем значение score равным 1 только при правильном ответе
        fullscore += score  # Увеличиваем счет пользователя на 1
    else:
        reply = f"В следующий раз получится. Правильный ответ: {random_definition['term']}. \nПояснение: {random_definition['description']}"
        next_button = 'Следующий вопрос'

    stop_button = 'Нет'
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(next_button, stop_button)

    # Добавляем результат пользователя в список результатов
    user_id = str(message.from_user.id)
    scores = [score for score in scores if score['user_id'] != user_id]
    scores.append({'user_id': user_id, 'score': fullscore})

    bot.send_message(message.chat.id, reply, reply_markup=markup)

    # Сохраняем результаты в файл
    save_scores(scores)


# Обработка команды "Нет"
@bot.message_handler(func=lambda message: message.text == 'Нет')
def stop_game(message, fullscore=None):

    record = load_record()
    record = int(record)
    # Загрузка результатов этой сессии
    scores = load_scores()
    # Загрузка Fullscore
    fullscores = load_fullscores()
    # Проверка, есть ли пользователь с таким ID в прошлых результатах
    user_id = str(message.from_user.id)
    user_score = next((score for score in scores if score['user_id'] == user_id), None)
    user_fullscore = next((fullscore for fullscore in fullscores if fullscore['user_id'] == user_id), None)
    # Загрузка текущего результата
    current_score = next((score['score'] for score in scores if score['user_id'] == user_id), None)

    if user_score:
        # Если пользователь уже играл ранее, сравниваем текущий результат с прошлым
        if current_score > user_fullscore['fullscore']:
            user_fullscore['fullscore'] = current_score  # Обновляем прошлый результат в списке результатов
            bot.send_message(message.chat.id, f"Вы улучшили свой прошлый результат! Новый результат: {current_score} {plural_form(current_score)}.")
        elif current_score == user_fullscore['fullscore']:
            bot.send_message(message.chat.id, f"Вы набрали такое же количество баллов как и в прошлый раз: {current_score} {plural_form(current_score)}.")
        else:
            bot.send_message(message.chat.id, f"Ваш прошлый результат {user_fullscore['fullscore']} {plural_form(user_fullscore['fullscore'])} лучше текущего результата {current_score} {plural_form(current_score)}.")
    else:
        # Если пользователь новый или ранее не играл, сохраняем текущий результат
        fullscores.append({'user_id': user_id, 'fullscore': current_score})
        bot.send_message(message.chat.id, f"Ваш результат: {current_score} {plural_form(current_score)}.")

    # Присваиваем значение 0 элементу в списке scores
    for item in scores:
        if item['user_id'] == user_id:
            item['score'] = 0

    if record < current_score:
        record = current_score

    # Сохраняем результаты в файл
    save_record(record)
    save_scores(scores)
    save_fullscores(fullscores)

    start_button = '/start'
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(start_button)
    bot.send_message(message.chat.id, "Прощайте! Чтобы начать игру снова, нажмите кнопку '/start'.", reply_markup=markup)

# Запуск бота
bot.polling()
