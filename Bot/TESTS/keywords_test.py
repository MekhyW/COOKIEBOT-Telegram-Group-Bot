import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
IBMWATSONTOKEN = ''
service = NaturalLanguageUnderstandingV1(version='2018-03-16', authenticator=IAMAuthenticator(IBMWATSONTOKEN))
service.set_service_url('https://gateway.watsonplatform.net/natural-language-understanding/api')

response = service.analyze(
    text='Não tenho fursuit, ainda posso participar da BFF?',
    features=Features(entities=EntitiesOptions(),
                      keywords=KeywordsOptions())).get_result()

keywords = json.loads(json.dumps(response, indent=2))['keywords']
keyword_texts = []
for keyword in keywords:
    keyword_texts.append(keyword['text'])
print(keywords)
print(keyword_texts)
