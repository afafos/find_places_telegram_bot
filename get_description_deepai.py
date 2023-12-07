import requests
from api import *


def get_brief_description(name, location_query):
    payload = {
        'text': 'Describe briefly using no more than 400 characters {} located in {}'.format(name, location_query)
    }

    headers = {
        'api-key': deepai_api
    }

    response = requests.post("https://api.deepai.org/api/text-generator", data=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        brief_description = result.get('output', 'No brief description available')
        return brief_description
    else:
        return 'Failed to get brief description'
