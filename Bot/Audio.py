from universal_funcs import *
import subprocess
import speech_recognition, ShazamAPI
recognizer = speech_recognition.Recognizer()

def Identify_music(cookiebot, msg, chat_id, AUDIO_FILE):
    shazam = ShazamAPI.Shazam(open(AUDIO_FILE, 'rb').read())
    recognize_generator = shazam.recognizeSong()
    response = next(recognize_generator)
    if('track' in response[1]):
        cookiebot.sendMessage(chat_id, "MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵", reply_to_message_id=msg['message_id'])

def Speech_to_text(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
    open('VOICEMESSAGE.oga', 'wb').write(r.content)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
    AUDIO_FILE = "VOICEMESSAGE.wav"
    try:
        with speech_recognition.AudioFile(AUDIO_FILE) as source:
            audio = recognizer.record(source)
        voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
        #voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
        Text = voicetext_ptbr['transcript'].capitalize()
        cookiebot.sendMessage(chat_id, "Texto: \n"+'"'+Text+'"', reply_to_message_id=msg['message_id'])
    except Exception as e:
        print(e)
    Identify_music(msg, chat_id, AUDIO_FILE)