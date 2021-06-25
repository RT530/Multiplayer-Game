from threading import Timer

from flask import Flask, render_template, send_file
from numpy import cos, pi, sin, sqrt, power


class Room:
    def __init__(self, room_id):
        self.room_id = room_id

        # Start update
        self.update()

    def update(self):

        # Loop
        Timer(0.01, self.update).start()

    def bullet(self, bullet_id):
        bullet = room[self.room_id]['bullets'][bullet_id]

        # Is the person that shoot the bullet still online
        if bullet['id'] in room[self.room_id]['players']:
            player = room[self.room_id]['players'][bullet['id']]
            # Is the person that shoot the bullet still alive
            if player['hp'] > 0:
                # Is the bullet in the game area
                if -50 < bullet['x'] < 1050 and -50 < bullet['y'] < 1050:
                    # Move the bullet
                    bullet['x'] += 2.5 * cos(bullet['direction'] * pi / 180)
                    bullet['y'] += 2.5 * sin(bullet['direction'] * pi / 180)

                    # See does the bullet hit any player
                    for player_id in room[self.room_id]['players']:
                        player = room[self.room_id]['players'][player_id]
                        # If it hit
                        if get_distance(player, bullet) < 15:
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


@app.route('/Multiplayer Game')
def multiplayer_game():
    return render_template('Home.html')


@app.route('/data/extra.js')
def extra():
    return send_file('templates/extra.js')


app.run()
