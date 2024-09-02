from universal_funcs import *
from Configurations import *
from UserRegisters import *
import sqlite3
from price_parser import Price
import html
publisher_db = sqlite3.connect('Publisher.db', check_same_thread=False)
publisher_cursor = publisher_db.cursor()
publisher_cursor.execute("CREATE TABLE IF NOT EXISTS publisher (name TEXT, days INT, next_time TEXT, target_chat_id INT, postmail_chat_id INT, second_chatid INT, postmail_message_id INT, second_messageid INT, origin_userid INT)")
publisher_db.commit()
cache_posts = {}
postmail_chat_link = "https://t.me/CookiebotPostmail"
postmail_chat_id = -1001869523792
approval_chat_id = -1001659344607
url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

def AskPublisher(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'typing')
    if language == "pt":
        answer = "Divulgar postagem?"
    else:
        answer = "Share post?"
    Send(cookiebot, chat_id, answer, msg_to_reply=msg, 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️",callback_data=f"SendToApprovalPub {msg['forward_from_chat']['id']} {chat_id} {msg['forward_from_message_id']} {msg['message_id']}")],
            [InlineKeyboardButton(text="❌",callback_data='DenyPub')]
        ]
    ))
    if 'photo' in msg:
        media_type = 'photo'
        media_id = msg['photo'][-1]['file_id']
    elif 'video' in msg:
        media_type = 'video'
        media_id = msg['video']['file_id']
    elif 'animation' in msg:
        media_type = 'animation'
        media_id = msg['animation']['file_id']
    elif 'document' in msg:
        media_type = 'animation'
        media_id = msg['document']['file_id']
    caption_entities = []
    if 'caption_entities' in msg:
        for entity in msg['caption_entities']:
            caption_entities.append(entity)
    cache_posts[str(msg['forward_from_message_id'])] = {media_type: media_id, 'caption': msg['caption'], 'caption_entities': caption_entities}

def AskApproval(cookiebot, query_data, from_id, isAlternate=0):
    origin_chatid = query_data.split()[1]
    second_chatid = query_data.split()[2]
    origin_messageid = query_data.split()[3]
    second_messageid = query_data.split()[4]
    origin_userid = from_id
    Forward(cookiebot, approval_chat_id, second_chatid, second_messageid, isAlternate=isAlternate)
    Send(cookiebot, approval_chat_id, 'Approve post?', 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️ 7 days",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 7 {second_messageid}')],
            [InlineKeyboardButton(text="✔️ 3 days",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 3 {second_messageid}')],
            [InlineKeyboardButton(text="✔️ 1 day",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 1 {second_messageid}')],
            [InlineKeyboardButton(text="❌",callback_data=f'DenyPub {origin_messageid}')]
        ]
    ))

def create_job(hour, minute, name, days, target_chat_id, postmail_chat_id, second_chatid, postmail_message_id, second_messageid, origin_userid):
    current_time = datetime.datetime.now()
    if current_time.hour < hour or (current_time.hour == hour and current_time.minute < minute):
        next_time = str(datetime.datetime(current_time.year, current_time.month, current_time.day, hour, minute))
    else:
        next_time = str(datetime.datetime(current_time.year, current_time.month, current_time.day, hour, minute) + datetime.timedelta(days=1))
    publisher_cursor.execute("INSERT INTO publisher VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, days, next_time, target_chat_id, postmail_chat_id, second_chatid, postmail_message_id, second_messageid, origin_userid))
    publisher_db.commit()
    print(f'Created job: {name}')
    return name

def list_jobs():
    publisher_cursor.execute("SELECT * FROM publisher")
    jobs = []
    for row in publisher_cursor.fetchall():
        job = {
            'name': row[0],
            'days': row[1],
            'next_time': row[2],
            'target_chat_id': row[3],
            'postmail_chat_id': row[4],
            'second_chatid': row[5],
            'postmail_message_id': row[6],
            'second_messageid': row[7],
            'origin_userid': row[8]
        }
        jobs.append(job)
    return jobs

def delete_job(job_name):
    publisher_cursor.execute("DELETE FROM publisher WHERE name = ?", (job_name,))
    publisher_db.commit()
    print(f'Deleted job: {job_name}')
    return job_name

def edit_job_data(job_name, param, value):
    publisher_cursor.execute(f"UPDATE publisher SET {param} = ? WHERE name = ?", (value, job_name))
    publisher_db.commit()
    print(f'Edited job: {job_name}')
    return job_name

def ConvertPricesinText(text, code_target):
    if (code_target == 'BRL') and any([x in text for x in ('R$', 'BRL', 'Reais', 'reais')]):
        return text
    final_text = ''
    text = text.replace('Reais', 'R$').replace('reais', 'R$')
    for paragraph in text.split('\n'):
        amount = 0
        currency = None
        for word in paragraph.split():
            parsed = Price.fromstring(word, currency_hint='usd')
            if parsed.amount is not None and parsed.amount_float > amount:
                amount = parsed.amount_float
            if parsed.currency is not None:
                currency = parsed.currency
        if amount == 0 or currency is None:
            final_text += f"{paragraph}\n"
            continue
        if currency in ('$', 'US$', 'USD', 'U$'):
            code_from = 'USD'
        elif currency in ('€', 'EUR'):
            code_from = 'EUR'
        elif currency in ('£', 'GBP'):
            code_from = 'GBP'
        elif currency in ('R$', 'BRL'):
            code_from = 'BRL'
        elif currency in ('¥', 'JPY'):
            code_from = 'JPY'
        elif currency in ('C$', 'CAD'):
            code_from = 'CAD'
        elif currency in ('A$', 'AUD'):
            code_from = 'AUD'
        elif currency in ('ARS'):
            code_from = 'ARS'
        else:
            code_from = currency
        if code_from == code_target:
            return text
        try:
            rate_url = f"https://v6.exchangerate-api.com/v6/{exchangerate_key}/latest/{code_from}"
            rate = json.loads(requests.get(rate_url).text)['conversion_rates'][code_target]
            converted = round(amount * rate, 2)
            final_text += f"{paragraph} ({code_target} ≈{converted})\n"
        except Exception as e:
            print(e)
            final_text += f"{paragraph}\n"
    return final_text

def remove_emojis_from_ends(input_string):
    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F"
        r"\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F"
        r"\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+"
    )
    while emoji_pattern.match(input_string):
        input_string = input_string[1:]
    while emoji_pattern.match(input_string[::-1]):
        input_string = input_string[:-1]
    return input_string

def PreparePost(cookiebot, origin_messageid, origin_chat, origin_user):
    cached_post = cache_posts[origin_messageid]
    inline_keyboard = []
    inline_keyboard.append([InlineKeyboardButton(text=origin_chat['title'], url=f"https://t.me/{origin_chat['username']}")])
    for url in set(re.findall(url_regex, cached_post['caption'])):
        name = url[0]
        if name.endswith('/'):
            name = name[:-1]
        name = name.replace('www.', '').replace('http://', '').replace('https://', '')
        if len(name) and len(url) and url != f"https://t.me/{origin_chat['username']}":
            url_no_emojis_on_ends = remove_emojis_from_ends(url[0])
            inline_keyboard.append([InlineKeyboardButton(text=name, url=url_no_emojis_on_ends, parse_mode='HTML')])
            cached_post['caption'] = cached_post['caption'].replace(url[0], url_no_emojis_on_ends)
    caption_new = emojis_to_numbers(cached_post['caption'])
    for entity in cached_post['caption_entities']:
        if 'url' in entity and len(entity['url']) and len(inline_keyboard) < 5:
            name = entity['url']
            if name.endswith('/'):
                name = name[:-1]
            name = name.replace('www.', '').replace('http://', '').replace('https://', '')
            inline_keyboard.append([InlineKeyboardButton(text=name, url=entity['url'])])
    if origin_user is not None and 'Mekhy' not in origin_user['first_name']:
        inline_keyboard.append([InlineKeyboardButton(text=origin_user['first_name'], url=f"https://t.me/{origin_user['username']}")])
    inline_keyboard.append([InlineKeyboardButton(text="Mural 📬", url=postmail_chat_link)])
    caption_pt = GoogleTranslator(source='auto', target='pt').translate(caption_new)
    caption_en = GoogleTranslator(source='auto', target='en').translate(caption_new)
    caption_pt = html.escape(ConvertPricesinText(caption_pt, 'BRL'))
    caption_en = html.escape(ConvertPricesinText(caption_en, 'USD'))
    if 'photo' in cached_post:
        sent_pt = SendPhoto(cookiebot, postmail_chat_id, cached_post['photo'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
        sent_en = SendPhoto(cookiebot, postmail_chat_id, cached_post['photo'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
    elif 'video' in cached_post:
        sent_pt = cookiebot.sendVideo(chat_id=postmail_chat_id, video=cached_post['video'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
        sent_en = cookiebot.sendVideo(chat_id=postmail_chat_id, video=cached_post['video'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
    elif 'animation' in cached_post:
        sent_pt = cookiebot.sendAnimation(chat_id=postmail_chat_id, animation=cached_post['animation'], caption=caption_pt, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
        sent_en = cookiebot.sendAnimation(chat_id=postmail_chat_id, animation=cached_post['animation'], caption=caption_en, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))['message_id']
    cache_posts.pop(origin_messageid)
    return sent_pt, sent_en

def DenyPost(cookiebot, query_data):
    if len(query_data.split()) < 2:
        return
    origin_messageid = query_data.split()[1]
    cache_posts.pop(origin_messageid)

def SchedulePost(cookiebot, query_data):
    approve, origin_chatid, second_chatid, origin_messageid, origin_userid, days, second_messageid = query_data.split()[:7]
    origin_chat = cookiebot.getChat(origin_chatid)
    try:
        origin_user = cookiebot.getChatMember(origin_chatid, origin_userid)['user']
    except:
        origin_user = None
    sent_pt, sent_en = PreparePost(cookiebot, origin_messageid, origin_chat, origin_user)
    jobs = list_jobs()
    for job in jobs:
        if job['name'].split('-->')[0].strip() == origin_chat['title'].strip():
            delete_job(job['name'])
            jobs.remove(job)
    answer = f"Post set for the following times ({days} days):\n"
    answer += "NOW - Cookiebot Mural 📬\n"
    for group in GetRequestBackend('registers'):
        group_id = group['id']
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = GetConfig(cookiebot, group_id)
        if not publisherpost:
            continue
        if publisherMembersOnly:
            members = GetMembersChat(group_id)
            if origin_user is None or origin_user['username'] not in str(members):
                answer += f"ERROR! Cannot post in {cookiebot.getChat(group_id)['title']} (because you are not an active member)\n"
                continue
        try:
            num_posts_for_group = 0
            target_chattitle = cookiebot.getChat(group_id)['title']
            for job in jobs:
                if f"--> {target_chattitle}" in job['name']:
                    num_posts_for_group += 1
                if maxPosts is not None and num_posts_for_group > maxPosts:
                    delete_job(job['name'])
                    jobs.remove(job)
                    num_posts_for_group -= 1
            hour = random.randint(0,23)
            minute = random.randint(0,59)
            postmail_message_id = sent_pt if language == 'pt' else sent_en
            create_job(hour, minute, f"{origin_chat['title']} --> {target_chattitle}, at {hour}:{minute}", int(days), int(group_id),
                       int(postmail_chat_id), int(second_chatid), int(postmail_message_id), int(second_messageid), int(origin_userid))
            answer += f"{hour}:{minute} - {target_chattitle}\n"
        except Exception as e:
            print(e)
    try:
        answer += f"OBS: private chats are not listed!"
        Send(cookiebot, mekhyID, answer)
        Send(cookiebot, origin_userid, answer)
        Send(cookiebot, second_chatid, "Post added to the publication queue!", msg_to_reply={'message_id': second_messageid})
    except Exception as e:
        Send(cookiebot, mekhyID, traceback.format_exc())
        Send(cookiebot, second_chatid, "Post added to the publication queue, but I was unable to send you the times.\n<blockquote>Send /start in my DM so I can send you messages.</blockquote>", msg_to_reply={'message_id': second_messageid})

def ScheduleAutopost(cookiebot, msg, chat_id, language, listaadmins_id, isAlternate=0):
    SendChatAction(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id and int(msg['from']['id']) != mekhyID:
        Send(cookiebot, chat_id, "You are not a group admin!", msg_to_reply=msg)
        return
    if 'reply_to_message' not in msg:
        Send(cookiebot, chat_id, "Você precisa responder a uma mensagem com o comando para eu poder repostar ela nesse grupo!", msg_to_reply=msg, language=language)
        return
    if len(msg['text'].split()) > 1:
        if not msg['text'].split()[1].isnumeric():
            Send(cookiebot, chat_id, "Número de dias inválido", msg_to_reply=msg, language=language)
            return
        days = msg['text'].split()[1]
        text = f"Repostagem programada para o grupo por {days} dias!"
    else:
        days = 9999
        text = "Repostagem programada para o grupo! (sem limite de dias)"
    original_msg_id = msg['reply_to_message']['message_id']
    chat = cookiebot.getChat(chat_id)
    hour = random.randint(10,17)
    minute = random.randint(0,59)
    create_job(hour, minute, f"{chat['title']} --> {chat['title']}, at {hour}:{minute} ", int(days), int(chat_id), int(chat_id), int(chat_id), int(original_msg_id), int(original_msg_id), int(msg['from']['id']))
    ReactToMessage(msg, '👍', isAlternate=isAlternate)
    Send(cookiebot, chat_id, text, msg_to_reply=msg, language=language, parse_mode='HTML')

def ClearAutoposts(cookiebot, msg, chat_id, language, listaadmins_id, isAlternate=0):
    SendChatAction(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id:
        Send(cookiebot, chat_id, "You are not a group admin!", msg_to_reply=msg)
        return
    for job in list_jobs():
        if str(job['postmail_chat_id']) == str(chat_id):
            delete_job(job['name'])
    ReactToMessage(msg, '👍', isAlternate=isAlternate)
    Send(cookiebot, chat_id, "Repostagens do grupo canceladas!", msg_to_reply=msg, language=language)

def SchedulerPull(cookiebot, isAlternate=0):
    current_time = datetime.datetime.now()
    current_time = datetime.datetime(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    for job in list_jobs():
        if current_time < datetime.datetime.strptime(job['next_time'], '%Y-%m-%d %H:%M:%S'):
            continue
        if job['days'] <= 1:
            delete_job(job['name'])
        else:
            edit_job_data(job['name'], 'days', job['days'] - 1)
            edit_job_data(job['name'], 'next_time', str(current_time + datetime.timedelta(days=1)))
        try:
            group_id = str(job['target_chat_id'])
            origin_messageid = str(job['postmail_message_id'])
            target_chat = cookiebot.getChat(group_id)
            if 'is_forum' in target_chat and target_chat['is_forum']:
                config = GetConfig(cookiebot, group_id)
                Forward(cookiebot, group_id, postmail_chat_id, origin_messageid, thread_id=int(config[10]), isAlternate=isAlternate)
            else:
                Forward(cookiebot, group_id, postmail_chat_id, origin_messageid, isAlternate=isAlternate)
        except Exception as e:
            Send(cookiebot, mekhyID, traceback.format_exc())
            delete_job(job['name'])

def CheckNotifyPostReply(cookiebot, msg, chat_id, language):
    for job in list_jobs():
        if job['name'].startswith(msg['reply_to_message']['reply_markup']['inline_keyboard'][0][0]['text']):
            second_chatid = str(job['second_chatid'])
            second_messageid = str(job['second_messageid'])
            text = f"@{msg['from']['username']}" if 'username' in msg['from'] else f"{msg['from']['first_name']} {msg['from']['last_name']}"
            text += f" replied:\n'{msg['text']}'\n\nIn chat {msg['chat']['title']}"
            Send(cookiebot, second_chatid, text, msg_to_reply={'message_id': second_messageid}, language=language)
            Send(cookiebot, chat_id, "Resposta enviada ao dono do post!", msg_to_reply=msg, language=language)
            return
