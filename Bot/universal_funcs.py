WolframAPP_ID = ''
googleAPIkey = ''
searchEngineCX = ''
cookiebotTOKEN = ''
bombotTOKEN = ''
mekhyID = 780875868
import os, math, random, time, datetime, json, requests, re, sys, traceback
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

def wait_open(filename):
    if os.path.exists(filename):
        while True:
            try:
                text = open(filename, 'r')
                text.close()
                break
            except IOError:
                pass

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