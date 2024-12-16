from universal_funcs import send_message, openai_key
import ShazamAPI
import whisper

stt_model = whisper.load_model("base")

def identify_music(cookiebot, msg, chat_id, content, language):
    shazam = ShazamAPI.Shazam(content)
    recognize_generator = shazam.recognizeSong()
    try:
        response = next(recognize_generator)
    except StopIteration:
        return
    if not 'track' in response[1]:
        return
    title = response[1]['track']['title']
    subtitle = response[1]['track']['subtitle']
    if language in ['pt', 'es']:
        send_message(cookiebot, chat_id,
                     f"MÚSICA: 🎵 <b>{title}</b> - <i>{subtitle}</i> 🎵", msg, language)
    else:
        send_message(cookiebot, chat_id,
                     f"SONG: 🎵 <b>{title}</b> - <i>{subtitle}</i> 🎵", msg, language)

def speech_to_text(content):
    with open('stt.ogg', 'wb') as audio_file:
        audio_file.write(content)
    with open('stt.ogg', 'rb') as audio_file:
        result = stt_model.transcribe(audio_file)
        transcript = result["text"].capitalize()
    return transcript
