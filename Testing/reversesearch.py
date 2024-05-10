from saucenao_api import SauceNao, VideoSauce, BookSauce, errors
import json
key = json.loads(open('Bot/cookiebot_basecredentials.json', 'r').read())['saucenao_key']
sauce = SauceNao(key)

def main(url):
    try:
        results = sauce.from_url(url)
    except errors.ShortLimitReachedError:
        print('30s interval limit reached')
        return
    except errors.LongLimitReachedError:
        print('Daily limit reached')
        return
    if results:
        print(f'{len(results)} results')
        for result in results:
            print(result.similarity, result.title, result.urls, result.author)
    print(f'Remaining searches: {results.short_remaining} (30s interval) and {results.long_remaining} (daily limit)')

if __name__ == '__main__':
    main('https://www.duelshop.com.br/1211-large_default/odd-eyes-pendulum-dragon-sdmp-en009-common.jpg')