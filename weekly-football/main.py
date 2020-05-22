import telebot
import answers
from config import *

bot = telebot.TeleBot(TOKEN)

results = {
    CASE_YES: [],
    CASE_NO: [],
    CASE_MAYBE: [],
}
voted_user_ids = []


def get_name(user):
    last_name = user.last_name or ''

    return (user.first_name + ' ' + last_name).strip()


@bot.message_handler(commands=['start', 'help'])
def init_handler(message):
    bot.send_message(message.chat.id, answers.INIT)


@bot.message_handler(commands=['yes', 'no', 'maybe'])
def yes_no_maybe_handler(message):
    text = message.text or '/maybe'
    cmd = text[1:]

    answer = answers.YES_NO_MAYBE[cmd]

    if message.from_user.id in voted_user_ids:
        # change answer
        answer = answers.VOTED
    else:
        # mark user as voted
        voted_user_ids.append(message.from_user.id)
        # store result
        results[cmd].append(get_name(message.from_user))

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['show'])
def result_handler(message):
    answer = 'YES: ' + ', '.join(results[CASE_YES]) + '\n' \
             'NO: ' + ', '.join(results[CASE_NO]) + '\n' \
             'MAYBE: ' + ', '.join(results[CASE_MAYBE])

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['change'])
def result_handler(message):
    answer = answers.CHANGE_FOR_NOT_VOTED

    if message.from_user.id in voted_user_ids:
        voted_user_ids.remove(message.from_user.id)

        for case in [CASE_YES, CASE_NO, CASE_MAYBE]:
            if get_name(message.from_user) in results[case]:
                results[case].remove(get_name(message.from_user))

        answer = answers.CHANGE_FOR_VOTED

    bot.send_message(message.chat.id, answer)


if __name__ == '__main__':
    bot.polling()
