import requests
import re

URL_REGEX = r'\b((?:https?|ftp|file):\/\/[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]{1,2048})'
TRACKER_REGEX = r'si=[^&]{0,100}&?|igsh=[^&]{0,100}&?'
TWITTER_REGEX = r'(?:twitter|x)\.com/[a-zA-Z0-9_]{1,15}/status/[0-9]{1,20}'
TIKTOK_REGEX = r'tiktok\.com/@[a-zA-Z0-9_.]{1,24}/video/[0-9]{1,20}'
INSTAGRAM_REGEX = r'instagram\.com/(reel|p)/[a-zA-Z0-9_-]{1,11}'
BSKY_REGEX = r'bsky\.app/profile/[a-zA-Z0-9.-]{1,253}'

def fix_embed_if_social_link(message: str) -> str | bool:
    message = message.strip()
    try:
        if requests.get(message, timeout=2).status_code != 200:
            return False
    except:
        return False
    transformations = [
        (TWITTER_REGEX, "https://fixupx.com/{}", r'[^/]+/status/[0-9]+'),
        (TIKTOK_REGEX, "https://d.tnktok.com/{}", r'@[^/]+/video/[0-9]+'),
        (INSTAGRAM_REGEX, "https://ddinstagram.com/{}", r'(reel|p)/([^?/]+)'),
        (BSKY_REGEX, "https://fxbsky.app/profile/{}", r'\.app/profile/(.+)')
    ]
    if re.search(TIKTOK_REGEX, message) and re.search(r'vm\.tiktok\.com/.+|tiktok\.com/t/.+', message):
        try:
            message = requests.get(message, timeout=1).url
        except:
            return False
    for main_pattern, template, extract_pattern in transformations:
        if re.search(main_pattern, message):
            if match := re.search(extract_pattern, message):
                if 'ddinstagram.com' in template:
                    path = match.group(1) + '/' + match.group(2)
                    query = message[message.find('?'):] if '?' in message else ''
                    return template.format(path) + query
                return template.format(match.group(1) if '(' in extract_pattern else match.group())
            return False
    if re.search(TRACKER_REGEX, message):
        clean = re.sub(TRACKER_REGEX, "", message)
        return re.sub(r'\?$', '', clean) if clean != message else False
    return False

if __name__ == "__main__":
    text = input("Enter the message: ")
    print(fix_embed_if_social_link(text))
