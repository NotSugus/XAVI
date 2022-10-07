import os
from dotenv import (load_dotenv, find_dotenv)

from flask import Flask,request, jsonify

from google.cloud import storage
from google.oauth2 import service_account

from io import BytesIO
import uuid

import pymongo
from pymongo import MongoClient
import bson.json_util as json_util
import datetime

#==== Cargando variables de entorno ====#
DOTENV = os.environ.get('DOTENV', find_dotenv())
load_dotenv(DOTENV, override=True)

BUCKET_NAME = os.getenv('BUCKET_NAME')
GCP_ACC = os.getenv('GCP_ACC')
MONGO_URI = os.getenv('MONGO_URI')
MONGO_ACC = os.getenv('MONGO_ACC')
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COL = os.getenv('MONGO_COL')
STT_ENDPOINT_HOST = os.getenv('STT_ENDPOINT')
STT_ENDPOINT_PORT = os.getenv('STT_ENDPOINT_PORT')

app = Flask('SpeechToText')

path = "."

#==== Importar modelos de TTS ====#
import dummyTTS

#==== Accesos de google cloud storage ====#
key_json_filename = fr'{path}/config/{GCP_ACC}'
credentials = service_account.Credentials.from_service_account_file(
    key_json_filename,
)
gcs_client = storage.Client(
    project = credentials.project_id,
    credentials = credentials
)
bucket = gcs_client.get_bucket(BUCKET_NAME)

#==== Accesos de Mongo ====#
client = MongoClient(MONGO_URI,
                    tls=True,
                    tlsCertificateKeyFile=f"{path}/config/{MONGO_ACC}")
db = client[MONGO_DB]
collection = db[MONGO_COL]

#===== Funciones del programa =====#
def readText(language, text):
    """
    Lee el texto que se encuentra en GCP
    """
    filename = fr"{language}/3/{text}.txt"                  
    blob = bucket.blob(filename)
    file_obj = BytesIO()
    file_as_string = blob.download_to_file(file_obj)
    file_obj.seek(0)
    content_bytes = file_obj.read()
    with open('input.txt', 'wb') as f:                      
        f.write(content_bytes)


def getAudio(filename,language):
    """
    Genera el audio del texto descargado
    """
    if language == "spanish":
        for name, text in zip([filename], dummyTTS.TTS_ESP()):
            print(f"Audio en español {name} generado a partir de input: {text}")
    elif language == "english":
        for name, text in zip([filename], dummyTTS.TTS_ESP()):
            print(f"Audio en ingles {name} generado a partir de input: {text}")

    text_id = str(uuid.uuid4())
    return text, text_id


def generateJson(user_id, language, filename, text):
    val = {'user_id': user_id,
           'uploadDate': datetime.datetime.utcnow(),
           'language': language,
           'filename': fr'gs://{BUCKET_NAME}/{filename}',
           'audioOut': text,                                    #cambio de nombre para evitar confusiones?
           'stage': 4}
    return val


def uploadAudio(language, audio_id, audio, user_id):
    """
    Sube el audio obtenido a GCP
    """
    filename = fr"{language}/4/{audio_id}.wav"
    blob = bucket.blob(filename)
    blob.upload_from_string(audio)

    dictionary = generateJson(user_id, language, filename, audio)
    val = dictionary
    collection.insert_one(val)
    return dictionary


@app.route('/', methods=["GET"])
def get_tts():
    try:
        # Obteniendo el json del payload
        query_parameters = request.json
    
        user_id = query_parameters.get('UserID')
        audio_id = query_parameters.get('AudioID')
        sesh_id = query_parameters.get('SesionID')
        lang = query_parameters.get('language')
        #lang = 'english'


        # Leyendo el audio .wav
        readText(lang, audio_id)

        # Obteniendo el transcript
        transcript, text_id = getAudio('input.txt',lang)

        # Otebiendo el Json de salida
        value = uploadAudio(lang, text_id, transcript, user_id)

        resp = json_util.dumps(value)
        return resp
    except RuntimeError:
        print("Runtime Error")

if __name__ == "__main__":
    app.run(host= STT_ENDPOINT_HOST, port= STT_ENDPOINT_PORT, debug=True)
