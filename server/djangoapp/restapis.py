import os
from urllib.parse import quote
import requests

backend_url = os.environ.get('backend_url', 'http://localhost:3030').rstrip('/')
sentiment_analyzer_url = os.environ.get('sentiment_analyzer_url', 'http://localhost:5050').rstrip('/')


def get_request(endpoint, **kwargs):
    response = requests.get(f'{backend_url}/{endpoint.lstrip("/")}', params=kwargs, timeout=10)
    response.raise_for_status()
    return response.json()


def post_review(data_dict):
    response = requests.post(f'{backend_url}/insert_review', json=data_dict, timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_review_sentiments(text):
    response = requests.get(f'{sentiment_analyzer_url}/analyze/{quote(text, safe="")}', timeout=10)
    response.raise_for_status()
    return response.json()['sentiment']
