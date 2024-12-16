import whisper

model = whisper.load_model("base")

def speech_to_text(filename):
    with open(filename, 'rb') as audio_file:
        result = model.transcribe(audio_file)
        transcript = result["text"]
    transcript = transcript.capitalize()
    return transcript

print(speech_to_text('audio_2024-07-16_20-59-44.ogg'))
