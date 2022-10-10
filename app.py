#====== Importar dependencias ======#
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
import soundfile as sf
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder

# import tts_es

spec_generator = SpectrogramGenerator.from_pretrained(model_name="tts_en_fastpitch").cuda()
vocoder = Vocoder.from_pretrained(model_name="tts_hifigan").cuda()

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

# Funcion que lee el texto de entrada en GCP de acuerdo al text_id 
def readText(text_id, language):
    """
    Lee el texto que se encuentra en GCP
    """
    filename = fr"{language}/3/{text_id}.txt"                  
    blob = bucket.blob(filename)
    file_obj = BytesIO()
    file_as_string = blob.download_to_file(file_obj)
    file_obj.seek(0)
    content_bytes = file_obj.read()
    with open('input.txt', 'wb') as f:                      
        f.write(content_bytes)
    with open('input.txt', 'rb') as f:
        text = f.readline()
        return text

# Funcion que genera el audio de salida en funcion del texto de entrada.
# Regresa el audio_id con el cual identificar el audio generado
def getAudio(text_id,language):
    """
    Genera el audio del texto descargado
    """
    # Leyendo el texto .txt
    text = readText(text_id,language)

    audio_id = str(uuid.uuid4())
    if language == "english":
        parsed = spec_generator.parse(f"{text}")
        spectrogram = spec_generator.generate_spectrogram(tokens=parsed)
        audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)
        sf.write(f"{audio_id}.wav", audio.to('cpu').detach().numpy()[0], 22050)
    # elif language == "spanish":
    #     tts_es.AUDIO_ES(text,audio_id)
    return audio_id

# Genera el diccionario JSON para subida a MONGO
def generateJson(session_id, gcp_filename, language):
    val = {'user_id': session_id,
           'uploadDate': datetime.datetime.utcnow(),
           'language': language,
           'filename': fr'gs://{BUCKET_NAME}/{gcp_filename}',                                    
           'stage': 'audio generado'}
    return val

# Sube el audio a GCP y el diccionario a MONGO
def uploadAudio(language, audio_id, session_id):
    """
    Sube el audio obtenido a GCP
    """
    gcp_filename = fr"{language}/4/{audio_id}.wav"
    audio_file = f"{audio_id}.wav"
    blob = bucket.blob(gcp_filename)
    blob.upload_from_filename(audio_file)             #it is uploading the file name, not the file.

    dictionary = generateJson(session_id, gcp_filename, language)
    val = dictionary
    collection.insert_one(val)
    return dictionary


@app.route('/', methods=["GET"])
def get_tts():
    try:
        # Obteniendo el json del payload
        query_parameters = request.json
        text_id = query_parameters.get('text_id')
        session_id = query_parameters.get('session_id')
        #lang = query_parameters.get('language')
        lang = 'english'

        # Obteniendo el audio
        audio_id = getAudio(text_id,lang)

        # Otebiendo el Json de salida
        value = uploadAudio(lang, audio_id, session_id)

        resp = json_util.dumps(value)
        return resp
    except RuntimeError:
        print("Runtime Error")

if __name__ == "__main__":
    app.run(host= STT_ENDPOINT_HOST, port= STT_ENDPOINT_PORT, debug=True)