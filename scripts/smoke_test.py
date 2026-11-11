"""End-to-end checks for a disposable local deployment; creates a demo user/review."""
import secrets
import sys
from datetime import date
import requests

base = sys.argv[1].rstrip('/')
assert base.startswith(('http://localhost:', 'http://127.0.0.1:')), 'Local demo deployments only'
s = requests.Session()
for page in ['/', '/about/', '/contact/', '/dealers', '/login', '/register']:
    response = s.get(base + page, timeout=15)
    assert response.status_code == 200, (page, response.status_code)

def get(path):
    response = s.get(base + '/djangoapp/' + path, timeout=20)
    response.raise_for_status()
    return response.json()

def post(path, data, expected=200):
    response = s.post(base + '/djangoapp/' + path, json=data, headers={'X-CSRFToken': s.cookies.get('csrftoken', '')}, timeout=20)
    assert response.status_code == expected, (path, response.status_code, response.text[:200])
    return response.json()

get('session')
user = 'smoke-' + secrets.token_hex(5)
password = secrets.token_urlsafe(24)
post('register', {'userName': user, 'password': password, 'firstName': 'Demo', 'lastName': 'Tester'}, 201)
assert get('session')['username'] == user
assert len(get('get_dealers')['dealers']) == 50
assert all(d['state'] == 'Texas' for d in get('get_dealers/Texas')['dealers'])
assert get('dealer/1')['dealer'][0]['id'] == 1
assert len(get('get_cars')['CarModels']) == 3
text = 'Excellent service, friendly staff and a great car! ' + user
post('add_review', {'dealership': 1, 'review': text, 'car_make': 'Toyota', 'car_model': 'Camry', 'car_year': 2021, 'purchase_date': str(date.today())}, 201)
review = next(r for r in get('reviews/dealer/1')['reviews'] if r['review'] == text)
assert review['sentiment'] == 'positive', review['sentiment']
assert review['name'] == 'Demo Tester'
post('logout', {})
assert get('session')['username'] is None
post('add_review', {}, 401)
post('login', {'userName': user, 'password': password})
assert get('session')['username'] == user
print('PASS:', base, 'static pages, auth, CSRF, dealer filters, car models, persistent review and sentiment')
