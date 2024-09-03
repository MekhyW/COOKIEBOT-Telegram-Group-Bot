import openai
import json
openai_client = openai.OpenAI(api_key='')

def speech_to_text(filename):
    with open(filename, 'rb') as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
    transcript = transcript.capitalize()
    return transcript

print(speech_to_text('audio_2024-07-16_20-59-44.ogg'))