from universal_funcs import *
max_consecutive_responses_ai = 7
remaining_responses_ai = {}

def sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language):
    sticker_seq = get_request_backend(f"stickers/{chat_id}")
    if 'error' in sticker_seq and sticker_seq['error'] == "Not Found":
        post_request_backend(f"stickers/{chat_id}", {"lastUsed": 0})
    else:
        lastUsed = int(sticker_seq['lastUsed']) + 1
        if lastUsed == int(stickerspamlimit):
            send_message(cookiebot, chat_id, "Cuidado com o flood de stickers", msg, language)
        if int(lastUsed) > int(stickerspamlimit):
            delete_message(cookiebot, telepot.message_identifier(msg))
        put_request_backend(f"stickers/{chat_id}", {"lastUsed": lastUsed})

def increase_remaining_responses_ai(user_id):
    if user_id in remaining_responses_ai:
        if remaining_responses_ai[user_id] < max_consecutive_responses_ai:
            remaining_responses_ai[user_id] += 1
    else:
        remaining_responses_ai[user_id] = max_consecutive_responses_ai

def decrease_remaining_responses_ai(user_id):
    if user_id in remaining_responses_ai:
        if remaining_responses_ai[user_id] > -max_consecutive_responses_ai:
            remaining_responses_ai[user_id] -= 1
    else:
        remaining_responses_ai[user_id] = max_consecutive_responses_ai - 1

def sticker_cooldown_updates(msg, chat_id):
    put_request_backend(f"stickers/{chat_id}", {"lastUsed": 0})
