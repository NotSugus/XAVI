from pyexpat.errors import messages
from flask import Flask
from flask import request
import collections
from pymongo import MongoClient
from tts_es import AUDIO_ES
from tts_en import AUDIO_EN

mongo_uri = 'mongodb://localhost:27017'
client = MongoClient(mongo_uri)

db = client['appdb']
col = db['users']

app = Flask(__name__)

@app.route('/')
def home():
    print("Home Page in")
    return("Home page")

@app.route('/esp/<id>')
def users_action(id):
    results = col.find({'id': int(id)})
    for n in results:
        message = n['message']
        print("Message id: " + id)
        print("Mensaje a procesar: " + message)
    AUDIO_ES(message)
    return("Audio generado")

@app.route('/eng/<id>')
def users_action(id):
    results = col.find({'id': int(id)})
    for n in results:
        message = n['message']
        print("Message id: " + id)
        print("Mensaje a procesar: " + message)
    AUDIO_ES(message)
    return("Audio generado")

app.run(host = '0.0.0.0',debug=True)