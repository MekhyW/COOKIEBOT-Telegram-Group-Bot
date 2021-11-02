import ShazamAPI
import ast

file_content_to_recognize = open('file.wav', 'rb').read()

shazam = ShazamAPI.Shazam(file_content_to_recognize)
recognize_generator = shazam.recognizeSong()
response = next(recognize_generator)
if('track' in response[1]):
    print("MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵")