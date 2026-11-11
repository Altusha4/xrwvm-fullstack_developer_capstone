import json
from unittest.mock import patch
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import admin
from .models import CarMake, CarModel


class PortalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='Example-test-password-4981')
        self.make = CarMake.objects.create(name='Toyota')
        self.car = CarModel.objects.create(car_make=self.make, name='Camry', type='SEDAN', year=2021)

    def post(self, url, data):
        return self.client.post('/djangoapp/' + url, json.dumps(data), content_type='application/json')

    def test_static_pages(self):
        for path, text in [('/', 'BEST CARS'), ('/about/', 'About Us'), ('/contact/', 'Contact Us')]:
            self.assertContains(self.client.get(path), text)

    def test_registration_login_logout(self):
        result = self.post('register', {'userName': 'new-user', 'password': 'Unique-demo-43984!', 'email': 'demo@example.com'})
        self.assertEqual(result.status_code, 201)
        self.assertEqual(self.client.get('/djangoapp/session').json()['username'], 'new-user')
        self.assertEqual(self.post('logout', {}).status_code, 200)
        self.assertIsNone(self.client.get('/djangoapp/session').json()['username'])
        self.assertEqual(self.post('login', {'userName': 'new-user', 'password': 'Unique-demo-43984!'}).status_code, 200)

    def test_duplicate_and_weak_password(self):
        self.assertEqual(self.post('register', {'userName': 'tester', 'password': 'Another-password-43984!'}).status_code, 409)
        self.assertEqual(self.post('register', {'userName': 'weak', 'password': '123'}).status_code, 400)

    def test_wrong_password(self):
        self.assertEqual(self.post('login', {'userName': 'tester', 'password': 'wrong'}).status_code, 401)

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/djangoapp/login', '{}', content_type='application/json').status_code, 403)
        client.get('/djangoapp/session')
        response = client.post('/djangoapp/login', json.dumps({'userName': 'tester', 'password': 'Example-test-password-4981'}), content_type='application/json', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 200)

    def test_models_admin_and_year_validation(self):
        self.assertTrue(admin.site.is_registered(CarMake))
        self.assertTrue(admin.site.is_registered(CarModel))
        self.car.year = 2010
        with self.assertRaises(ValidationError):
            self.car.full_clean()
        self.assertEqual(self.client.get('/djangoapp/get_cars').json()['CarModels'][0]['CarMake'], 'Toyota')

    @patch('djangoapp.views.get_request')
    def test_dealers_and_state(self, get):
        get.return_value = [{'id': 1, 'state': 'Texas'}]
        self.assertEqual(self.client.get('/djangoapp/get_dealers/Texas').json()['dealers'][0]['id'], 1)
        get.assert_called_with('fetchDealers/Texas')
        self.assertEqual(self.client.get('/djangoapp/dealer/1').status_code, 200)
        get.return_value = []
        self.assertEqual(self.client.get('/djangoapp/dealer/999').status_code, 404)

    @patch('djangoapp.views.get_request', side_effect=requests.Timeout)
    def test_upstream_failure(self, get):
        self.assertEqual(self.client.get('/djangoapp/get_dealers').status_code, 502)

    @patch('djangoapp.views.analyze_review_sentiments')
    @patch('djangoapp.views.get_request')
    def test_review_sentiment(self, get, analyze):
        get.return_value = [{'id': 1, 'review': 'Excellent service'}]
        analyze.return_value = 'positive'
        self.assertEqual(self.client.get('/djangoapp/reviews/dealer/1').json()['reviews'][0]['sentiment'], 'positive')
        analyze.side_effect = requests.Timeout
        self.assertEqual(self.client.get('/djangoapp/reviews/dealer/1').json()['reviews'][0]['sentiment'], 'unavailable')

    @patch('djangoapp.views.post_review')
    @patch('djangoapp.views.get_request')
    def test_add_review_auth_validation_and_identity(self, get, post):
        data = {'dealership': 1, 'review': 'Great dealership', 'car_year': 2021, 'purchase_date': '2026-01-01', 'car_make': 'Toyota', 'car_model': 'Camry', 'name': 'spoofed'}
        self.assertEqual(self.post('add_review', data).status_code, 401)
        self.client.force_login(self.user)
        get.return_value = [{'id': 1}]
        post.return_value = {'id': 123}
        self.assertEqual(self.post('add_review', data).status_code, 201)
        self.assertEqual(post.call_args.args[0]['name'], 'tester')
        data['purchase_date'] = '2999-01-01'
        self.assertEqual(self.post('add_review', data).status_code, 400)

    def test_invalid_json_and_http_method(self):
        self.assertEqual(self.client.get('/djangoapp/login').status_code, 405)
        self.assertEqual(self.client.post('/djangoapp/login', '{', content_type='application/json').status_code, 400)
