import telebot     # run telegram bot
from telebot import types
import soundfile as sf
import random
import numpy
from datetime import datetime # generate log
def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + " " + text)
    random_integer_array 

if __name__ == "__main__":
    with open("creds/digits_2021_dataset_bot.txt", "r") as f:
        audio_digits_dataset_creds = f.read().strip() # "  hello world \t\n" -> "hello world"
    bot = telebot.TeleBot(audio_digits_dataset_creds)
    print(audio_digits_dataset_creds)
    request = "Пожалуйста, произнесите заданные цифры вслух с интервалом в 1 секунду "
    random_integer_array = numpy.random.randint(0, 10, 5)
    users_last_task = {}
     
    @bot.message_handler(commands=['start'])
    def hello(msg):
        global random_integer_array
        global users_last_task
        random_integer_array = numpy.random.randint(0, 10, 5)
        users_last_task[msg.from_user.id] = random_integer_array
        bot.send_message(msg.chat.id, request + str(random_integer_array))

    @bot.message_handler(content_types=['voice']) # decorator
    def get_text_messages(message):
        user_id = message.from_user.id
        user_name = message.from_user.username  
        global random_integer_array  
        global users_last_task
                                                                                                                                                                                                                          
        log_text = "User ({0}): {1}".format(user_name, str(message.voice))
        log(log_text)

        tele_file = bot.get_file(message.voice.file_id)
        log_text = "User ({0}): {1}".format(user_name, str(tele_file))
        log(log_text)
        ogg_data = bot.download_file(tele_file.file_path)
        print(random_integer_array)
        file_name = str(users_last_task[user_id][0]) + "_" + str(users_last_task[user_id][1]) + "_"\
        + str(users_last_task[user_id][2]) + "_" + str(users_last_task[user_id][3]) + "_"\
        + str(users_last_task[user_id][4])
        with open("dataset/ogg1/" + file_name +".ogg", "wb") as f:
            f.write(ogg_data)
        random_integer_array = numpy.random.randint(0, 10, 5)
        users_last_task[user_id] = random_integer_array

        bot.send_message(user_id, request + str(random_integer_array))
        print(random_integer_array)
    bot.polling(none_stop=True, interval=0)