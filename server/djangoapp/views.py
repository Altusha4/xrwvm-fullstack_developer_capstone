import json
from datetime import date
from functools import wraps
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from .models import CarModel
from .restapis import get_request, post_review, analyze_review_sentiments


def guarded(fn):
    @wraps(fn)
    def wrapped(request, *args, **kwargs):
        try:
            return fn(request, *args, **kwargs)
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except requests.RequestException:
            return JsonResponse({'error': 'A backend service is unavailable. Please try again.'}, status=502)
    return wrapped


@ensure_csrf_cookie
def frontend(request, **kwargs):
    return render(request, 'index.html')


@ensure_csrf_cookie
@require_GET
def session_info(request):
    return JsonResponse({'username': request.user.username if request.user.is_authenticated else None})


@require_POST
@guarded
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(request, username=data['userName'], password=data['password'])
    if user is None:
        return JsonResponse({'error': 'Invalid username or password'}, status=401)
    login(request, user)
    return JsonResponse({'userName': user.username, 'status': 'Authenticated'})


@require_POST
def logout_request(request):
    logout(request)
    return JsonResponse({'status': 'Logged out'})


@require_POST
@guarded
def registration(request):
    data = json.loads(request.body)
    username = data['userName'].strip()
    if not username or len(username) > 150:
        raise ValueError('A valid username is required')
    user = User(username=username, first_name=data.get('firstName', ''), last_name=data.get('lastName', ''), email=data.get('email', ''))
    validate_password(data['password'], user)
    user.set_password(data['password'])
    try:
        user.save()
    except IntegrityError:
        return JsonResponse({'error': 'Username already exists'}, status=409)
    login(request, user)
    return JsonResponse({'userName': user.username, 'status': 'Authenticated'}, status=201)


@require_GET
@guarded
def get_dealerships(request, state='All'):
    endpoint = 'fetchDealers' if state == 'All' else 'fetchDealers/' + state
    return JsonResponse({'status': 200, 'dealers': get_request(endpoint)})


@require_GET
@guarded
def get_dealer_details(request, dealer_id):
    dealer = get_request(f'fetchDealer/{dealer_id}')
    return JsonResponse({'status': 200 if dealer else 404, 'dealer': dealer}, status=200 if dealer else 404)


@require_GET
@guarded
def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f'fetchReviews/dealer/{dealer_id}')
    for review in reviews:
        try:
            review['sentiment'] = analyze_review_sentiments(review['review'])
        except requests.RequestException:
            review['sentiment'] = 'unavailable'
    return JsonResponse({'status': 200, 'reviews': reviews})


@require_GET
def get_cars(request):
    cars = [{'id': c.id, 'CarMake': c.car_make.name, 'CarModel': c.name, 'year': c.year} for c in CarModel.objects.select_related('car_make').all()]
    return JsonResponse({'CarModels': cars})


@require_POST
@guarded
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    data = json.loads(request.body)
    data['dealership'] = int(data['dealership'])
    if not str(data['review']).strip() or len(data['review']) > 3000:
        raise ValueError('Review must contain 1 to 3000 characters')
    data['car_year'] = int(data['car_year'])
    if not 2015 <= data['car_year'] <= 2023:
        raise ValueError('Car year must be 2015 to 2023')
    if date.fromisoformat(data['purchase_date']) > date.today():
        raise ValueError('Purchase date cannot be in the future')
    if not get_request(f"fetchDealer/{data['dealership']}"):
        return JsonResponse({'error': 'Dealer not found'}, status=404)
    data['name'] = request.user.get_full_name() or request.user.username
    data['purchase'] = True
    result = post_review(data)
    return JsonResponse({'status': 200, 'review': result}, status=201)
