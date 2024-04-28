from universal_funcs import *
from Configurations import *
from UserRegisters import *
from google.cloud import scheduler_v1
from google.cloud import pubsub_v1
from price_parser import Price
client = scheduler_v1.CloudSchedulerClient.from_service_account_json("cookiebot_pubsub.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json("cookiebot_pubsub.json")
project_id = "cookiebot-309512"
project_path = f"projects/{project_id}"
parent = f"{project_path}/locations/southamerica-east1"
topic_name = 'projects/cookiebot-309512/topics/cookiebot-publisher-topic'
subscription_path = None
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
    caption_entities = []
    if 'caption_entities' in msg:
        for entity in msg['caption_entities']:
            caption_entities.append(entity)
    cache_posts[str(msg['forward_from_message_id'])] = {media_type: media_id, 'caption': msg['caption'], 'caption_entities': caption_entities}

def AskApproval(cookiebot, query_data, from_id, isBombot=False):
    origin_chatid = query_data.split()[1]
    second_chatid = query_data.split()[2]
    origin_messageid = query_data.split()[3]
    second_messageid = query_data.split()[4]
    origin_userid = from_id
    Forward(cookiebot, approval_chat_id, second_chatid, second_messageid, isBombot=isBombot)
    Send(cookiebot, approval_chat_id, 'Approve post?', 
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️ 7 days",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 7 {second_messageid}')],
            [InlineKeyboardButton(text="✔️ 3 days",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 3 {second_messageid}')],
            [InlineKeyboardButton(text="✔️ 1 day",callback_data=f'ApprovePub {origin_chatid} {second_chatid} {origin_messageid} {origin_userid} 1 {second_messageid}')],
            [InlineKeyboardButton(text="❌",callback_data=f'DenyPub {origin_messageid}')]
        ]
    ))

def create_job(job_name, job_description, job_data, job_schedule):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'description': job_description,
        'pubsub_target': {
            'topic_name': topic_name,
            'data': bytes(job_data,'utf-8'),
        },
        'schedule': job_schedule,
    }
    response = client.create_job(parent=parent, job=job)
    print(f'Created job: {response.name}')
    return response

def list_jobs():
    response = client.list_jobs(parent=parent)
    jobs = []
    for job in response:
        jobs.append(job)
    return jobs

def delete_job(job_name):
    try:
        response = client.delete_job(name=client.job_path(project_id, 'southamerica-east1', job_name))
    except:
        response = client.delete_job(name=job_name)
    print(f'Deleted job: {response}')
    return response

def edit_job_data(job_name, job_data):
    job = {
        'name': client.job_path(project_id, 'southamerica-east1', job_name),
        'pubsub_target': {
            'topic_name': topic_name,
            'data': bytes(job_data,'utf-8'),
        },
    }
    response = client.update_job(job=job, update_mask={'paths': ['pubsub_target']})
    print(f'Updated job: {response.name}')
    return response

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
    caption_pt = ConvertPricesinText(caption_pt, 'BRL')
    caption_en = ConvertPricesinText(caption_en, 'USD')
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
    origin_chatid = query_data.split()[1]
    second_chatid = query_data.split()[2]
    origin_messageid = query_data.split()[3]
    origin_userid = query_data.split()[4]
    days = query_data.split()[5]
    second_messageid = query_data.split()[6]
    origin_chat = cookiebot.getChat(origin_chatid)
    try:
        origin_user = cookiebot.getChatMember(origin_chatid, origin_userid)['user']
    except:
        origin_user = None
    sent_pt, sent_en = PreparePost(cookiebot, origin_messageid, origin_chat, origin_user)
    jobs = list_jobs()
    for job in jobs:
        if job.name.startswith(f"{parent}/jobs/{origin_chatid}"):
            delete_job(job.name)
            jobs.remove(job)
    answer = f"Post set for the following times ({days} days):\n"
    answer += "NOW - Cookiebot Mural 📬\n"
    for group in GetRequestBackend('registers'):
        group_id = group['id']
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = GetConfig(cookiebot, group_id)
        if publisherMembersOnly:
            members = GetMembersChat(group_id)
            if origin_user is None or origin_user['username'] not in str(members):
                answer += f"ERROR! Cannot post in {cookiebot.getChat(group_id)['title']} (because you are not an active member)\n"
                continue
        if publisherpost:
            try:
                num_posts_for_group = 0
                target_chattitle = cookiebot.getChat(group_id)['title']
                oldest_job = None
                oldest_job_time = None
                for job in jobs:
                    if f"--> {target_chattitle}" in job.description:
                        num_posts_for_group += 1
                        if oldest_job_time is None or job.schedule_time < oldest_job_time:
                            oldest_job = job
                            oldest_job_time = job.schedule_time
                    if maxPosts is not None and num_posts_for_group > maxPosts:
                        delete_job(job.name)
                        num_posts_for_group -= 1
                hour = random.randint(0,23)
                minute = random.randint(0,59)
                sent = sent_pt if language == 'pt' else sent_en
                create_job(origin_chatid+group_id, 
                f"{origin_chat['title']} --> {target_chattitle}, at {hour}:{minute} ", 
                f"{days} {postmail_chat_id} {group_id} {sent} {origin_chatid}",
                f"{minute} {hour} * * *")
                answer += f"{hour}:{minute} - {target_chattitle}\n"
            except Exception as e:
                print(e)
                if 'RESOURCE_EXHAUSTED' in str(e) and oldest_job is not None:
                    delete_job(oldest_job.name)
                    create_job(origin_chatid+group_id, 
                    f"{origin_chat['title']} --> {target_chattitle}, at {hour}:{minute} ", 
                    f"{days} {postmail_chat_id} {group_id} {sent} {origin_chatid} {second_chatid} {second_messageid}",
                    f"{minute} {hour} * * *")
                    answer += f"{hour}:{minute} - {target_chattitle}\n"
    try:
        answer += f"OBS: private chats are not listed!"
        Send(cookiebot, mekhyID, answer)
        Send(cookiebot, origin_userid, answer)
        Send(cookiebot, second_chatid, "Post added to the publication queue\!", msg_to_reply={'message_id': second_messageid})
    except Exception as e:
        Send(cookiebot, mekhyID, traceback.format_exc())
        Send(cookiebot, second_chatid, "Post added to the publication queue, but I was unable to send you the times.\n>Send /start in my DM so I can send you messages\.", msg_to_reply={'message_id': second_messageid})

def ScheduleAutopost(cookiebot, msg, chat_id, language, listaadmins_id, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id:
        Send(cookiebot, chat_id, "You are not a group admin\!", msg_to_reply=msg)
        return
    if 'reply_to_message' not in msg:
        Send(cookiebot, chat_id, "Você precisa responder a uma mensagem com o comando para eu poder repostar ela nesse grupo\!", msg_to_reply=msg, language=language)
        return
    if len(msg['text'].split()) < 2 or not msg['text'].split()[1].isnumeric():
        Send(cookiebot, chat_id, "Você precisa especificar o número de dias para o autopost repostar nesse grupo\!\n>Exemplo\: /repostar 10", msg_to_reply=msg, language=language)
        return
    original_msg_id = msg['reply_to_message']['message_id']
    chat = cookiebot.getChat(chat_id)
    days = msg['text'].split()[1]
    hour = random.randint(10,17)
    minute = random.randint(0,59)
    create_job(str(chat_id)+str(chat_id), 
                f"{chat['title']} --> {chat['title']}, at {hour}:{minute} ", 
                f"{days} {chat_id} {chat_id} {original_msg_id} {chat_id} 0 0",
                f"{minute} {hour} * * *")
    ReactToMessage(msg, '👍', isBombot=isBombot)
    Send(cookiebot, chat_id, f"Repostagem programada para o grupo por *{days} dias\!*", msg_to_reply=msg, language=language)

def ClearAutoposts(cookiebot, msg, chat_id, language, listaadmins_id, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'typing')
    if str(msg['from']['id']) not in listaadmins_id:
        Send(cookiebot, chat_id, "You are not a group admin\!", msg_to_reply=msg)
        return
    jobs = list_jobs()
    for job in jobs:
        if job.name.startswith(f"{parent}/jobs/{chat_id}"):
            delete_job(job.name)
    ReactToMessage(msg, '👍', isBombot=isBombot)
    Send(cookiebot, chat_id, "Repostagens do grupo canceladas\!", msg_to_reply=msg, language=language)

def SchedulerPull(cookiebot, isBombot=False):
    response = subscriber.pull(subscription=subscription_path, max_messages=100, return_immediately=True)
    received_messages = response.received_messages
    for message in received_messages:
        subscriber.acknowledge(subscription=subscription_path, ack_ids=[message.ack_id])
        print(message.message.data)
        data = message.message.data.decode('utf-8')
        remaining_times = int(data.split()[0]) - 1
        postmail_chat_id = data.split()[1]
        group_id = data.split()[2]
        origin_messageid = data.split()[3]
        origin_chatid = data.split()[4]
        if remaining_times <= 0:
            delete_job(origin_chatid+group_id)
        else:
            edit_job_data(origin_chatid+group_id, f"{remaining_times} {postmail_chat_id} {group_id} {origin_messageid} {origin_chatid}")
        try:
            target_chat = cookiebot.getChat(group_id)
            if 'is_forum' in target_chat and target_chat['is_forum']:
                config = GetConfig(cookiebot, group_id)
                Forward(cookiebot, group_id, postmail_chat_id, origin_messageid, thread_id=int(config[10]), isBombot=isBombot)
            else:
                Forward(cookiebot, group_id, postmail_chat_id, origin_messageid, isBombot=isBombot)
        except TelegramError as e:
            Send(cookiebot, mekhyID, traceback.format_exc())
            delete_job(origin_chatid+group_id)
    return received_messages

def CheckNotifyPostReply(cookiebot, msg, chat_id, language):
    jobs = list_jobs()
    for job in jobs:
        if job.description.startswith(f"{parent}/jobs/{msg['reply_to_message']['inline_keyboard'][0]['text']} --> {msg['chat']['title']}"):
            job_data = job.pubsub_target.data.decode('utf-8')
            if(len(job_data.split()) < 7):
                return
            second_chatid = job_data.split()[5]
            second_messageid = job_data.split()[6]
            text = f"@{msg['from']['username']}" if 'username' in msg['from'] else f"{msg['from']['first_name']} {msg['from']['last_name']}"
            text += f" replied:\n'{msg['reply_to_message']['text']}'\n\nIn chat {msg['chat']['title']}"
            Send(cookiebot, second_chatid, text, msg_to_reply={'message_id': second_messageid}, language=language)
            return

def startPublisher(isBombot):
    global subscription_path
    if isBombot:
        subscription_path = subscriber.subscription_path(project_id, "bombot-subscription")
    else:
        subscription_path = subscriber.subscription_path(project_id, "cookiebot-subscription")