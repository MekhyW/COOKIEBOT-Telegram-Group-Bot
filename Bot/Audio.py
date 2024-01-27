from universal_funcs import *
import ShazamAPI
import openai

def Identify_music(cookiebot, msg, chat_id, content, language):
    shazam = ShazamAPI.Shazam(content)
    recognize_generator = shazam.recognizeSong()
    try:
        response = next(recognize_generator)
    except StopIteration:
        return
    if('track' in response[1]):
        title = response[1]['track']['title']
        subtitle = response[1]['track']['subtitle']
        if language in ['pt', 'es']:
            Send(cookiebot, chat_id, f"MÚSICA: 🎵 {title} - {subtitle} 🎵", msg, language)
        else:
            Send(cookiebot, chat_id, f"SONG: 🎵 {title} - {subtitle} 🎵", msg, language)

def Speech_to_text(content):
    with open('stt.mp3', 'wb') as audio_file:
        audio_file.write(content)
        transcript = openai.Audio.transcribe("whisper-1", audio_file)['text']
    transcript = openai.Audio.transcribe("whisper-1", content)['text']
    transcript = transcript.capitalize()
    return transcript