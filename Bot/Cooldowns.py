import datetime
from universal_funcs import send_message, delete_message
import telepot
MAX_CONSECUTIVE_RESPONSES_AI = 7
MAX_IMAGE_SEARCHES_DAILY = 180
MAX_IMAGE_SEARCHES_DAILY_PER_USER = 15
remaining_responses_ai = {}
remaining_image_searches = {}
last_used_sticker = {}

def sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language):
    if chat_id not in last_used_sticker:
        last_used_sticker[chat_id] = 0
    else:
        last_used = int(last_used_sticker[chat_id]) + 1
        if last_used == int(stickerspamlimit):
            send_message(cookiebot, chat_id, "Cuidado com o flood de stickers", msg, language)
        if int(last_used) > int(stickerspamlimit):
            delete_message(cookiebot, telepot.message_identifier(msg))
        last_used_sticker[chat_id] = last_used

def increase_remaining_responses_ai(user_id):
    if user_id in remaining_responses_ai:
        if remaining_responses_ai[user_id] < MAX_CONSECUTIVE_RESPONSES_AI:
            remaining_responses_ai[user_id] += 1
    else:
        remaining_responses_ai[user_id] = MAX_CONSECUTIVE_RESPONSES_AI

def decrease_remaining_responses_ai(user_id):
    if user_id in remaining_responses_ai:
        if remaining_responses_ai[user_id] > -MAX_CONSECUTIVE_RESPONSES_AI:
            remaining_responses_ai[user_id] -= 1
    else:
        remaining_responses_ai[user_id] = MAX_CONSECUTIVE_RESPONSES_AI - 1

def decrease_remaining_image_searches(user_id):
    today = datetime.datetime.now().date()
    if user_id in remaining_image_searches and remaining_image_searches[user_id]['date'] == today:
        if remaining_image_searches[user_id]['remaining'] > 0:
            remaining_image_searches[user_id]['remaining'] -= 1
    else:
        remaining_image_searches[user_id] = {'date': today, 'remaining': MAX_IMAGE_SEARCHES_DAILY_PER_USER - 1}
    if 'total_remaining' in remaining_image_searches and remaining_image_searches['total_remaining']['date'] == today:
        remaining_image_searches['total_remaining']['remaining'] -= 1
    else:
        remaining_image_searches['total_remaining'] = {'date': today, 'remaining': MAX_IMAGE_SEARCHES_DAILY - 1}

def sticker_cooldown_updates(chat_id):
    last_used_sticker[chat_id] = 0
