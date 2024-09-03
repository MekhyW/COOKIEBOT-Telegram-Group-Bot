import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import math
import re

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

def GenerateWelcomeCard(chat_img, user_img, chat_title, user_firstname, language, size):
    scale = size[0]/chat_img.shape[1]
    rescaled_chat_img = cv2.resize(chat_img, (int(chat_img.shape[1] * scale), int(chat_img.shape[0] * scale)))
    cx, cy, offx, offy = int(rescaled_chat_img.shape[1]/2), int(rescaled_chat_img.shape[0]/2), int(size[1]/2), int(size[0]/2)
    cropped_chat_img = rescaled_chat_img[(cx - offx):(cx + offx), (cy - offy):(cy + offy)]
    blurred_chat_img = cv2.blur(cropped_chat_img, (17, 17))
    circle_center = (cx, int(cy/3))
    circle_radius = int(size[1]*0.28)
    cv2.circle(blurred_chat_img, circle_center, int(circle_radius*1.1), (255, 255, 255), -1)
    # Insert user profile picture
    user_img = cv2.resize(user_img, (circle_radius*2, circle_radius*2))
    for i in range(0, user_img.shape[0]):
        for j in range(0, user_img.shape[1]):
            if math.sqrt((i - circle_radius)**2 + (j - circle_radius)**2) < circle_radius:
                blurred_chat_img[circle_center[1] - circle_radius + i, circle_center[0] - circle_radius + j] = user_img[i, j]
    # Insert text
    cv2.rectangle(blurred_chat_img, (0, int(size[0]*0.36)), (size[1]*10, int(size[0]*0.40)), (0, 0, 0), -1)
    if language == 'pt':
        welcome = 'Bem-vinde ao'
    elif language == 'es':
        welcome = 'Bienvenido a'
    else:
        welcome = 'Welcome to'
    font = ImageFont.truetype('Roadgeek2005Engschrift-lgJw.ttf', 32)
    img_pil = Image.fromarray(blurred_chat_img)
    draw = ImageDraw.Draw(img_pil)    
    chat_title = emoji_pattern.sub(r'', chat_title.strip())
    user_firstname = emoji_pattern.sub(r'', user_firstname.strip())             
    text = f'{welcome} {chat_title}, {user_firstname}!'
    textW, textH = draw.textbbox((0, 0), text, font=font)[2:]
    textX = int(((size[1]*2.2) - textW) / 2)
    textY = int(((size[0]*0.69) + textH) / 2)
    draw.text((textX, textY), text, font = font, fill = (255, 255, 255, 0))
    final_img = np.array(img_pil)
    return final_img

chatpfp = cv2.imread('chatpfp.jpg', cv2.IMREAD_COLOR)
userpfp = cv2.imread('userpfp.jpg', cv2.IMREAD_COLOR)

cv2.imshow('card', GenerateWelcomeCard(chatpfp, userpfp, 'Furmeet Ribeirão Preto 05/02/23', 'Mekhy', 'pt', (1067, 483)))
cv2.waitKey(0)