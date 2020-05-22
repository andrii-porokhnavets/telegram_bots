import telebot
import re
import pymongo
from datetime import datetime
from telebot import types
from bson.objectid import ObjectId
from config import *

bot = telebot.TeleBot(TOKEN)

db = pymongo.MongoClient('mongodb://localhost:27017/').kunyn_team

working_obj = {}
for player in db.players.find():
    working_obj[player['telegram_id']] = {
        'name': player['name']
    }

choose_game_msg = 'Тут останні твої ігри'
choose_player_msg = 'Вибери гравця'
choose_rest_player_msg = 'Є! Тобі залишилось оцініти ще їх:'
choose_score_msg = 'Тепер вибери оцінку або введи значення'

show_game_scores = 'Вибери гру, щоб побачити рейтинг гравців за неї'

CREATING_GAME = {
    'name': False,
    'date': False,
}


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Бот для статистики гравців футзальної команди *Кунин*. Тисни /join')


@bot.message_handler(commands=['help'])
def init_handler(message):
    bot.send_message(message.chat.id, 'Список доступних опцій:\n'
                                      '/join - приєднатися до команди\n'
                                      '/games - список 3-х останніх ігор\n'
                                      '/all_games - список всіх ігор\n'
                                      '/rating - рейтинг гравців за всі ігри\n'
                                      '/games_rating - список ігор, щоб подивитись рейтинг')


@bot.message_handler(commands=['join'])
def join_handler(message):
    from_user = message.from_user
    send_msg = 'Ви прийняті і можете оцінювати інших гравців'
    if_exist = db.players.find_one({'telegram_id': from_user.id}) is not None

    if if_exist:
        send_msg = 'Ви вже були додані до команди раніше'
    else:
        db.players.insert_one({
            'telegram_id': from_user.id,
            'name': from_user.first_name
        })

        working_obj[from_user.id] = {
            'name': from_user.first_name
        }

    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row(types.KeyboardButton('/rating'), types.KeyboardButton('/help'))
    keyboard.row(types.KeyboardButton('/games'), types.KeyboardButton('/games_rating'))

    bot.send_message(message.chat.id, send_msg, reply_markup=keyboard)


@bot.message_handler(commands=['games', 'all_games', 'games_rating'])
def handler(message):
    msg = show_game_scores if message.text == '/games_rating' else choose_game_msg
    limit = 3 if message.text == '/games' else 0
    games = db.games.find({'date': {'$lt': datetime.now()}}).sort('date', pymongo.DESCENDING).limit(limit)

    keyboard = types.InlineKeyboardMarkup()
    for game in games:
        keyboard.row(types.InlineKeyboardButton(game['name'], callback_data=str(game['_id'])))

    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['add_game'])
def handler(message):
    CREATING_GAME['name'] = True
    bot.send_message(message.chat.id, 'Введи назву гри')


@bot.message_handler(func=lambda _: CREATING_GAME['name'])
def handler(message):
    game_name = message.text
    msg = 'Коли вона була?'
    is_valid = re.search(r"^(\w+('\w+)?)(\s\w+|-\d|\s\(\w+\))?(\s-\s)(\w+('\w+)?)(\s\w+|-\d|\s\(\w+\))?$", game_name) is not None

    if is_valid:
        CREATING_GAME['name'] = False
        is_exist = db.games.find_one({'name': game_name}) is not None

        if is_exist:
            msg = f'Гра <b>{game_name}</b> вже існує.\nПодивитись список /all_games\nДодати іншу /add_game'
        else:
            inserted_game = db.games.insert_one({
                'name': game_name,
                'scores': []
            })

            CREATING_GAME['date'] = True
            CREATING_GAME['id'] = inserted_game.inserted_id
    else:
        msg = 'Введи валідну назву гри.\nПриклад: <i>Команда-1 - Команда-2</i>'

    bot.send_message(message.chat.id, msg, parse_mode='html')


@bot.message_handler(func=lambda _: CREATING_GAME['date'])
def handler(message):
    target_game = {'_id': ObjectId(CREATING_GAME['id'])}
    game = db.games.find_one(target_game)
    msg = f'Гру *{game["name"]}* створено. Обирай її у списку /games'

    try:
        date = datetime.strptime(message.text, '%Y-%m-%d %H:%M')

        db.games.update_one(target_game, {'$set': {
            'date': date
        }})
        CREATING_GAME['date'] = False
        CREATING_GAME['id'] = None
    except ValueError:
        msg = 'Невірний формат! Приклад валідної дати: _2020-01-12 02:20_'

    bot.send_message(message.chat.id, msg, parse_mode='markdown')


def get_rating_msg(game_id=None):
    target_game = {'_id': game_id} if game_id is not None else {'date': {'$lt': datetime.now()}}

    games = db.games.find(target_game)

    rating = {tg_id: [] for tg_id in working_obj}

    for game in games:
        for s in game['scores']:
            rating[s['to']].append(s['score'])

    for tg_id, scores in rating.items():
        try:
            rating[tg_id] = sum(scores) / len(scores)
        except ZeroDivisionError:
            rating[tg_id] = 0

    sorted_players = {k: v for k, v in sorted(rating.items(), key=lambda item: item[1], reverse=True)}

    result_msg = ''
    for tg_id, score, n in zip(sorted_players, sorted_players.values(), range(len(sorted_players))):
        result_msg += f'{n + 1}. {working_obj[tg_id]["name"]}  {round(score, 2)}\n'

    return result_msg


def get_players_to_score(game, user_id):
    scores = game['scores']
    scores_by_current_user = filter(lambda score: score['by'] == user_id, scores)
    users_with_score = list(map(lambda s: s['to'], scores_by_current_user))
    users_with_score.append(user_id)

    all_users_ids = working_obj.keys()
    ids_to_score = set(all_users_ids) - set(users_with_score)

    return ids_to_score


def get_keyboard_with_players(players):
    keyboard = types.InlineKeyboardMarkup()
    for id in players:
        keyboard.row(types.InlineKeyboardButton(working_obj[id]['name'], callback_data=id))

    return keyboard


@bot.message_handler(commands=['rating'])
def handler(message):
    bot.send_message(message.chat.id, get_rating_msg())


@bot.callback_query_handler(func=lambda call: call.message.text == show_game_scores)
def handler(query):
    bot.send_message(query.message.chat.id, get_rating_msg(ObjectId(query.data)))


@bot.callback_query_handler(func=lambda call: call.message.text == choose_game_msg)
def handler(query):
    # When choose game
    game = db.games.find_one({'_id': ObjectId(query.data)})

    if not game:
        bot.send_message(query.message.chat.id, 'Спочатку виберу гру. Тисни /games')
        return

    working_obj[query.from_user.id]['game_id'] = ObjectId(query.data)

    players_to_score = get_players_to_score(game, query.from_user.id)

    if len(players_to_score) > 0:
        keyboard = get_keyboard_with_players(players_to_score)

        bot.send_message(query.message.chat.id, choose_player_msg, reply_markup=keyboard)
    else:
        bot.send_message(query.message.chat.id, f'За гру *{game["name"]}* ти вже поставив оцінки всім гравцям',
                         parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.message.text in [choose_player_msg, choose_rest_player_msg])
def handler(query):
    # When choose player for the game

    if not working_obj[query.from_user.id].get('game_id'):
        bot.send_message(query.message.chat.id, 'Ти не обрав гру! Тисни /games')
        return

    working_obj[query.from_user.id]['to_id'] = int(query.data)

    keyboard = types.InlineKeyboardMarkup()
    for r in range(2):
        keyboard.row(
            types.InlineKeyboardButton(r * 5 + 1, callback_data=r * 5 + 1),
            types.InlineKeyboardButton(r * 5 + 2, callback_data=r * 5 + 2),
            types.InlineKeyboardButton(r * 5 + 3, callback_data=r * 5 + 3),
            types.InlineKeyboardButton(r * 5 + 4, callback_data=r * 5 + 4),
            types.InlineKeyboardButton(r * 5 + 5, callback_data=r * 5 + 5),
        )

    bot.send_message(query.message.chat.id, choose_score_msg, reply_markup=keyboard)


def set_score(score, from_id, chat_id):
    if not working_obj[from_id].get('game_id'):
        bot.send_message(chat_id, 'Ти не обрав гру! Тисни /games')
        return

    to_id = working_obj[from_id].get('to_id')
    if not to_id:
        bot.send_message(chat_id, 'Ти не обрав гравця, для якого хочеш поставити оцінку!')
        return

    if score < 1 or score > 10:
        bot.send_message(chat_id, 'Оцінка може бути в діапазоні *[1, 10]*', parse_mode='markdown')
        return

    target_game = {'_id': working_obj[from_id]['game_id']}

    game = db.games.find_one(target_game)

    if any(map(lambda s: s['by'] == from_id and s['to'] == to_id, game['scores'])):
        bot.send_message(chat_id, f'Ти вже ставив оцінку грацю *{working_obj[to_id]["name"]}* за гру *{game["name"]}*',
                         parse_mode='markdown')
        return

    new_score = {
        'by': from_id,
        'score': score,
        'to': to_id
    }

    db.games.update_one(target_game, {'$push': {'scores': new_score}})

    game['scores'].append(new_score)

    rest_players = get_players_to_score(game, from_id)
    if len(rest_players) > 0:
        keyboard = get_keyboard_with_players(rest_players)

        bot.send_message(chat_id, choose_rest_player_msg, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, f'Круто! За гру *{game["name"]}* ти вже поставив оцінки всім гравцям',
                         parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.message.text == choose_score_msg)
def score_handler(query):
    # When choose score for player
    set_score(int(query.data), query.from_user.id, query.message.chat.id)


@bot.message_handler(func=lambda _: True)
def handler(message):
    try:
        score = float(message.text)
        set_score(score, message.from_user.id, message.chat.id)
    except ValueError:
        msg = "Невірний формат оцінки! Можливо спробуй через крапку.\nПриклади: '7', '8.5', 6.75"

        if not working_obj[message.from_user.id].get('game_id'):
            msg = 'Ти не обрав гру! Тисни /games'
        elif not working_obj[message.from_user.id].get('to_id'):
            msg = 'Ти не обрав гравця, для якого хочеш поставити оцінку!'

        bot.send_message(message.chat.id, msg)


if __name__ == '__main__':
    bot.polling(none_stop=True)
