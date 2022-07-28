googleAPIkey = ''
newsAPIkey = ''
searchEngineCX = ''
smalltalkKey = ''
cookiebotTOKEN = ''
bombotTOKEN = ''
mekhyID = 780875868
import os, math, numpy, random, time, datetime, re, sys, traceback
import urllib, json, requests
from bs4 import BeautifulSoup
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
import googletrans
translator = googletrans.Translator()

def Send(cookiebot, chat_id, text, msg_to_reply=None, language="pt"):
    cookiebot.sendChatAction(chat_id, 'typing')
    if language == 'eng':
        text = translator.translate(text, dest='en').text
    elif language == 'es':
        text = translator.translate(text, dest='es').text
    if msg_to_reply:
        reply_id = msg_to_reply['message_id']
        cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id)
    else:
        cookiebot.sendMessage(chat_id, text)

def wait_open(filename):
    if os.path.exists(filename):
        try:
            text = open(filename, 'r')
            text.close()
        except IOError:
            time.sleep(1)

def DeleteMessage(cookiebot, identifier):
    try:
        cookiebot.deleteMessage(identifier)
    except Exception as e:
        print(e)

def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False