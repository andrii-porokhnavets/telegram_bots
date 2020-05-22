import config
import telebot

bot = telebot.TeleBot(config.TOKEN)

see_results = '/show today members'
voted_answer = 'You have already voted! /show members'
voted_members = []
yes_list = {}
no_list = {}
maybe_list = {}


def get_name(user):
    first_name = user.first_name
    if first_name is None:
        first_name = ''

    last_name = user.last_name
    if last_name is None:
        last_name = ''

    name = first_name + ' ' + last_name
    if name == ' ':
        name = 'Unknown user'

    return name


@bot.message_handler(commands=['start'])
def start(message):
    answer = 'Hello, I am a Telegram bot created to help organization your meets\n' \
             'To find out how to use me press /help\n' \
             'To see today members press /show'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['help'])
def help_handler(message):
    answer = '/start = getting started \n' \
             '/yes = I will definitely be today\n' \
             '/no = I can`t today. Sorry!\n' \
             '/maybe = I am still thinking about it\n' \
             '/show = See today members'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['yes'])
def yes_handler(message):
    answer = 'Cool! We are waiting for you!\n' + see_results

    from_user = message.from_user
    if from_user.id not in voted_members:
        voted_members.append(from_user.id)
        yes_list[from_user.id] = get_name(from_user)
    else:
        answer = voted_answer

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['no'])
def no_handler(message):
    answer = 'Oh! We hope to see yor for the next time!\n' + see_results

    from_user = message.from_user
    if from_user.id not in voted_members:
        voted_members.append(from_user.id)
        no_list[from_user.id] = get_name(from_user)
    else:
        answer = voted_answer

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['maybe'])
def maybe_handler(message):
    answer = 'Came on! Let`s press /yes and don`t doubt!\n' + see_results

    from_user = message.from_user
    if from_user.id not in voted_members:
        voted_members.append(from_user.id)
        maybe_list[from_user.id] = get_name(from_user)
    else:
        answer = voted_answer

    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['show'])
def show_handler(message):
    answer = 'Yes: ' + ', '.join(yes_list.values()) + '\n'
    answer += 'No: ' + ', '.join(no_list.values()) + '\n'
    answer += 'Maybe: ' + ', '.join(maybe_list.values()) + '\n'

    bot.send_message(message.chat.id, answer)


if __name__ == "__main__":
    bot.polling()
