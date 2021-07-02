import telebot     # run telegram bot
import os
import numpy as np
from datetime import datetime # generate log
import pickle
import subprocess
from scipy.io.wavfile import read
import librosa


def predict(user_id, model):
    dataset = "data1/splitted"
    audios = []
    sample_rate = 0
    for file in sorted(os.listdir(dataset)):
        if file.split("#")[0] == str(user_id):
            file_path = dataset + "/" + file
            sample_rate, audio = read(file_path)
            audios.append(audio)
            os.remove(file_path)
    max_duration_sec = 0.6
    max_duration = round(max_duration_sec * sample_rate)
    features = []
    features_flatten = []
    print(audios)
    for audio in audios:
        if len(audio) < max_duration:
            audio = np.pad(audio, (0, max_duration - len(audio)), constant_values=0)
        if len(audio) > max_duration:
            continue
        feature = librosa.feature.melspectrogram(audio.astype(float), sample_rate, n_mels=16, fmax=1000)
        features.append(feature)
        features_flatten.append(feature.reshape(-1))
    labels_test_predicted = model.predict(X=features_flatten)
    print(labels_test_predicted)
    return labels_test_predicted    


def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + " " + text)

if __name__ == "__main__":
    with open("models/model.pkl", "rb") as f1:
        model = pickle.load(f1)
    with open("creds/evas_predictor_bot.txt", "r") as f:
        audio_digits_dataset_creds = f.read().strip() # "  hello world \t\n" -> "hello world"
    bot = telebot.TeleBot(audio_digits_dataset_creds)
    print(audio_digits_dataset_creds)
    request = "Пожалуйста, произнесите цифры вслух с интервалом в 1 секунду "
    @bot.message_handler(commands=['start'])
    def hello(msg):
        bot.send_message(msg.chat.id, request)

    @bot.message_handler(content_types=['voice']) # decorator
    def get_text_messages(message):
        user_id = message.from_user.id
        user_name = message.from_user.username                                                                                                                                                                                          
        log_text = "User ({0}): {1}".format(user_name, str(message.voice))
        log(log_text)

        tele_file = bot.get_file(message.voice.file_id)
        ogg_data = bot.download_file(tele_file.file_path)
        with open("data/raw/" + str(user_id) +".ogg", "wb") as f:
            f.write(ogg_data)
        try:
            subprocess.check_call(["ffmpeg", "-y", "-i", "data/raw/" + str(user_id) + ".ogg", "data/wav/" + str(user_id) + ".wav"])
            subprocess.check_call(["python", "vad.py", "data/wav/" + str(user_id) + ".wav", "0.2", "0.015",  "data/splitted", "-normal"])
            log_text = "User ({0}): {1}".format(user_name, str(tele_file))
            log(log_text)
            labels_test_predicted = predict(user_id, model)
            bot.send_message(user_id, str(labels_test_predicted))
        except Exception:
            bot.send_message(user_id, "Извините, не удалось распознать цифры")    

    bot.polling(none_stop=True, interval=0)