from flask import Flask, jsonify, request
from datetime import datetime
from models import Log, _init__db, db as database
from flask_basicauth import BasicAuth
import time

SHOW_LIMIT = 20

app = Flask(__name__)
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
        self.room_number = int(room_number)
        self.room_name = self.choices.get(self.room_number)
        self.created = datetime.now()
        self.message = self.get_message()

    def get_message(self) -> str:
        return f"{self.created}: Movement from room {self.room_number}"
    
    def emit(self):
        self._save()
        return self.__dict__

    def _save(self):
        Log.create(**self.__dict__)

@app.route('/ping/room/<number>', methods=['GET'])
@basic_auth.required
def ping_room(number):
    r = Response(room_number=request.view_args['number'])
    return r.emit(), 200

@app.route('/show/room/<number>', methods=['GET'])
@basic_auth.required
def show_room(number):
    room_number = request.view_args['number']
    room_logs = Log.select().where(Log.room_number==room_number).order_by(Log.created.desc()).limit(SHOW_LIMIT).dicts()
    return jsonify(results=list(room_logs)), 200

@app.route('/show/rooms', methods=['GET'])
@basic_auth.required
def show_rooms():
    rooms_logs = Log.select().order_by(Log.created.desc()).limit(SHOW_LIMIT).dicts()
    return jsonify(results=list(rooms_logs)), 200

@app.route('/show/last/<limit>', methods=['GET'])
@basic_auth.required
def show_last(limit):
    ogs = Log.select().order_by(Log.created.desc()).limit(limit).dicts()
    return jsonify(results=list(rooms_logs)), 200

if __name__ == '__main__':
    app.run(port=9050)