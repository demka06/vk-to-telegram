import traceback
from datetime import datetime
from pytz import timezone
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import telebot
import urllib.request
import os

bot = telebot.TeleBot(str(os.environ.get("TG-TOKEN")))
# ------------- [ CONNECT TO VK ] -----------
token = str(os.environ.get("VK-TOKEN"))
vk_session = vk_api.VkApi(token=token)  # Обработка access_token
longpoll = VkLongPoll(vk_session)  # Данные для работы в сообществе
vk = vk_session.get_api()  # For api requests
a = 0
track = ""


def send_audio(file=None, title=None):
    audios = open(file, 'rb')
    bot.send_audio(chat_id=500550780, audio=audios, title=title)
    audios.close()


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_user and not event.from_me:
                name = vk.users.get(user_ids=event.user_id)[0]
                now_utc = datetime.now(timezone('UTC'))
                time = now_utc.astimezone(timezone('Europe/Moscow'))
                attachs = ""
                if len(event.attachments) != 0:
                    attach = vk.messages.getById(message_ids=event.message_id)['items'][0]["attachments"]
                    for i in attach:

                        if i['type'] == "photo":
                            pick = i["photo"]['sizes'][len(i["photo"]['sizes']) - 1]['url']
                            attachs += f"\n<a href='{pick}'>[ПИКЧА]</a>"
                        if i['type'] == "video":
                            vid, us = i["video"]["id"], i["video"]["owner_id"]
                            video = vk.video.get(owner_id=us, videos=str(us) + "_" + str(vid))['items'][0]['player']
                            attachs += f"\n<a href='{video}'>[ВИДЕО]</a>"
                        if i["type"] == "sticker":
                            stick = i["sticker"]['images'][len(i["sticker"]['images']) - 1]['url']
                            print(stick)
                            attachs += f"\n<a href='{stick}'>[СТИК]</a>"
                        if i["type"] == "audio_message":
                            a = 1
                            msg_url = i["audio_message"]["link_mp3"]
                            urllib.request.urlretrieve(msg_url, "гс.mp3")
                            attachs += f"\n<a href='{msg_url}'>[ГС]</a>"
                        if i["type"] == "audio":
                            a = 2
                            audio_id = f'{i["audio"]["owner_id"]}_{i["audio"]["id"]}'
                            audio = vk.audio.getById(audios=audio_id)
                            audio_url = audio[0]["url"]
                            track = f"{audio[0]['artist']} - {audio[0]['title']}"
                            urllib.request.urlretrieve(audio_url, "аудио.mp3")
                            attachs += f"\n<a href='{audio_url}'>[МУЗЯКА]</a>"
                        if i["type"] == "doc":
                            doc_url = i["doc"]["url"]
                            attachs += f"\n<a href='{doc_url}'>[ДОКУМЕНТ]</a>"

                msg = f"""[{str(time).split(".")[0]}]
Отправитель: <a href="vk.com/id{event.user_id}">{name['first_name']} {name['last_name']}</a>
Текст: {event.text}
Вложения: {attachs}"""
                bot.send_message(500550780, msg, parse_mode="HTML")
                if a == 1:
                    send_audio("гс.mp3")
                    a = 0
                elif a == 2:
                    send_audio("аудио.mp3", track)
                    a = 0
    except Exception:
        print(traceback.format_exc())
