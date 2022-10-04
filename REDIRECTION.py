from flask import Flask, request, redirect
import os
from dotenv import load_dotenv

load_dotenv()
lan = os.getenv("LANGUAGE")

app = Flask(__name__)

@app.route("/")
def home():
    print("rerouting to /" + str(lan))
    return redirect("/eng")

#rutas de redireccionamiento a la app
@app.route("/eng")
def RedEngApp():
    print("redirect complete, sending to app")
    return redirect("/eng/app/")
@app.route("/esp")
def RedEspApp():
    print("redirect complete, sending to app")
    return redirect("/esp/app/")

#rutas de la app
@app.route("/eng/app/")
def EngApp():
    #aqui va la app de ingles
    print("app ingles")
    return "Done"#hacer push del uri a mongo y del audio a gcp
@app.route("/esp/app/")
def EspApp():
    #aqui va la app de español
    print("app español")
    return "Listo"#hacer push del uri a mongo y del audio a gcp

app.run(host="0.0.0.0", debug=True)    