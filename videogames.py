# Setup Flask imports
from flask import Flask, render_template, request, redirect, jsonify, url_for

# Setup CRUD Imports
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Genre, Game, User, Base

# Setup AntiForgery
from flask import session as login_session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
from flask import make_response

# Setup Session from database
engine = create_engine('sqlite:///gamecatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)


# LOGIN FUNCTIONALITY #
@app.route('/login')
def showLogin():
    state = ''.join(
                    random.choice(string.ascii_uppercase+string.digits)
                    for x in range(32))
    login_session['state'] = state
    genres, createdgenres = sideBar()
    return render_template('login.html', STATE=state, genres=genres,
                           createdgenres=createdgenres)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s" % access_token

    # Exchange Client Token for long-lived server-side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v4.0/me"
    jsondata = json.loads(result)
    token = jsondata['access_token']
    url = 'https://graph.facebook.com/v4.0/me?access_token=%s&fields=name,id,email'\
          % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get User picture
    url = 'https://graph.facebook.com/v4.0/me/picture?access_token=%s&redirect=0&height=200&width=200'\
          % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # Assign user id if not already been assigned
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Output welcome message
    output = ""
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = " width:300px; height: 300px; border-radius: 150px; \
    -webkit-border-radius: 150px; -moz-border-radius:150px;">'
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showGenres'))

    else:
        redirect(url_for('showGenres'))

# END OF LOGIN FUNCTIONALITY #

# USER DB MANAGEMENT #


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# END OF USRE DB MANAGEMENT #

# JSON FUNCTIONALITY #


@app.route('/main/JSON')
def GenreJSON():
    session = DBSession()
    Genre_to_JSON = session.query(Genre).all()
    return jsonify(Genre=[i.serialize for i in Genre_to_JSON])


@app.route('/main/<int:genre_id>/JSON')
def GameJSON(genre_id):
    session = DBSession()
    Games_to_JSON = session.query(Game).filter_by(id_genre=genre_id).all()
    return jsonify(Game=[i.serialize for i in Games_to_JSON])


# END OF JSON FUNCTIONALITY #

# ASSIST FUNCTION #
# sideBar() collect data needed for header.html #


def sideBar():
    session = DBSession()
    genres = session.query(Genre).order_by(asc(Genre.name)).all()
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
        createdgenres = session.query(Genre).filter_by(user_id=user_id)
    else:
        createdgenres = []
    return genres, createdgenres

# Pages #


@app.route('/')
@app.route('/main')
def showGenres():
    genres, createdgenres = sideBar()
    session = DBSession()
    newgames = session.query(Game).order_by(desc(Game.id)).limit(5)
    return render_template('main.html', genres=genres,
                           createdgenres=createdgenres, newgames=newgames)


@app.route('/main/new', methods=['POST', 'GET'])
def createGenre():
    if 'username' in login_session:
        if request.method == 'POST':
            session = DBSession()
            name = request.form['name']
            newGenre = Genre(name=name, count=int(0),
                             user_id=login_session['user_id'])
            session.add(newGenre)
            session.commit()
            return redirect(url_for('showGenres'))
        else:
            genres, createdgenres = sideBar()
            return render_template('newgenre.html',
                                   createdgenres=createdgenres,
                                   genres=genres)
    else:
        return redirect(url_for('showGenres'))


@app.route('/main/<int:genre_id>/delete', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    session = DBSession()
    genreToDelete = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        if login_session['user_id'] == genreToDelete.user_id:
            if genreToDelete.count > 0:
                gamesToDelete = session.query(Game).filter_by(
                                                              id_genre=genre_id
                                                              ).all()
                for game in gamesToDelete:
                    session.delete(game)
            session.delete(genreToDelete)
            session.commit()
            return redirect(url_for('showGenres'))
        else:
            return redirect(url_for('showGenres'))
    else:
        genres, createdgenres = sideBar()
        return render_template('deletegenre.html', genre=genreToDelete,
                               genres=genres, createdgenres=createdgenres)


@app.route('/main/<int:genre_id>/games')
def showGames(genre_id):
    session = DBSession()
    genreToSee = session.query(Genre).filter_by(id=genre_id).one()
    gamesToSee = session.query(Game).filter_by(id_genre=genre_id).all()
    genres, createdgenres = sideBar()
    return render_template('showgames.html', genre=genreToSee,
                           games=gamesToSee, genres=genres,
                           createdgenres=createdgenres)


@app.route('/main/<int:genre_id>/games/new', methods=['GET', 'POST'])
def createGame(genre_id):
    message = None
    session = DBSession()
    genreToAdd = session.query(Genre).filter_by(id=genre_id).one()
    genres, createdgenres = sideBar()
    if request.method == 'POST':
        if 'username' in login_session:
            name = request.form['name']
            existingGame = session.query(Game
                                         ).filter_by(name=name).one_or_none()
            if existingGame is not None:
                message = "Name is already taken by another game.\
                           Please pick a new one"
                return render_template('creategame.html', genre=genreToAdd,
                                       message=message, genres=genres,
                                       createdgenres=createdgenres)
            elif name == "":
                message = "Name is empty, please provide a name"
                return render_template('creategame.html', genre=genreToAdd,
                                       message=message, genres=genres,
                                       createdgenres=createdgenres)
            else:
                description = request.form['description']
                if description == "":
                    description = "Creator did not provide a description...\
                                  Thus it will forever remain a mistery.\n \
                                  Unless you try it."
                newGame = Game(name=name, genre=genreToAdd,
                               description=description,
                               user_id=login_session['user_id'])
                genreToAdd.count += 1
                session.add(newGame)
                session.add(genreToAdd)
                session.commit()
                return redirect(url_for('showGames', genre_id=genreToAdd.id))
        else:
            return redirect(url_for('showGames', genre_id=genreToAdd.id))
    else:
        return render_template('creategame.html', genre=genreToAdd,
                               message=message, genres=genres,
                               createdgenres=createdgenres)


@app.route('/main/<int:genre_id>/games/<int:game_id>/view')
def viewGame(genre_id, game_id):
    session = DBSession()
    genreToSee = session.query(Genre).filter_by(id=genre_id).one()
    gameToSee = session.query(Game).filter_by(id=game_id).one()
    if 'username' in login_session:
        user_id = getUserID(login_session['email'])
    else:
        user_id = None
    genres, createdgenres = sideBar()
    return render_template('seegame.html', genre=genreToSee, game=gameToSee,
                           user_id=user_id, genres=genres,
                           createdgenres=createdgenres)


@app.route('/main/<int:genre_id>/games/<int:game_id>/edit',
           methods=['GET', 'POST'])
def editGame(genre_id, game_id):
    session = DBSession()
    genreToEditFrom = session.query(Genre).filter_by(id=genre_id).one()
    gameToEdit = session.query(Game).filter_by(id=game_id).one()
    message = None
    genres, createdgenres = sideBar()
    if request.method == 'POST':
        user_id = getUserID(login_session['email'])
        if gameToEdit.user_id == user_id:
            name = request.form['newname']
            description = request.form['newdescription']
            # Check that name was not empty:
            if name == "":
                message = "Please provide a name with your edits"
                return render_template('editgame.html', genre=genreToEditFrom,
                                       game=gameToEdit, message=message,
                                       genres=genres,
                                       createdgenres=createdgenres)
            else:
                if description == "":
                    description = "The creator of this game decided to keep\
                    this description empty. No cover to judge this book with.\
                    How misterious."
                gameToEdit.name = name
                gameToEdit.description = description
                session.add(gameToEdit)
                session.commit()
                return redirect(url_for('viewGame', genre_id=genre_id,
                                        game_id=game_id))
        else:
            return redirect(url_for('viewGame', genre_id=genre_id,
                                    game_id=game_id))

    else:
        return render_template('editgame.html', genre=genreToEditFrom,
                               game=gameToEdit, message=message,
                               genres=genres,
                               createdgenres=createdgenres)


@app.route('/main/<int:genre_id>/games/<int:game_id>/delete',
           methods=['GET', 'POST'])
def deleteGame(genre_id, game_id):
    session = DBSession()
    genreToDeleteFrom = session.query(Genre).filter_by(id=genre_id).one()
    gameToDelete = session.query(Game).filter_by(id=game_id).one()
    if request.method == 'POST':
        user_id = getUserID(login_session['email'])
        if user_id == gameToDelete.user_id:
            genreToDeleteFrom.count -= 1
            session.add(genreToDeleteFrom)
            session.delete(gameToDelete)
            session.commit()
            return redirect(url_for('showGames',
                                    genre_id=genreToDeleteFrom.id))
        else:
            return redirect(url_for('showGames',
                                    genre_id=genreToDeleteFrom.id))
    else:
        genres, createdgenres = sideBar()
        return render_template('deletegame.html', genre=genreToDeleteFrom,
                               game=gameToDelete, genres=genres,
                               createdgenres=createdgenres)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
