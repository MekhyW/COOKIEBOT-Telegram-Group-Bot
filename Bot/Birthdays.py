import random
import datetime
import time
import threading
import math
from universal_funcs import get_request_backend, delete_request_backend, send_message, send_photo
from UserRegisters import get_members_chat
from Configurations import get_config
from SocialContent import get_profile_image
import cv2
import numpy as np

def birthday(cookiebot, current_date_utc, msg=None, manual_chat_id=None, language=None):
    current_date_formatted = datetime.datetime.fromtimestamp(current_date_utc, tz=datetime.timezone.utc).strftime('%Y-%m-%d')
    if manual_chat_id and len(msg['text'].split()) == 1:
        text = i18n.get("bday.title", lang=language)
        send_message(cookiebot, manual_chat_id, text, msg)
        return
    bd_users = get_request_backend(f"users?birthdate={current_date_formatted}")
    groups = get_request_backend('registers') if not manual_chat_id else [get_request_backend(f"registers/{manual_chat_id}")]
    for group in groups:
        try:
            _, _, _, _, _, funfunctions, _, language, _, _, _, _, _ = get_config(cookiebot, group['id'])
            if not funfunctions:
                continue
        except TypeError:
            continue
        chatinfo = cookiebot.getChat(group['id'])
        users_in_group = get_members_chat(cookiebot, group['id'])
        bd_users_in_group = []
        is_new_birthday_pinned, is_old_birthday_pinned = False, False
        if 'pinned_message' in chatinfo and 'caption' in chatinfo['pinned_message'] and any(x in chatinfo['pinned_message']['caption'].lower() for x in ['feliz aniversário!', 'happy birthday!', 'feliz cumpleaños!']):
            is_new_birthday_pinned, is_old_birthday_pinned = (True, False) if current_date_formatted in chatinfo['pinned_message']['caption'] else (False, True)
        for bd_user in bd_users:
            if 'username' not in bd_user or bd_user['username'] not in [x['user'] for x in users_in_group]:
                continue
            try:
                full_user = cookiebot.getChatMember(group['id'], bd_user['id'])['user']
                bd_users_in_group.append(full_user)
            except:
                delete_request_backend(f"registers/{group['id']}/users", {"user": bd_user})
        if manual_chat_id and msg and 'text' in msg:
            bd_users_in_group.extend([{'username': x.replace('@', '')} for x in msg['text'].split() if x.startswith('@')])
        #if is_old_birthday_pinned or (is_new_birthday_pinned and manual_chat_id):
        #    cookiebot.unpinChatMessage(group['id'], chatinfo['pinned_message']['message_id'])
        if (len(bd_users_in_group) and not is_new_birthday_pinned) or manual_chat_id:
            collage_image = make_birthday_collage(bd_users_in_group)
            collage_caption = make_birthday_caption(bd_users_in_group, current_date_formatted)
            with open(collage_image, 'rb') as final_img:
                collage_message_id = send_photo(cookiebot, group['id'], final_img, caption=collage_caption, language=language)
            try:
                cookiebot.pinChatMessage(group['id'], collage_message_id)
            except Exception as e:
                pass
            cookiebot.sendMessage(group['id'], '🎂')
            timer_next_birthdays = threading.Timer(900, next_birthdays, args=(cookiebot, msg, group['id'], language, current_date_utc))
            timer_next_birthdays.start()
        if manual_chat_id:
            return
        time.sleep(3)

def make_birthday_collage(bd_users_in_group):
    collage_images = []
    for bd_user in bd_users_in_group:
        if 'username' in bd_user:
            try:
                user_img = get_profile_image(bd_user['username'])
                user_img = cv2.imdecode(np.asarray(bytearray(user_img.read()), dtype="uint8"), cv2.IMREAD_COLOR)
            except:
                user_img = cv2.imread('Static/No_Image_Available.jpg', cv2.IMREAD_COLOR)
        else:
            user_img = cv2.imread('Static/No_Image_Available.jpg', cv2.IMREAD_COLOR)
        collage_images.append(user_img)
    n = len(collage_images)
    width = int(math.ceil(math.sqrt(n)))
    height = int(math.ceil(n / float(width)))
    collage_size = (height * collage_images[0].shape[0], width * collage_images[0].shape[1])
    collage = np.zeros((collage_size[0], collage_size[1], 3), dtype=np.uint8)
    for i in range(n):
        row = int(i / width)
        col = i % width
        y_start = row * collage_images[i].shape[0]
        x_start = col * collage_images[i].shape[1]
        y_end = y_start + collage_images[i].shape[0]
        x_end = x_start + collage_images[i].shape[1]
        collage[y_start:y_end, x_start:x_end] = collage_images[i]
    confetti = cv2.imread('Static/Confetti.png', cv2.IMREAD_COLOR)
    confetti = cv2.resize(confetti, (collage.shape[1], collage.shape[0]))
    transparent_indices = np.where(confetti[:, :, -1] == 0)
    confetti[transparent_indices] = collage[transparent_indices]
    cv2.imwrite("birthday.png", confetti)
    return "birthday.png"

def make_birthday_caption(bd_users_in_group, current_date_formatted):
    users_str = ""
    for index in range(len(bd_users_in_group)):
        users_str += " e " if index > 0 else ""
        users_str += f"@{bd_users_in_group[index]['username']}" if 'username' in bd_users_in_group[index] else f"{bd_users_in_group[index]['firstName']} {bd_users_in_group[index]['lastName']}"
        caption = i18n.get_choice("bday.cta", lang=language, names=users_str)
    caption += i18n.get("bday.closing", lang=language, date=current_date_formatted)
    return caption

def next_birthdays(cookiebot, msg, chat_id, language, current_date_utc):
    text = i18n.get("bday.next", lang=language)
    for offset in range(1, 5):
        target_date = datetime.datetime.utcfromtimestamp(current_date_utc) + datetime.timedelta(days=offset)
        target_date_formatted = target_date.strftime('%Y-%m-%d')
        bd_users = get_request_backend(f"users?birthdate={target_date_formatted}")
        text += f"{offset} dias:\n"
        for bd_user in bd_users:
            text += f"@{bd_user['username']}\n" if 'username' in bd_user else f"{bd_user['firstName']} {bd_user['lastName']}\n"
        if not len(bd_users):
            text += "- \n"
        text += "\n"
    send_message(cookiebot, chat_id, text)