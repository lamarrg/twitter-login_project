from flask import Flask, render_template, session, redirect, request, url_for, g
from twitter_utils import get_request_token, get_oauth_verifier_url, get_access_token
from user import User
from database import Database
import json
import requests

app = Flask(__name__)
app.secret_key = '1234'  #required so cookie can be encrypted

Database.initialise(host='localhost', database='learning', user='postgres', password='$erenity9')

@app.before_request
def load_user():
    if 'screen_name' in session:
        g.user = User.load_from_db_by_screen_name(session['screen_name'])

@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/login/twitter')
def twitter_login():
    if 'screen_name' in session:
        return redirect(url_for('profile'))

    request_token = get_request_token()
    session['request_token'] = request_token

    return redirect(get_oauth_verifier_url(request_token))
    # redirecting to twitter so they can confirm auth

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/auth/twitter') # http://127.0.0.1:4995/auth/twitter?oauth_verifer=123456
def twitter_auth():
    oauth_verifier = request.args.get('oauth_verifier')
    access_token = get_access_token(session['request_token'], oauth_verifier)
    user = User.load_from_db_by_screen_name(access_token['screen_name'])
    if not user:
        user = User(access_token['screen_name'], access_token['oauth_token'], access_token['oauth_token_secret'], None)
        user.save_to_db()

    session['screen_name'] = user.screen_name

    return redirect(url_for('profile'))  # This is the function, not the page name

@app.route('/profile')
def profile():
    return render_template('profile.html', user=g.user)


@app.route('/search')
def search():
    query = request.args.get('q')  # I think the 'q' comes from line 27 of login.py
    tweets = g.user.twitter_request('https://api.twitter.com/1.1/search/tweets.json?q={}'.format(query)) #computers filter:media'

    tweet_texts = [{'tweet': tweet['text'], 'label': 'neutral'} for tweet in tweets['statuses']]

    for tweet in tweet_texts:
        r = requests.post('http://text-processing.com/api/sentiment/', data={'text': tweet['tweet'] })
        json_response = r.json()
        label = json_response['label']
        tweet['label'] = label

    print(tweet_texts)


    return render_template('search.html', content=tweet_texts)



app.run(port=4995, debug=True)