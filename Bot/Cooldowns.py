from universal_funcs import get_request_backend, post_request_backend, put_request_backend, send_message, delete_message
import telepot
MAX_CONSECUTIVE_RESPONSES_AI = 7
remaining_responses_ai = {}

def sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language):
    sticker_seq = get_request_backend(f"stickers/{chat_id}")
    if 'error' in sticker_seq and sticker_seq['error'] == "Not Found":
        post_request_backend(f"stickers/{chat_id}", {"lastUsed": 0})
    else:
        last_used = int(sticker_seq['lastUsed']) + 1
        if last_used == int(stickerspamlimit):
            send_message(cookiebot, chat_id, "Cuidado com o flood de stickers", msg, language)
        if int(last_used) > int(stickerspamlimit):
            delete_message(cookiebot, telepot.message_identifier(msg))
        put_request_backend(f"stickers/{chat_id}", {"lastUsed": last_used})

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

def sticker_cooldown_updates(chat_id):
    put_request_backend(f"stickers/{chat_id}", {"lastUsed": 0})
