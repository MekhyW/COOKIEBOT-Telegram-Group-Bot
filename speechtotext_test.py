import os
import subprocess

src_filename = 'file_11.oga'
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', src_filename, "VOICEMESSAGE.wav", '-y'])
import speech_recognition
recognizer = speech_recognition.Recognizer()
AUDIO_FILE = "VOICEMESSAGE.wav"
with speech_recognition.AudioFile(AUDIO_FILE) as source:
    audio = recognizer.record(source)
voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
#print(voicetext_ptbr['transcript'])
#print(voicetext_ptbr['confidence'])
#print(voicetext_enus['transcript'])
#print(voicetext_enus['confidence'])
print(type(voicetext_ptbr['confidence']))
print(voicetext_enus)

