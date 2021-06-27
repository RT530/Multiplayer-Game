from multiprocessing.pool import ThreadPool
from threading import Timer
from time import time
import webbrowser

from lib.check_import import check_import
from lib.code import get_random_code, get_code
from lib.enforce import enforce

check_import('Flask', 'numpy')
from flask import Flask, render_template, redirect, request, send_file, session
from numpy import cos, pi, sin, sqrt, power, abs


class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.time = time()

        # Start update
        self.update()

    def update(self):

        if room[self.room_id]['join'] > 0 or self.time + 30 < time():
            self.clean_offline_player()
            # Does the room have any player
            if len(room[self.room_id]['players']) == 0:
                # Delete room
                del room[self.room_id]
                return

        for player_id in room[self.room_id]['players']:
            player = room[self.room_id]['players'][player_id]
            if 0 < player['hp'] < 1000:
                player['hp'] += 1

        # Get all bullet id
        bullets_id = [bullet_id for bullet_id in room[self.room_id]['bullets']]
        # If there is any bullet
        if len(bullets_id) > 0:
            # Update all bullet in one time
            ThreadPool(len(bullets_id)).map(self.bullet, bullets_id)

        # Loop
        Timer(0.01, self.update).start()

    # Enforce function clean_offline_player
    @enforce()
    # Clear all offline player
    def clean_offline_player(self):
        for player_id in room[self.room_id]['players']:
            player = room[self.room_id]['players'][player_id]
            # If lass update time is more then 2.5 second
            if player['time'] + 2.5 < time():
                # Delete player from the room
                del room[self.room_id]['players'][player_id]

    def bullet(self, bullet_id):
        # Is the bullet exist
        if bullet_id in room[self.room_id]['bullets']:
            # Get bullet for dictionary
            bullet = room[self.room_id]['bullets'][bullet_id]

            # Is the person that shoot the bullet still online
            if bullet['id'] in room[self.room_id]['players']:
                player = room[self.room_id]['players'][bullet['id']]
                # Is the bullet in the game area and
                # is the person that shoot the bullet still alive
                width, height = room[self.room_id]['size']
                if -50 < bullet['x'] < width + 50 and -50 < bullet['y'] < height + 50 and player['hp'] > 0:
                    # Move the bullet
                    bullet['x'] += 2.5 * cos(bullet['direction'] * pi / 180)
                    bullet['y'] += 2.5 * sin(bullet['direction'] * pi / 180)

                    # See does the bullet hit any player
                    for player_id in room[self.room_id]['players']:
                        if player_id == bullet['id']:
                            continue

                        player = room[self.room_id]['players'][player_id]
                        # If it hit and hit player hp is not zero
                        if get_distance(bullet, player) < 15 and player['hp'] > 0:
                            # Delete the bullet
                            del room[self.room_id]['bullets'][bullet_id]
                            # Decrease player hp
                            player['hp'] -= 100
                            return

                    # See does the bullet hit any other bullets
                    for bullet2_id in room[self.room_id]['bullets']:
                        bullet2 = room[self.room_id]['bullets'][bullet2_id]

                        if bullet2['id'] == bullet['id']:
                            continue

                        # If it hit
                        if get_distance(bullet, bullet2) < 10:
                            # Delete the bullet
                            del room[self.room_id]['bullets'][bullet_id]
                            del room[self.room_id]['bullets'][bullet2_id]
                            return
                    return

            # Delete the bullet
            del room[self.room_id]['bullets'][bullet_id]


# Get distance between two dictionary
def get_distance(a, b):
    return abs(sqrt(power(a['x'] - b['x'], 2) + power(a['y'] - b['y'], 2)))


# Dictionary for saving the room
room = {}
# Defined server
app = Flask(__name__)
app.secret_key = '12345'


# Link URL "/Multiplayer Game" to function multiplayer_game_home
@app.route('/Multiplayer Game')
def multiplayer_game_home():
    return render_template('Home.html')


# Link URL "/Multiplayer Game/create" to function multiplayer_game_create
@app.route('/Multiplayer Game/create', methods=['GET', 'POST'])
def multiplayer_game_create():
    if request.method == 'GET':
        return render_template('Home.html', page='create')
    else:
        requests = request.form.get

        if requests('width') == '':
            width = 1000
        else:
            width = int(requests('width'))
        if requests('height') == '':
            height = 1000
        else:
            height = int(requests('height'))
        if requests('password') == '':
            password = None
        else:
            password = get_code(requests('password'))

        # Generate random room id
        room_id = get_random_code()
        # Defined new room dictionary
        room[room_id] = {
            'join': 0,  # Defined join in room
            'players': {},  # Defined players dictionary in room
            'bullets': {},  # Defined bullets dictionary in room
            'size': [width, height],  # Save room size
            'password': password  # Save password code
        }

        # Start room loop
        Room(room_id)

        session['pass'] = True
        # Redirect to the game page
        return redirect(f'/Multiplayer Game/{room_id}/join')


# Link URL "/Multiplayer Game/<room_id>/join" to function multiplayer_game_join
@app.route('/Multiplayer Game/<room_id>/join', methods=['GET', 'POST'])
def multiplayer_game_join(room_id):
    if room_id in room:
        if request.method == 'GET':
            if room[room_id]['password'] is None or 'pass' in session:
                return render_template('Game.html')
            return render_template('Game.html', password=True)
        else:
            requests = request.form.get

            if room[room_id]['password'] is not None:
                if get_code(requests('password')) != room[room_id]['password'] and 'pass' not in session:
                    return render_template('Game.html', password=True, name=requests('name'))

            # Generate random player id
            player_id = get_random_code()
            # Defined new player dictionary
            room[room_id]['players'][player_id] = {
                'hp': 1000,  # Defined hp for player
                'x': -1000000,  # Defined x coordinate for player
                'y': -1000000,  # Defined y coordinate for player
                'direction': 0,  # Defined direction for player
                'time': time(),  # Defined last update time for player
                'shoot_time': time() + 1,  # Defined last shoot time for player
                'name': request.form.get('name')  # Save player name
            }
            room[room_id]['join'] += 1
            session['player_id'] = player_id
            session['room_id'] = room_id
            session['pass'] = True

            return redirect(f'/Multiplayer Game/{room_id}')
    else:
        return redirect('/Multiplayer Game/room')


# Link URL "/Multiplayer Game/<room_id>" to function multiplayer_game_room
@app.route('/Multiplayer Game/<room_id>')
def multiplayer_game_room(room_id):
    # Is room exist
    if room_id in room:
        if 'pass' in session:
            session.pop('pass', None)
            # Show game page with room_id and player_id variable giving
            return render_template('Game.html', room_size=room[room_id]['size'])
        else:
            # Redirect to the join page
            return redirect(f'/Multiplayer Game/{room_id}/join')

    # Redirect to the home page
    return redirect('/Multiplayer Game')


# Link URL "/Multiplayer Game/<room_id>/update" to function multiplayer_game_update
@app.route('/Multiplayer Game/<room_id>/update', methods=['POST'])
def multiplayer_game_update(room_id):
    # Is room exist
    if room_id in room:
        # Get request from POST
        requests = request.form.get
        # Is player exist
        if requests('player_id') in room[room_id]['players']:
            player = room[room_id]['players'][requests('player_id')]
            # Update last update time
            player['time'] = time()
            # Update x coordinate
            player['x'] = -float(requests('x'))
            # Update y coordinate
            player['y'] = -float(requests('y'))
            # Update direction
            player['direction'] = float(requests('direction'))

            # Get all player data
            players = []
            for player_id in room[room_id]['players']:
                if player_id == requests('player_id'):
                    continue
                player = room[room_id]['players'][player_id]
                if player['hp'] > 0:
                    players.append({
                        'x': player['x'],
                        'y': player['y'],
                        'hp': player['hp'] / 1000,
                        'direction': player['direction']
                    })

            # Get all bullet data
            bullets = []
            for bullet_id in room[room_id]['bullets']:
                bullets.append(room[room_id]['bullets'][bullet_id])

            # Return all players, bullets, and player hp
            player = room[room_id]['players'][requests('player_id')]
            return {
                'players': players,
                'bullets': bullets,
                'hp': player['hp'] / 1000
            }
        else:
            # Return error message if player is not find
            return {'error': 'No such player'}
    else:
        # Return error message if room is not find
        return {'error': 'No such room'}


# Link URL "/Multiplayer Game/<room_id>/shoot" to function multiplayer_game_shoot
@app.route('/Multiplayer Game/<room_id>/shoot', methods=['POST'])
def multiplayer_game_shoot(room_id):
    # Is room exist
    if room_id in room:
        # Get request from POST
        requests = request.form.get
        # Is player exist
        if requests('player_id') in room[room_id]['players']:
            player = room[room_id]['players'][requests('player_id')]
            # If last shoot time is more then 0.25 second
            if player['shoot_time'] + 0.25 < time():
                # Update last shoot time
                player['shoot_time'] = time()
                # Add new bullet to room
                room[room_id]['bullets'][get_random_code()] = {
                    'x': player['x'],  # Defined x coordinate for bullet
                    'y': player['y'],  # Defined y coordinate for bullet
                    'id': requests('player_id'),  # Defined id for bullet
                    'direction': player['direction']  # Defined direction for bullet
                }
    return ''


# Link URL "/Multiplayer Game/room" to function multiplayer_game_room
@app.route('/Multiplayer Game/room')
def multiplayer_game_display():
    # Show join room page
    return render_template('Home.html', page='display', room=room)


@app.route('/extra.js')
def extra():
    return send_file('templates/extra.js')


# Start server
webbrowser.open('http://127.0.0.1:5000/Multiplayer%20Game')
app.run()
