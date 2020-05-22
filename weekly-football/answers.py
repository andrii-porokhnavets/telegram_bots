from config import *

INIT = 'Привіт, я Telegram бот, створений для допомоги з організацією гри у футзал. \n' \
             f'Для ознайомлення з правилами жми {COMMAND_HELP} чи {COMMAND_START}\n' \
             f'{COMMAND_YES} = ти точно будеш на футболі \n' \
             f'{COMMAND_NO} = ти сьогодні не можеш і тебе не буде\n' \
             f'{COMMAND_MAYBE} = я ще не знаю, але можливо буду\n' \
             f'{COMMAND_SHOW} = глянути результат\n' \
             f'{COMMAND_CHANGE} = змінити рішення'

VOTED = 'Ти вже відповідав.\n' \
        f'Хочеш змінити свій вибір? Жми {COMMAND_CHANGE}\n' \
        f'Подитися хто буде? Жми {COMMAND_SHOW}'

YES_NO_MAYBE = {
    CASE_YES: 'Круто! Ти записаний у список на футбол сьогодні!',
    CASE_NO: 'Ну як хочеш!',
    CASE_MAYBE: 'Давай думай швидше, бо якщо не буде достатньо людей, то ти йдеш!',
}

CHANGE_FOR_VOTED = 'Окей! Давай вибирай ще раз\n' \
                   f'{COMMAND_YES} {COMMAND_NO} {COMMAND_MAYBE}'
CHANGE_FOR_NOT_VOTED = 'Ти ще не вибирав нічого. Що ти хочеш змінювати? Давай вибирай\n' \
                     f'{COMMAND_YES} {COMMAND_NO} {COMMAND_MAYBE}'
