import requests
import base64
import urllib.parse
import json
import datetime
import time

from ohmysportsfeedspy import MySportsFeeds
from flask import redirect, render_template, request, session
from functools import wraps

msf = MySportsFeeds(version="1.2")
msf.authenticate("3656e957-66e5-4a31-8031-617932", "sportsfan1993")

weekly_games = {}
weeks = []


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        response = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/quote")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def full_game_schedule():
    #funtion to pull full game schedule from mysportsfeed (all weeks)
    season = msf.msf_get_data(league='nfl',season='current',feed='full_game_schedule', format='json')
    season = season['fullgameschedule']
    season = season['gameentry']
    return season

def week_finder(games):
    print(games)
    #function to return the week we are in, based on the dates of the games from the full schedule
    for game in range(0, len(games)-1):
        #saving breaks in weeks and the last day of each week into weeks array
        if games[game+1]['week'] != games[game]['week']:
            weeks.append([games[game+1]['week'], games[game+1]['date']])
            print(weeks)

    #sending weeks array to another algorithm to calculate which week this date falls in
    week_num = which_week(weeks)

    print(week_num)
    return week_num

def which_week(weeks):
    #helper function to week_finder comparing beginning and end of weeks defined by current season full schedule
    day = datetime.datetime.today()
    week_found=4
    for date in range(1, len(weeks)-1):
        #checking if the today falls within the last day of weeks in the array
        if datetime.datetime.strptime(weeks[date-1][1], "%Y-%m-%d") < day and datetime.datetime.strptime(weeks[date][1], "%Y-%m-%d") >= day:
            print(datetime.datetime.strptime(weeks[date-1][1], "%Y-%m-%d"))
            print(day)
            print(datetime.datetime.strptime(weeks[date][1], "%Y-%m-%d"))
            week_found = weeks[date][0]
    return week_found



def this_week_nfl(week_number):
    #function to pull this weeks games

    this_week = msf.msf_get_data(league='nfl',season='current',feed='full_game_schedule', week=str(week_number), format='json')
    this_week = this_week['fullgameschedule']
    this_week = this_week['gameentry']

    #deleting game that is within 24 hours
    day = datetime.datetime.today()
    counter = 0
    for game in this_week:
        if datetime.datetime.strptime(game['date'], "%Y-%m-%d") < day:
            this_week.pop(counter)
        counter += 1




    return this_week

def clear_games():
    weekly_games = {}




