# coding=utf8
from universal_funcs import *
from captcha.image import ImageCaptcha
captcha = ImageCaptcha()
import json, requests
import string
Alphabet = {}
Alphabet['Latino'] = string.ascii_letters
Alphabet['Russo'] = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
Alphabet['Arabe'] = 'أبتثجحخدذرزسشصضطظعغفقكلمنهويپچگ'
Alphabet['Hebraico'] = 'אבגדהוזחטיכלמנסעפצקרשת'
Alphabet['Grego'] = 'αβγδεϝζηθικλμνξοπρσςτυφχψωϋϊύώ'
Alphabet['Chines'] = '一丁丂七丄丅丆万丈三上下丌不与丏丐丑丒专且丕世丗丘丙业丛东丝丞丢丠両丢丣两严並丧丨丩个丫丬中丮丯丰丱串丳临丵丶丷丸丹为主丼丽举丿乀乁乂乃乄久乆乇么义乊之乌乍乎乏乐乑乒乓乔乕乖乗乘乙乚乛乜九乞也习乡乢乣乤乥书乧乨乩乪乫乬乭乮乯买乱乲乳乴乵乶乷乸乹乺乻乼乽乾乿亀亁亂亃亄亅了亇予争亊事二亍于亏亐云互亓五井亖亗亘亙亚些亜亝亞亟亠亡亢亣交亥亦产亨亩亪享京亭亮亯亰亱亲亳亴亵亶亷亸亹人亻亼亽亾亿人兀允兂元兄充兆兇先光兊克兌免兎兏児兑兒兓兔兕兖兗兘兙党兛兜兝兞兟兠兡兢兣兤入兦內全兩兪八公六兮兯兰共兲关兴兵其具典兹兺养兼'
Alphabet['Japones'] = 'あいうえおかがきぎくぐけげこごさざしじすずせぜそぞただちぢつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん'
Alphabet['Coreano'] = '가각갂갃간갅갆갇갈갉갊갋갌갍갎갏감갑값갓갔강갖갗갘같갚갛개객갞갟갠갡갢갣갤갥갦갧갨갩갪갫갬갭갮갯갰갱갲갳갴갵갶갷갸갹갺갻갼갽갾갿걀걁걂걃걄걅걆걇걈걉걊걋걌걍걎걏걐걑걒걓걔걕걖걗걘걙걚걛걜걝걞걟걠걡걢걣걤걥걦걧걨걩걪걫걬걭걮걯거걱걲걳건걵걶걷걸걹걺걻걼걽걾걿검겁겂것겄겅겆겇겈겉겊겋게겍겎겏겐겑겒겓겔겕겖겗겘겙겚겛겜겝겞겟겠겡겢'
Alphabet['Tailandes'] = 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุู฿เแแดโตใึไๆ่้๊๋์ํ๎๏๐๑๒๓๔๕๖๗๘๙๚๛'
Alphabet['Vietnamita'] = 'ẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
Alphabet['Etiope'] = 'አኡኢኣኤእኦኧከኩኪካኬክኮኯኰኲኳኴኵኸኹኺኻኼኽኾ኿ዀ዁ዂዃዄዅ዆዇ወዉዊዋዌውዎዏዐዑዒዓዔዕዖ዗ዘዙዚዛዜዝዞዟዠዡዢዣዤዥዦዧየዩዪያዬይዮዯደዱዲዳዴድዶዷዸዹዺዻዼዽዾዿጀጁጂጃጄጅጆጇገጉጊጋጌግጎጏጐ጑ጒጓጔጕ጖጗ጘጙጚጛጜጝጞጟጠጡጢጣጤጥጦጧጨጩጪጫጬጭጮጯጰጱጲጳጴጵጶጷጸጹጺጻጼጽጾጿፀፁፂፃፄፅፆ'
Alphabet['Hindi'] = 'अआइईउऊऋऌऍऎएऐऑऒओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहळऴऱरलकतदनपपरल'
Alphabet['Georgiano'] = 'აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰჱჲჳჴჵჶჷჸჹჺ჻ჼჽჾჿᄀᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑᄒᄓᄔᄕᄖᄗᄘᄙᄚᄛᄜᄝᄞᄟᄠᄡᄢᄣᄤᄥᄦᄧᄨᄩᄪᄫᄬᄭᄮᄯᄰᄱᄲᄳᄴᄵᄶᄷᄸᄹᄺᄻᄼᄽᄾᄿᅀᅁᅂᅃᅄᅅᅆᅇᅈᅉᅊᅋᅌᅍᅎᅏᅐᅑᅒᅓᅔᅕᅖᅗᅘᅙᅚᅛᅜᅝᅞᅟᅠᅡᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵᅶᅷ'
Alphabet['Armenio'] = 'ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖՙ՚՛՜՝՞՟աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆև'
Alphabet['Bengali'] = 'অআইঈউঊঋঌএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহরলকতদনপপরল'
Alphabet['Urdu'] = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهہیےۓ۔ەۖۗۘۙۚۛۜ۝۞ۣ۟۠ۡۢۤۥۦۧۨ۩۪ۭ۫۬ۮۯ۰۱۲۳۴۵۶۷۸۹ۺۻۼ۽۾ۿ'
Alphabet['Lao'] = 'ກຂຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫອຮຯະາຳິີຶືຸູົຼຽເແໂໃໄໆ່້໊໋໐໑໒໓໔໕໖໗໘໙ໜໝໞໟກຂຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫອຮຯະາຳິີຶືຸູົຼຽເແໂໃໄໆ໐໑໒໓໔໕໖໗໘'
Alphabet['Cambojano'] = 'កខគឃងចឆជឈញដឋឌឍណតថទធនបផពភមយរលវឝឞសហឡអឣឤឥឦឧឨឩឪឫឬឭឮឯឰឱឲឳ឴឵ាិីឹឺុូួើឿៀេែៃោៅំះៈ៉៊់៌៍៎៏័៑្៓។៕៖ៗ៘៙៚៛ៜ៝០១២៣៤៥៦៧៨៩៰៱៲៳៴៵៶៷៸៹᠀᠁᠂᠃᠄᠅᠆᠇᠈᠉᠊᠋᠌᠍᠎᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙᠚᠛᠜᠝᠞ᠠᠡᠢᠣᠤᠥ'
Alphabet['Birmanes'] = 'ကခဂဃငစဆဇဈဉညဋဌဍဎဏတထဒဓနပဖဗဘမယရလဝသဟဠအဢဣဤဥဦဧဨဩဪါာိီုူေဲဳဴဵံ့း္်ျြွှဿ၀၁၂၃၄၅၆၇၈၉၊။၌၍၎၏ၐၑၒၓၔၕၖၗၘၙၚၛၜၝၞၟၠၡၢၣၤၥၦၧၨၩၪၫၬၭၮၯၰၱၲၳၴၵၶၷၸၹၺၻၼၽၾၿႀႁႂႃႄႅႆႇႈႉႊႋႌႍႎႏ႐႑႒႓႔႕႖႗႘႙ႚႛႜႝ႞႟ႠႡႢႣႤႥႦ'


def Bemvindo(cookiebot, msg, chat_id, limbotimespan, language):
    cookiebot.sendChatAction(chat_id, 'typing')
    if limbotimespan > 0:
        try:
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': True, 'can_send_other_messages': True, 'can_add_web_page_previews': True})
            cookiebot.restrictChatMember(chat_id, msg['from']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False}, until_date=int(time.time() + limbotimespan))
            Send(cookiebot, chat_id, "ATENÇÃO! Você está limitado por {} minutos. Por favor se apresente e se enturme na conversa com os demais membros.\nUse o /regras para ver as regras do grupo".format(str(round(limbotimespan/60))), language=language)
        except Exception as e:
            print(e)
    if os.path.exists("Welcome/Welcome_" + str(chat_id)+".txt"):
        wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
        with open("Welcome/Welcome_" + str(chat_id)+".txt", encoding='utf-8') as file:
            welcome = file.read()
            cookiebot.sendMessage(chat_id, welcome)
            file.close()
    else:
        try:
            Send(cookiebot, chat_id, "Olá! As boas-vindas ao grupo {}!".format(msg['chat']['title']), language=language)
        except:
            Send(cookiebot, chat_id, "Olá! As boas-vindas ao grupo!", language=language)

def CheckHumanFactor(cookiebot, msg, chat_id, language):
    if 'username' not in msg['new_chat_participant']:
        userphotos = cookiebot.getUserProfilePhotos(msg['new_chat_participant']['id'])
        if userphotos['total_count'] < 2:
            cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
            Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser um usuário-robô", language=language)
            return True
    return False

def CheckCharacters(cookiebot, msg, chat_id, language):
    name = msg['new_chat_participant']['first_name']
    if 'last_name' in msg['new_chat_participant']:
        name += msg['new_chat_participant']['last_name']
    score = 0
    for caractere in name:
        if caractere in Alphabet['Latino'] or caractere in Alphabet['Japones'] or caractere in Alphabet['Grego'] or caractere in Alphabet['Hebraico'] or caractere in Alphabet['Vietnamita']:
            score += 1
        else:
            for label in Alphabet:
                if caractere in Alphabet[label]:
                    detected_region = label
                    score -= 1
                    break
    if score < 0:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser ser um usuário-robô ({})".format(detected_region), language=language)
        return True
    return False

def CheckCAS(cookiebot, msg, chat_id, language):
    r = requests.get("https://api.cas.chat/check?user_id={}".format(msg['new_chat_participant']['id']), timeout=10)
    in_banlist = json.loads(r.text)['ok']
    if in_banlist == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser flagrado pelo sistema anti-ban CAS https://cas.chat/", language=language)
        return True
    return False


def CheckRaider(cookiebot, msg, chat_id, language):
    r = requests.post('https://burrbot.xyz/noraid.php', data={'id': '{}'.format(msg['new_chat_participant']['id'])}, timeout=10)
    is_raider = json.loads(r.text)['raider']
    if is_raider == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        Send(cookiebot, chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.", language=language)
        return True
    return False

def Captcha(cookiebot, msg, chat_id, captchatimespan, language):
    try:
        cookiebot.restrictChatMember(chat_id, msg['new_chat_participant']['id'], permissions={'can_send_messages': True, 'can_send_media_messages': False, 'can_send_other_messages': False, 'can_add_web_page_previews': False})
    except Exception as e:
        print(e)
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    photo = open('CAPTCHA.png', 'rb')
    if language == "pt":
        caption = "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60)))
    elif language == "es":
        caption = "Ingresa el código de arriba para demostrar que no eres un robot\nTienes {} minutos, si no lo resuelves en ese tiempo te eliminaré del chat\n(NOTA: Si no aparecen 4 dígitos, abrir la imagen completa)".format(str(round(captchatimespan/60)))
    else:
        caption = "Type the code above to prove you're not a robot\nYou have {} minutes, if you don't solve it in that time I'll remove you from the chat\n(NOTE: If 4 digits don't appear, open the full photo)".format(str(round(captchatimespan/60)))
    captchaspawnID = cookiebot.sendPhoto(chat_id, photo, caption=caption, reply_to_message_id=msg['message_id'], reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ADMINS: Approve",callback_data='CAPTCHA')]]))['message_id']
    photo.close()
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + " " + password + " " + str(captchaspawnID) + "\n")
    text.close()

def CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            #CHATID userID 2021-05-13 11:45:29.027116 password captcha_id
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            captchasettime = (hour*3600) + (minute*60) + (second)
            chat = int(line.split()[0])
            user = int(line.split()[1])
            if chat == chat_id and captchasettime+captchatimespan <= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                cookiebot.kickChatMember(chat, user)
                Send(cookiebot, chat, "Bani o usuário com id {} por não solucionar o captcha a tempo.\nSe isso foi um erro, peça para um staff adicioná-lo de volta".format(user), language=language)
                DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
            elif chat == chat_id and user == msg['from']['id']:
                text.write(line)
                DeleteMessage(cookiebot, telepot.message_identifier(msg))
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(cookiebot, msg, chat_id, button, limbotimespan=0, language='pt'):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            if str(chat_id) == line.split()[0] and button == True:
                cookiebot.sendChatAction(chat_id, 'typing')
                DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
                Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
            elif str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    DeleteMessage(cookiebot, (line.split()[0], line.split()[5]))
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    Bemvindo(cookiebot, msg, chat_id, limbotimespan, language)
                else:
                    DeleteMessage(cookiebot, telepot.message_identifier(msg))
                    Send(cookiebot, chat_id, "Senha incorreta, por favor tente novamente.", language=language)
                    text.write(line)
            else:
                text.write(line)
    text.close()

def left_chat_member(msg, chat_id):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()