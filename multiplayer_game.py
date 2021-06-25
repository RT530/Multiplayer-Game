from multiprocessing.pool import ThreadPool
from threading import Timer
from time import time

from lib.check_import import check_import
from lib.code import get_random_code
from lib.enforce import enforce

check_import('Flask', 'numpy')

from flask import Flask, render_template, send_file, redirect, request
from numpy import cos, pi, sin, sqrt, power


class Room:
    def __init__(self, room_id):
        self.room_id = room_id

        # Start update
        self.update()

    def update(self):
        self.clean_offline_player()

        for player_id in room[self.room_id]['players']:
            player = room[self.room_id]['players'][player_id]
            if 0 < player['hp'] < 1000:
                player['hp'] += 1

        bullets_id = [bullet_id for bullet_id in room[self.room_id]['bullets']]
        if len(bullets_id) > 0:
            ThreadPool(len(bullets_id)).map(self.bullet, bullets_id)

        # Loop
        Timer(0.01, self.update).start()

    @enforce()
    def clean_offline_player(self):
        for player_id in room[self.room_id]['players']:
            player = room[self.room_id]['players'][player_id]
            if player['time'] + 2.5 < time():
                del room[self.room_id]['players'][player_id]

    def bullet(self, bullet_id):
        # Get bullet for dictionary
        bullet = room[self.room_id]['bullets'][bullet_id]

        # Is the person that shoot the bullet still online
        if bullet['id'] in room[self.room_id]['players']:
            player = room[self.room_id]['players'][bullet['id']]
            # Is the bullet in the game area
            # Is the person that shoot the bullet still alive
            if -50 < bullet['x'] < 1050 and -50 < bullet['y'] < 1050 and player['hp'] > 0:
                # Move the bullet
                bullet['x'] += 2.5 * cos(bullet['direction'] * pi / 180)
                bullet['y'] += 2.5 * sin(bullet['direction'] * pi / 180)

                # See does the bullet hit any player
                for player_id in room[self.room_id]['players']:
                    if player_id == bullet['id']:
                        continue

                    player = room[self.room_id]['players'][player_id]
                    # If it hit
                    if get_distance(player, bullet) < 15 and player['hp'] > 0:
                        # Delete the bullet
                        del room[self.room_id]['bullets'][bullet_id]
                        # Decrease player hp
                        player['hp'] -= 100
                        return
                return

        # Delete the bullet
        del room[self.room_id]['bullets'][bullet_id]


def get_distance(a, b):
    return abs(sqrt(power(a['x'] - b['x'], 2) + power(a['y'] - b['y'], 2)))


# Dictionary for saving the room
room = {}
# Defined server
app = Flask(__name__)


# When call URL "/Multiplayer Game" run multiplayer_game_home
@app.route('/Multiplayer Game')
def multiplayer_game_home():
    return render_template('Home.html')


@app.route('/Multiplayer Game/create')
def multiplayer_game_create():
    room_id = get_random_code()
    room[room_id] = {
        'players': {},
        'bullets': {}
    }

    # Start room
    Room(room_id)

    # Redirect to the game page
    return redirect(f'/Multiplayer Game/{room_id}')


@app.route('/Multiplayer Game/<room_id>')
def multiplayer_game_room(room_id):
    if room_id in room:
        player_id = get_random_code()
        room[room_id]['players'][player_id] = {
            'hp': 1000,
            'x': -1000000,
            'y': -1000000,
            'direction': 0,
            'time': time(),
            'shoot_time': time() + 1
        }

        return render_template('Game.html', room_id=room_id, player_id=player_id)
    return redirect('/Multiplayer Game')


@app.route('/Multiplayer Game/<room_id>/update', methods=['POST'])
def multiplayer_game_update(room_id):
    if room_id in room:
        requests = request.form.get
        if requests('player_id') in room[room_id]['players']:
            player = room[room_id]['players'][requests('player_id')]
            player['time'] = time()
            player['x'] = -float(requests('x'))
            player['y'] = -float(requests('y'))
            player['direction'] = float(requests('direction'))

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

            bullets = []
            for bullet_id in room[room_id]['bullets']:
                bullet = room[room_id]['bullets'][bullet_id]
                bullets.append({
                    'x': bullet['x'],
                    'y': bullet['y'],
                    'id': bullet['id']
                })

            player = room[room_id]['players'][requests('player_id')]
            return {
                'players': players,
                'bullets': bullets,
                'hp': player['hp'] / 1000
            }
        else:
            return {'error': 'No such player'}
    else:
        return {'error': 'No such room'}


@app.route('/Multiplayer Game/<room_id>/shooting', methods=['POST'])
def multiplayer_game_shooting(room_id):
    if room_id in room:
        requests = request.form.get
        if requests('player_id') in room[room_id]['players']:
            player = room[room_id]['players'][requests('player_id')]
            if player['shoot_time'] + 0.25 < time():
                player['shoot_time'] = time()
                room[room_id]['bullets'][get_random_code()] = {
                    'x': player['x'],
                    'y': player['y'],
                    'id': requests('player_id'),
                    'direction': player['direction']
                }
    return ''


@app.route('/data/extra.js')
def extra():
    return send_file('templates/extra.js')


app.run()
