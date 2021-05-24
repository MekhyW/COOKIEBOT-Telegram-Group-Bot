import random
from captcha.image import ImageCaptcha
Captcha = ImageCaptcha()

caracters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
Captcha.write(password, 'CAPTCHA.png')