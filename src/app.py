from flask import Flask, jsonify, request, abort, redirect
from datetime import datetime
from models import Log, _init__db, db as database
from flask_basicauth import BasicAuth
from flask_cors import CORS
import time

SHOW_LIMIT = 20

app = Flask(__name__)
CORS(app)
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin'
basic_auth = BasicAuth(app)
_init__db()

@app.before_request
def _db_connect():
    database.connect()

@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()

class Response(dict):
    choices = {
        1:'bucatarie',
        2:'hol',
        3:'dormitor',
    }
    def __init__(self, room_number):
        self.room_number = room_number
        self.room_name = self.choices[self.room_number]
        self.created = datetime.now()
        self.message = self.get_message()
        self.key = self.get_key()

    def get_message(self) -> str:
        return f"{self.created}: Movement from room {self.room_number}"
    
    def emit(self):
        self._save()
        return self.__dict__

    def _save(self):
        Log.create(**self.__dict__)
    
    @classmethod
    def is_valid_number(cls, number):
        return number in cls.choices.keys()
    @classmethod
    def get_room_by_number(cls, number):
        return cls.choices.get(number, '')
    
    def get_key(self):
        import hashlib
        return hashlib.md5(str(self.created).encode()).hexdigest()

@app.route('/ping/room/<number>', methods=['GET'])
@basic_auth.required
def ping_room(number):
    number = int(request.view_args['number'])
    if not Response.is_valid_number(number):
        return abort(404)
    r = Response(room_number=number)
    return r.emit(), 200

@app.route('/show/room/<number>', methods=['GET'])
@basic_auth.required
def show_room(number):
    number = int(request.view_args['number'])
    room_name = Response.get_room_by_number(number)
    logs = Log.select().where(Log.room_number==number).order_by(Log.created.desc()).limit(SHOW_LIMIT).dicts()
    return jsonify(results=list(logs), room_number=number, room_name=room_name), 200

@app.route('/show/rooms', methods=['GET'])
@basic_auth.required
def show_rooms():
    results = {room_name:list(Log.select().where(Log.room_number==room_number).order_by(Log.created.desc()).limit(SHOW_LIMIT).dicts()) for room_number, room_name in Response.choices.items()}

    return jsonify(results=results), 200

@app.route('/show/last/<limit>', methods=['GET'])
@basic_auth.required
def show_last(limit):
    logs = Log.select().order_by(Log.created.desc()).limit(limit).dicts()
    return jsonify(results=list(logs)), 200

@app.route('/show/last', methods=['GET'])
@basic_auth.required
def show_last_one():
    log = Log.select().order_by(Log.created.desc()).dicts().get()
    return jsonify(result=log), 200


@app.route("/")
def index():
    return redirect('/index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9050, debug=True)
