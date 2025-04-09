from universal_funcs import send_message, openai_key, logger
import ShazamAPI
import openai
openai_client = openai.OpenAI(api_key=openai_key)

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
        send_message(cookiebot, chat_id, f"MÚSICA: 🎵 <b> {title} </b> - <i> {subtitle} </i> 🎵", msg)
    else:
        send_message(cookiebot, chat_id, f"SONG: 🎵 <b> {title} </b> - <i> {subtitle} </i> 🎵", msg)
    logger.log_text(f"Music identified: {title} - {subtitle}", severity="INFO")

def speech_to_text(content):
    with open('stt.ogg', 'wb') as audio_file:
        audio_file.write(content)
    with open('stt.ogg', 'rb') as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    transcript = transcript.capitalize()
    logger.log_text(f"Speech to text: {transcript}", severity="INFO")
    return transcript
