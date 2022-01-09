from universal_funcs import *
import threading
publisher_threads, publisher_minimum_msggap = {}, 100

def PublishPublisher(cookiebot, msg_id, chat_id, sender_id):
    if chat_id in publisher_threads and msg_id in publisher_threads[chat_id]:
        publisher_threads[chat_id].remove(msg_id)
    try:
        if chat_id == -1001499400382:
            cookiebot.forwardMessage(chat_id, sender_id, msg_id)
            cookiebot.sendMessage(sender_id, "--Mensagem {} enviada para grupo {}--".format(msg_id, chat_id))
    except Exception as e:
        print(e)

def ReceivePublisher(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Por quantos dias vc gostaria que a sua messagem fosse enviada?\nCertifique-se de que o seu contato está na mensagem!", reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="0 (É URGENTE!)",callback_data='0 PUBLISHER {}'.format(str(msg['message_id'])))], 
                                   [InlineKeyboardButton(text="1 Dia (Mais tarde ou Amanhã)",callback_data='1 PUBLISHER {}'.format(str(msg['message_id'])))],
                                   [InlineKeyboardButton(text="3 Dias",callback_data='3 PUBLISHER {}'.format(str(msg['message_id'])))], 
                                   [InlineKeyboardButton(text="5 Dias",callback_data='5 PUBLISHER {}'.format(str(msg['message_id'])))],
                                   [InlineKeyboardButton(text="Uma Semana",callback_data='7 PUBLISHER {}'.format(str(msg['message_id'])))]
                               ]))

def SpawnThreadsPublisher(chat_id):
    wait_open("Publish_Queue.txt")
    wait_open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt")
    with open("Publish_Queue.txt", 'r') as publish_queue:
        with open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt", 'r') as yesterdaytext:
            messages_yesterday = yesterdaytext.readlines()
            posts_in_queue = publish_queue.readlines()[1:]
            number_posts = math.floor(len(messages_yesterday)/publisher_minimum_msggap) - 1
            if number_posts <= 0 and len(messages_yesterday) > 0:
                number_posts = 1
            for n in range(min(number_posts, len(posts_in_queue))):
                msg_id = int(posts_in_queue[n].split()[0])
                sender_id = int(posts_in_queue[n].split()[1])
                x = datetime.datetime.now()
                y = datetime.datetime.strptime(messages_yesterday[round((n + 1) * (math.floor(len(messages_yesterday)/(number_posts+1))))], "%Y-%m-%d %H:%M:%S.%f\n")
                y = y + datetime.timedelta(days=1)
                delta_t = (y - x).seconds
                publisher_threads[chat_id].append(msg_id)
                threading.Timer(delta_t, PublishPublisher, args=(msg_id, chat_id, sender_id)).start()
                print("Publisher thread on group {} set to {} seconds from now".format(chat_id, delta_t))
        yesterdaytext.close()
    publish_queue.close()

def PublisherController(msg, chat_id, publisher):
    #BEGGINING OF GROUP ACTIVITY GATHERING
    wait_open("GroupActivity/Activity_today_" + str(chat_id) + ".txt")
    wait_open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt")
    open("GroupActivity/Activity_today_" + str(chat_id) + ".txt", 'a').close()
    open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt", 'a').close()
    todaytext = open("GroupActivity/Activity_today_" + str(chat_id) + ".txt", 'r')
    lines = todaytext.readlines()
    todaytext.close()
    if len(lines) > 0 and lines[0].split()[0] != str(datetime.date.today()):
        with open("GroupActivity/Activity_yesterday_" + str(chat_id)+".txt", 'w') as yesterdaytext:
            for line in lines:
                yesterdaytext.write(line)
        yesterdaytext.close()
        todaytext = open("GroupActivity/Activity_today_" + str(chat_id)+".txt", 'w')
        todaytext.close()
    with open("GroupActivity/Activity_today_" + str(chat_id)+".txt", 'a') as todaytext:
        todaytext.write(str(datetime.datetime.now()) + "\n")
    todaytext.close()
    #END OF GROUP ACTIVITY GATHERING
    #BEGINNING OF PUBLISHER SETUP
    wait_open("Publish_Queue.txt")
    publishqueue = open("Publish_Queue.txt", 'r')
    publishqueue_lines = publishqueue.readlines()
    publishqueue.close()
    if publishqueue_lines[0] != str(datetime.date.today())+"\n":
        with open("Publish_Queue.txt", 'w') as publishqueue:
            publishqueue.write(str(datetime.date.today()) + "\n")
            if len(publishqueue_lines) > 1:
                for line in publishqueue_lines[1:]:
                    if len(line.split()) > 2 and int(line.split()[2]) > 1:
                        publishqueue.write(line.split()[0] + " " + line.split()[1] + str(int(line.split()[2]) - 1) + "\n")
        publishqueue.close()
    global publisher_threads
    if chat_id not in publisher_threads:
        publisher_threads[chat_id] = []
    if publisher == True and len(publisher_threads[chat_id]) == 0:
        SpawnThreadsPublisher(chat_id)
    #END OF PUBLISHER SETUP

def PublisherQuery(cookiebot, msg, query_data, mekhyID):
    forwarded = cookiebot.forwardMessage(mekhyID, msg['message']['chat']['id'], query_data.split()[2])
    cookiebot.sendMessage(mekhyID, "Group post - Days: {}".format(query_data.split()[0]), reply_to_message_id=forwarded, reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Aprovar", callback_data='Approve PUBLISH {} {} {}'.format(query_data.split()[2], msg['message']['chat']['id'], query_data.split()[0]).replace("(", '').replace(",", '').replace(")", ''))], [InlineKeyboardButton(text="Recusar", callback_data='Refuse PUBLISH')]]))
    DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
    cookiebot.sendChatAction(msg['message']['chat']['id'], 'typing')
    cookiebot.sendMessage(msg['message']['chat']['id'], "➡️ Sua mensagem foi enviada para aprovação ➡️\n\n--> Isto é feito para evitar conteúdo NSFW em chats SFW e abuso do sistema\n--> Por favor NÃO APAGUE a sua mensagem", reply_to_message_id=query_data.split()[2])

def PublishQuery(cookiebot, msg, query_data, mekhyID):
    if query_data.startswith('Approve'):
        if int(query_data.split()[4]) == 0:
            for grouptxt in os.listdir("Registers"):
                PublishPublisher(int(query_data.split()[2]), int(grouptxt.replace(".txt", '')), int(query_data.split()[3]))
            cookiebot.sendMessage(msg['message']['chat']['id'], "Publicado URGENTE (lembrar de dar forward para o bot irmão)")
        else:
            wait_open("Publish_Queue.txt")
            text = open("Publish_Queue.txt", 'a+', encoding='utf-8')
            text.write(query_data.split()[2] + " " + query_data.split()[3] + " " + query_data.split()[4] + "\n")
            text.close()
            cookiebot.sendMessage(msg['message']['chat']['id'], query_data)
            cookiebot.sendMessage(query_data.split()[3], "✅ Sua mensagem foi Aprovada! ✅\nDeixe ela aqui e pode relaxar, eu vou divulgar por vc :)")
    DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))