import os
import nltk
from flask import Flask, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.data.path.insert(0, os.path.dirname(__file__))
app = Flask(__name__)
sia = SentimentIntensityAnalyzer()


@app.get('/')
def home():
    return jsonify(service='Sentiment Analyzer')


@app.get('/analyze/<path:input_txt>')
def analyze_sentiment(input_txt):
    score = sia.polarity_scores(input_txt)['compound']
    return jsonify(sentiment='positive' if score >= 0.05 else 'negative' if score <= -0.05 else 'neutral')
