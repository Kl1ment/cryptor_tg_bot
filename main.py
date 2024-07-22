import telebot
from telebot import types
import backend
import pickle
from random import randint
from config import TOKEN, ADMIN_ID

token = TOKEN
bot = telebot.TeleBot(token)
admin = [ADMIN_ID]
text = ''
image = None


@bot.message_handler(commands=['start'])
def start(message):
    try:
        with open('all_users.dat', 'rb+') as f:
            dict_of_user = pickle.load(f)
            if not (message.chat.id in dict_of_user):
                dict_of_user[message.chat.id] = {'username': message.chat.username,
                                                 'first_name': message.chat.first_name,
                                                 'last_name': message.chat.last_name}
            f.seek(0)
            pickle.dump(dict_of_user, f)
    except FileNotFoundError:
        dict_of_user = {message.chat.id: {'username': message.chat.username,
                                          'first_name': message.chat.first_name,
                                          'last_name': message.chat.last_name}}
        with open('all_users.dat', 'wb') as f:
            pickle.dump(dict_of_user, f)

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton(text='/help')
    btn_get_image = types.KeyboardButton(text='/get_image')
    keyboard.add(btn_get_image, btn_help)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAICx2U6Z7ktazUPZA8zO3h_vryRFyeIAALTAANWnb0K9TKPl9US-T0wBA',
                     reply_markup=keyboard)
    begin(message)


@bot.message_handler(commands=['begin'])
def begin(message):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_btn_encrypt = types.InlineKeyboardButton(text='Encrypt', callback_data='encrypt')
    inline_btn_decrypt = types.InlineKeyboardButton(text='Decrypt', callback_data='decrypt')
    inline_keyboard.add(inline_btn_encrypt, inline_btn_decrypt)
    bot.send_message(message.chat.id, "What would you like to do?", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'encrypt':
            encrypt(call.message)
        if call.data == 'decrypt':
            decrypt(call.message)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id, '===============================\n'
                                      'Where can I get an image in BMP format?\n'
                                      '\n'
                                      '1) You can try to find and download '
                                      'a BMP file from the Internet.\n'
                                      '2) You can create a BMP file yourself. '
                                      'Take any image and open it with Paint.'
                                      'Then save the file as BMP24.\n'
                                      '3) You can use the /get_image command and '
                                      'get our image.\n'
                                      '\n'
                                      '===============================\n'
                                      'How can I encrypt the text into the image?\n'
                                      '\n'
                                      'Use the /encrypt command. Then send '
                                      'this Bot the text you want to encrypt. '
                                      'In the next message, send in BMP24 format '
                                      'the image you want to use.\n'
                                      '\n'
                                      '===============================\n'
                                      'How can I decrypt a text from the image?\n'
                                      '\n'
                                      'Use the /decrypt command. Then send '
                                      'in BMP24 format the image, which you receive'
                                      'from anyone.\n')
    begin(message)


@bot.message_handler(commands=['encrypt'])
def encrypt(message):
    bot.send_message(message.chat.id, 'Write text for encryption')
    bot.register_next_step_handler(message, get_text_to_encrypt)


def get_text_to_encrypt(message):
    global text
    bot.send_message(message.chat.id, 'Alright! Now send me an image file in BMP24 format for encryption')
    text = message.text
    bot.register_next_step_handler(message, get_img_to_encrypt)


def get_img_to_encrypt(message):
    global image
    global text
    try:
        image_info = bot.get_file(message.document.file_id)
        image = bot.download_file(image_info.file_path)

        result, new_image = backend.encrypt(text, 2, image)
        bot.send_message(message.chat.id, result)
        if new_image:
            with open('num_image.dat', 'rb+') as f:
                num_image = pickle.load(f)
                num_image += 1
                bot.send_document(message.chat.id, new_image, visible_file_name=f'image{num_image}.bmp')
                f.seek(0)
                pickle.dump(num_image, f)
    except AttributeError:
        bot.send_message(message.chat.id, "You haven't sent file")
    finally:
        begin(message)


@bot.message_handler(commands=['decrypt'])
def decrypt(message):
    bot.send_message(message.chat.id, 'Send me an image file in BMP24 format for decryption')
    bot.register_next_step_handler(message, get_img_to_decrypt)


def get_img_to_decrypt(message):
    try:
        image_info = bot.get_file(message.document.file_id)
        encrypt_image = bot.download_file(image_info.file_path)
        result = backend.decrypt(2, encrypt_image)
        bot.send_message(message.chat.id, result)
    except AttributeError:
        bot.send_message(message.chat.id, "You haven't sent file")
    finally:
        begin(message)


@bot.message_handler(commands=['get_image'])
def get_image(message):
    num_of_image = randint(0, 9)
    with open(f'image/image{num_of_image}.bmp', 'rb') as f:
        image_file = f.read()
    bot.send_document(message.chat.id, image_file, visible_file_name=f'bot_image{num_of_image}.bmp')
    begin(message)


# @bot.message_handler(commands=['stop'])
# def stop_bot(message):
#     if message.chat.id in admin:
#         bot.stop_bot()


@bot.message_handler(content_types=['text'])
def tolk_about(message):
    bot.send_message(message.chat.id, "I'm sorry, I'd like to talk to you, "
                                      "but I'm just a Bot and I can't talk")
    begin(message)


if __name__ == '__main__':
    bot.infinity_polling()
