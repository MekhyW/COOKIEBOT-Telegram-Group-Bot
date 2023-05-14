from universal_funcs import *

def Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language):
    sticker_seq = GetRequestBackend(f"stickers/{chat_id}")
    if 'error' in sticker_seq and sticker_seq['error'] == "Not Found":
        PostRequestBackend(f"stickers/{chat_id}", {"lastUsed": 0})
    else:
        lastUsed = int(sticker_seq['lastUsed']) + 1
        if lastUsed == int(stickerspamlimit):
            Send(cookiebot, chat_id, "Cuidado com o flood de stickers", msg, language)
        if int(lastUsed) > int(stickerspamlimit):
            DeleteMessage(cookiebot, telepot.message_identifier(msg))
        PutRequestBackend(f"stickers/{chat_id}", {"lastUsed": lastUsed})

def StickerCooldownUpdates(msg, chat_id):
    PutRequestBackend(f"stickers/{chat_id}", {"lastUsed": 0})