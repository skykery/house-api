from peewee import *
import datetime
db = SqliteDatabase('/db/logs.db', pragmas={'foreign_keys': 1})
# db = SqliteDatabase('logs.db', pragmas={'foreign_keys': 1})

class BaseModel(Model):
    class Meta:
        database = db

class Log(BaseModel):
    room_name = CharField(index=True)
    room_number = IntegerField(index=True)
    message = CharField()
    created = DateTimeField(default=datetime.datetime.now, index=True)

def _init__db():
    db.create_tables([Log])