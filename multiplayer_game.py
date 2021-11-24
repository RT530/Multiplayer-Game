from multiprocessing.pool import ThreadPool
from threading import Timer
from json import loads
from time import time
import webbrowser

from lib.code import get_code, get_random_code
from lib.check_import import check_import
from lib.data_table import DataTable
from lib.enforce import enforce

check_import('flask')
from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from numpy import cos, sin, sqrt, power, pi
from numpy.random import uniform, randint


# Player class will save the data of the player
class Player:
    def __init__(self, name, player_id):
        self.next = 500
        self.amount = 0
        self.shot_time = time()
        self.kill_by = None
        self.direction = 0
        self.time = time()
        self.name = name
        self.level = 1
        self.score = 0
        self.hp = 1000
        self.max_hp = 1000

        self.id = player_id

        self.bullet_speed = 1
        self.bullet_size = 1
        self.shot_speed = 0

        self.type = 'basis'

        self.armor = 0
        self.hurt = 1

        self.skill = 'armor'
        self.skill_delay = time()

        # self.upgrade_point = 1000 # test only
        self.upgrade_point = 0
        self.upgrade_delay = 0

        self.hit = 0

        self.healing = 0.5

        self.speed = 0.5
        self.max_speed = 2

        self.upgrade_info = [
            ['Max HP', 15, 18, 0, '#0eca0c'],
            ['Healing', 15, 58, 0, '#00ff00'],
            ['Armor', 15, 98, 0, '#bababa'],
            ['Attack', 15, 138, 0, '#ff0f12'],
            ['Shot Speed', 15, 178, 0, '#ffadae'],
            ['Bullet Size', 15, 218, 0, '#d402cd'],
            ['Bullet Speed', 15, 258, 0, '#ffb3fc'],
            ['Speed', 15, 298, 0, '#00f0eb'],
            ['Max Speed', 15, 338, 0, '#143dff']
        ]

        self.x = None
        self.y = None
        # velocity of the player x and y
        self.dx = 0
        self.dy = 0

    # upgrade player ability
    def upgrade(self, upgrade_id):
        # check if upgrade is maximum, if not upgrade chosen option
        if self.upgrade_info[upgrade_id - 1][3] < 5:
            self.upgrade_point -= 1
            self.upgrade_info[upgrade_id - 1][3] += 1
            if upgrade_id == 1:
                self.hp *= 1.1
                self.max_hp *= 1.1
            if upgrade_id == 2:
                self.healing += 0.5
            if upgrade_id == 3:
                self.armor += 50
            if upgrade_id == 4:
                self.hurt += 0.5
            if upgrade_id == 5:
                self.shot_speed += 0.1
            if upgrade_id == 6:
                self.bullet_size += 0.2
            if upgrade_id == 7:
                self.bullet_speed += 0.1
            if upgrade_id == 8:
                self.speed += 0.5
            if upgrade_id == 9:
                self.max_speed += 1
            self.upgrade_delay = time()

    # update player info
    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Constant decrease in velocity
        if self.dx > 0:
            self.dx -= 0.1
        elif self.dx < 0:
            self.dx += 0.1
        if self.dy > 0:
            self.dy -= 0.1
        elif self.dy < 0:
            self.dy += 0.1

        # to increase accuracy
        self.dx = round(self.dx, 2)
        self.dy = round(self.dy, 2)

        # auto health regen
        if 0 < self.hp < self.max_hp:
            if time() > self.hit + 2.5:
                self.hp += self.healing
        elif self.max_hp < self.hp:
            self.hp = self.max_hp

    # add xp to the player
    def add_xp(self, amount):
        self.amount += amount
        if self.amount >= self.next:
            self.amount = self.amount % self.next
            self.upgrade_point += 1
            self.next *= 1.5
            self.level += 1

    # move up
    def up(self):
        if self.dy > -self.max_speed:
            self.dy -= self.speed
        else:
            self.dy = -self.max_speed

    # move down
    def down(self):
        if self.dy < self.max_speed:
            self.dy += self.speed
        else:
            self.dy = self.max_speed

    # move left
    def left(self):
        if self.dx > -self.max_speed:
            self.dx -= self.speed
        else:
            self.dx = -self.max_speed

    # move right
    def right(self):
        if self.dx < self.max_speed:
            self.dx += self.speed
        else:
            self.dx = self.max_speed


# Bullet class will save the info of the bullet
class Bullet:
    def __init__(self, player):
        self.speed = player.bullet_speed * 2.5
        self.size = player.bullet_size * 5
        self.hurt = player.hurt * 100

        self.id = session['player_id']
        self.x, self.y, self.direction = get_pos(player)

    # move bullet
    def update(self):
        self.x += self.speed * cos(self.direction * pi / 180)
        self.y += self.speed * sin(self.direction * pi / 180)


# XP class will save the info of the XP
class XP:
    def __init__(self, x, y):
        self.x = None
        self.y = None
        self.size = None
        self.pos = (x, y)
        self.amount = None

        self.renew()

    # reset xp
    def renew(self):
        x, y = self.pos
        self.x = uniform(x * 25, (x + 1) * 25)
        self.y = uniform(y * 25, (y + 1) * 25)

        self.amount = randint(10, 101)
        self.size = 10 - self.amount / 100 * 10


# Room class will save the info of the room and update
class Room:
    def __init__(self, room_id, width, height, password):
        self.table = DataTable(width, height, 25, 1, 1)
        self.size = [width, height]
        self.password = password
        self.room_id = room_id
        self.time = time()
        self.players = {}
        self.bullets = {}
        self.join = 0

        # Spawn xp ball
        for x in range(0, len(self.table) - 2, 3):
            for y in range(0, len(self.table[x]) - 2, 3):
                xp = XP(x, y)
                self.table.update(xp.x, xp.y, xp)

        self.update()

    # update room status
    def update(self):
        players_id = [player_id for player_id in self.players]
        if len(players_id) > 0:
            ThreadPool(len(players_id)).map(self.player, players_id)

        bullets_id = [bullet_id for bullet_id in self.bullets]
        if len(bullets_id) > 0:
            ThreadPool(len(bullets_id)).map(self.bullet, bullets_id)

        if self.join > 0 or time() > self.time + 30:
            self.clean_offline_player()
            if len(self.players) == 0:
                del room[self.room_id]
                return

        Timer(1 / 60, self.update).start()

    # update the player position in the room
    def player(self, player_id):
        player = self.players[player_id]
        player.update()

        if player.x < 10:
            player.x = 10
        elif player.x > self.size[0] - 10:
            player.x = self.size[0] - 10

        if player.y < 10:
            player.y = 10
        elif player.y > self.size[1] - 10:
            player.y = self.size[1] - 10

        if player.hp <= 0:
            self.table.delete(player.x, player.y, player_id)

    # update the bullet in the room
    def bullet(self, bullets_id):
        """
            Function run through a bullet position and check if it hit other players or bullets or xp,
            if it hit a player then player health decreases, and delete the bullet.
            If it hit another bullet that's not from the same player, it will cancel its damage with that
            bullet or xp ball and if the damage falls to 0 or negative then delete bullet, or decrease its
            damage if the xp ball or enemy bullet has less damage.
        """
        bullet = self.bullets[bullets_id]
        bullet.update()

        if bullet.id in self.players:
            player = self.players[bullet.id]
            if -25 < bullet.x < self.size[0] + 25 and \
                    -25 < bullet.y < self.size[1] + 25 and \
                    bullet.hurt > 0:
                self.table.update(bullet.x, bullet.y, bullet, bullets_id)
                for data in self.table.get_by_pos(bullet.x, bullet.y):
                    if isinstance(data, Player):
                        if get_distance(bullet, data) < bullet.size + 10 and bullet.id != data.id:
                            bullet.hurt -= data.armor
                            if bullet.hurt > 0:
                                data.hp -= bullet.hurt
                            del self.bullets[bullets_id]
                            self.table.delete(bullet.x, bullet.y, bullets_id)

                            if data.hp <= 0:
                                player.score += 1000
                                data.kill_by = player.name

                                amount = data.amount / 2
                                if data.level > player.level:
                                    amount += (data.level - player.level) * 100
                                elif data.level == player.level:
                                    amount += 100
                                elif data.level < player.level:
                                    amount += 50

                                player.add_xp(amount)
                            else:
                                data.hit = time()
                                player.score += 10
                    elif isinstance(data, Bullet):
                        if bullet.id != data.id:
                            if get_distance(bullet, data) < bullet.size + data.size:
                                hurt = bullet.hurt
                                bullet.hurt -= data.hurt
                                data.hurt -= hurt
                    elif isinstance(data, XP):
                        if data.amount != 0 and get_distance(bullet, data) < data.size + bullet.size:
                            bullet.hurt -= data.amount
                            Timer(10, data.renew).start()
                            player.add_xp(data.amount)
                            data.amount = 0
            else:
                del self.bullets[bullets_id]
                self.table.delete(bullet.x, bullet.y, bullets_id)
        else:
            del self.bullets[bullets_id]
            self.table.delete(bullet.x, bullet.y, bullets_id)

    # add bullet to the room (when player shoots)
    def add_bullet(self, player_id):
        player = self.players[player_id]
        if player.hp > 0:
            self.bullets[get_random_code()] = Bullet(player)

    # remove all offline players 5 second.
    @enforce
    def clean_offline_player(self):
        for player_id in [player_id for player_id in self.players]:
            if time() > self.players[player_id].time + 5:
                player = self.players[player_id]
                del self.players[player_id]
                self.table.delete(player.x, player.y, player_id)

    # add player to the room
    def add_player(self, name):
        player_id = get_random_code()

        if name == '':
            player = Player(player_id, player_id)
        else:
            player = Player(name, player_id)

        player.x = uniform(10, self.size[0] - 10)
        player.y = uniform(10, self.size[0] - 10)
        self.players[player_id] = player
        self.join += 1

        return player_id


class Data:
    """
        Data class will classify the data, preparation for web display as every unique class will be
        drawn separately, therefore decreases webserver cpu stress (optimization)
    """

    # initiating program
    def __init__(self, data, player_id):
        self.xp = []
        self.players = []
        self.bullets = []
        self.player_id = player_id

        ThreadPool(len(data)).map(self.sort, data)

    # sorting data into player, bullet and xp
    def sort(self, data):
        if isinstance(data, Player):
            if data.id != self.player_id:
                self.players.append({
                    'x': data.x,
                    'y': data.y,
                    'direction': data.direction,
                    'hp': data.hp / data.max_hp
                })
        elif isinstance(data, Bullet):
            self.bullets.append({
                'x': data.x,
                'y': data.y,
                'id': data.id
            })
        elif isinstance(data, XP):
            if data.amount != 0:
                self.xp.append({
                    'x': data.x,
                    'y': data.y,
                    'size': data.size
                })


# calculate the distance between two class (bullet / xp / player)
def get_distance(a, b):
    return abs(sqrt(power(a.x - b.x, 2) + power(a.y - b.y, 2)))


# get the bullet exit position
def get_pos(player):
    # for future, right now only one type of tank
    direction = player.direction * pi / 180
    if player.type == 'basis':
        x = player.x + 20 * cos(direction)
        y = player.y + 20 * sin(direction)
        return x, y, player.direction


room = {}
app = Flask(__name__)
app.secret_key = 'BGdgjcEgHaJAj'


# link /extra.js to function extra
@app.route('/extra.js')
def extra():
    # extension library for Javascript
    return send_file('templates/extra.js')


# link /Multiplayer Game to function multiplayer_game_home
@app.route('/Multiplayer Game')
def multiplayer_game_home():
    # home page
    return render_template('Home.html')


# link /Multiplayer Game/create to function multiplayer_game_create
@app.route('/Multiplayer Game/create', methods=['GET', 'POST'])
def multiplayer_game_create():
    # room creation page with default values
    if request.method == 'GET':
        return render_template('Home.html', page='create')
    elif request.method == 'POST':
        requests = request.form.get
        room_id = get_random_code()
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

        room[room_id] = Room(room_id, width, height, password)

        session['pass'] = True
        return redirect(f'/Multiplayer Game/{room_id}/join')


# link /Multiplayer Game/<room_id> to function multiplayer_game_room
@app.route('/Multiplayer Game/<room_id>')
def multiplayer_game_room(room_id):
    """
       if connection to server was restarted
       then password will need to be reentered
    """
    if room_id in room:
        if 'pass' in session and 'player_id' in session:
            session.pop('pass', None)
            room_size = room[room_id].size
            return render_template('Game.html', room_size=room_size)
        else:
            return redirect(f'/Multiplayer Game/{room_id}/join')
    else:
        if len(room) == 0:
            return redirect('/Multiplayer Game')
        return redirect('/Multiplayer Game/room')


# link /Multiplayer Game/<room_id>/join to function multiplayer_game_join
@app.route('/Multiplayer Game/<room_id>/join', methods=['GET', 'POST'])
def multiplayer_game_join(room_id):
    if room_id in room:
        # default cookie value
        if request.method == 'GET':
            if 'pass' not in session:
                session['pass'] = False

            if 'room_id' not in session:
                session['room_id'] = None

            if 'player_name' not in session or session['room_id'] != room_id:
                session['player_name'] = ''

            """
                If user is creator then first time does not require password, 
                if there is a password. 
            """
            if room[room_id].password is None or session['pass']:
                return render_template('Game.html', name=session['player_name'])
            return render_template('Game.html', password=True, name=session['player_name'])
        elif request.method == 'POST':
            """
                if there is a password for the game room,
                check password and if correct and will be assigned 
                player_id, room_id and password cookie
                If password wrong send back to password page again
            """
            requests = request.form.get

            if room[room_id].password is not None:
                if get_code(requests('password')) != room[room_id].password and not session['pass']:
                    return render_template('Game.html', password=True, name=requests('name'))

            session['player_id'] = room[room_id].add_player(requests('name'))
            session['room_id'] = room_id
            session['pass'] = True
            return redirect(f'/Multiplayer Game/{room_id}')
    else:
        if len(room) == 0:
            return redirect('/Multiplayer Game')
        return redirect('/Multiplayer Game/room')


# link /Multiplayer Game/room to function multiplayer_game_show
@app.route('/Multiplayer Game/room')
def multiplayer_game_show():
    """
        if player choose join room but no room exist,
        then create one.
    """
    if len(room) == 0:
        return redirect('/Multiplayer Game/create')
    return render_template('Home.html', page='display', room=room)


# link /Multiplayer Game/update to function multiplayer_game_update
@app.route('/Multiplayer Game/update')
def multiplayer_game_update():
    """
        check if room and player exists, then
        receive player status and organise data and update player status
        and room status back to server.
    """
    room_id = session['room_id']
    if room_id in room:
        player_id = session['player_id']
        if player_id in room[room_id].players:
            player = room[room_id].players[player_id]
            session['player_name'] = player.name
            player.time = time()

            requests = request.args.get
            status = loads(requests('status'))
            height = status['height'] / 2
            width = status['width'] / 2

            if player.hp > 0:
                player.direction = status['direction']
                for i in range(1, 10):
                    if player.upgrade_point > 0 and status[str(i)] and time() > player.upgrade_delay + 0.5:
                        player.upgrade(i)
                if status['up']:
                    player.up()
                if status['down']:
                    player.down()
                if status['left']:
                    player.left()
                if status['right']:
                    player.right()
                if status['shooting'] and player.shot_time < time():
                    room[room_id].add_bullet(player_id)
                    player.shot_time = time() + (1 - player.shot_speed)

            data = Data(room[room_id].table.get_by_area(
                player.x - width, player.y - height,
                player.x + width, player.y + height,
                25
            ), player_id)

            if player.hp > 0:
                room[room_id].table.update(player.x, player.y, player, player_id)

            return {
                'x': -player.x,
                'y': -player.y,
                'xp_ball': data.xp,
                'players': data.players,
                'bullets': data.bullets,
                'direction': player.direction,
                'hp': player.hp / player.max_hp,
                'level': player.level,
                'size': room[room_id].size,
                'score': player.score,
                'kill_by': player.kill_by,
                'xp': player.amount / player.next,
                'upgrade': player.upgrade_info,
                'upgrade_point': player.upgrade_point
            }
        else:
            return {'error': 'No such player'}
    else:
        return {'error': 'No such room'}


# link /Multiplayer Game/map to function multiplayer_game_map
@app.route('/Multiplayer Game/map')
def multiplayer_game_map():
    """
        check for room existence and calculate the ratio between the map and the room
        go through all the players inside the room and whether they are alive (Hp > 0)
    """
    game_map = []
    room_id = session['room_id']
    if room_id in room:
        offset = 250 / max(room[room_id].size)
        for player_id in room[room_id].players:
            player = room[room_id].players[player_id]
            if player.hp > 0:
                if player_id == session['player_id']:
                    color = '#0000ff'
                else:
                    color = '#ff0000'
                game_map.append({
                    'x': player.x * offset,
                    'y': player.y * offset,
                    'color': color
                })
        return jsonify(game_map)
    return {'error': 'No such room'}


# open the website to the game automation
webbrowser.open('http://127.0.0.1:5000/Multiplayer%20Game')
# Start server
app.run('0.0.0.0')
