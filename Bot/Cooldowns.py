from universal_funcs import *

sentcooldownmessage = False

def Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language):
    sticker_seq = GetRequestBackend(f"stickers/{chat_id}")
    if 'error' in sticker_seq and sticker_seq['error'] == "Not Found":
        PostRequestBackend(f"stickers/{chat_id}", {"id": chat_id, "lastUsed": 0})
    else:
        lastUsed = int(sticker_seq['lastUsed'])
        if lastUsed == stickerspamlimit:
            Send(cookiebot, chat_id, "Cuidado com o flood de stickers.\nMantenham o chat com textos!", msg, language)
        if lastUsed > stickerspamlimit:
            DeleteMessage(cookiebot, telepot.message_identifier(msg))

def CmdCooldownUpdates(msg, chat_id, lastmessagetime):
    global sentcooldownmessage
    if float(lastmessagetime)+60 < ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
        sentcooldownmessage = False

def StickerCooldownUpdates(msg, chat_id):
    PutRequestBackend(f"stickers/{chat_id}", {"lastUsed": 0})

def CooldownAction(cookiebot, msg, chat_id, language):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        Send(cookiebot, chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", msg, language)
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        DeleteMessage(cookiebot, telepot.message_identifier(msg))