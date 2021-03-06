from user import User
from database import Database
from twitter_utils import get_request_token, get_oauth_verifier, get_access_token
import hidden_constants

# Database.initialise(user="postgres", password="$erenity9", host="localhost", database="learning")

# Database.initialise(host=hidden_constants.hidden_host, database=hidden_constants.hidden_database, user=hidden_constants.hidden_user, password=hidden_constants.hidden_password)

user_email = input("Enter your email address: ")

user = User.load_from_db_by_email(user_email)

if not user:
    request_token = get_request_token()

    oauth_verifier = get_oauth_verifier(request_token)

    access_token = get_access_token(request_token, oauth_verifier)

    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")

    user = User(user_email, first_name, last_name, access_token['oauth_token'], access_token['oauth_token_secret'], None)
    user.save_to_db()



tweets = user.twitter_request('https://api.twitter.com/1.1/search/tweets.json?q=computers filter:media')

# for tweet in tweets['statuses']:
#     print(tweet["text"])