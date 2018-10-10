import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd, full_game_schedule, week_finder, clear_games, this_week_nfl

#Configure application
app = Flask(__name__)

# Ensure responses arent
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



#connect DB here
db = SQL("sqlite:///fantasy.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route('/login', methods = ["GET", "POST"])
def check():
    session.clear()

    if request.method == "POST":

        #checking inf inputs are blank or not
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        #send user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":

        #check input
        if not request.form.get("username"):
            return apology("Must enter a username", 403)

        #checking password input
        elif not request.form.get("password") or not request.form.get("confirmation") or request.form.get("password") != request.form.get("confirmation"):
            return apology("Please re-enter password and confirmation password", 403)

        #checking if password contains enough numbers
        proposed_pw = request.form.get("password")
        counter = 0
        for letter in proposed_pw:
            if letter.isdigit():
                counter += 1
        if counter < 4:
            return apology("Please make sure your password has at least 4 digits")

        #hashing the password
        password = generate_password_hash(request.form.get("password"))

        #checking to see if the username exists in the database already or not
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if result:
            return apology("Sorry, this username is already taken", 403)

        #inserting password and username into the database
        else:
            db.execute("INSERT INTO users (username, password) VALUES ( :username, :pword)", username = request.form.get("username"), pword = password)

        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        #creating a session using the unique id from the DB
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""
    clear_games()
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/upcoming_games', methods=["GET", "POST"])
@login_required
def upcoming_games():

    if request.method == "GET":
        #pulls full game schedule
        full_games = full_game_schedule()

        #finds which week we are currently in
        week_num = week_finder(full_games)

        #returns JSON dictionary of games in this week
        weekly_games = this_week_nfl(week_num)


        return render_template("upcoming_games.html", future_games = weekly_games)
    # else:
    #     #insert post for when someone submits their picks, query database and save that
    #     return 'Hello'

@app.route('/statistics', methods=["GET", "POST"])
@login_required
def statistics():
    return render_template("statistics.html")

@app.route('/leaderboard', methods=["GET", "POST"])
@login_required
def leaderboard():
    return render_template("leaderboard.html")

@app.route('/myteam', methods=["GET", "POST"])
@login_required
def team_lookup():
    return render_template("myteam.html")




# def errorhandler(e):
#     """Handle error"""
#     return apology(e.name, e.code)


# # listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)