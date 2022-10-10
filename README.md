# TTS ENDPOINT

El endpoint TTS de la aplicación TTS es un espejo del (endpoint STT)[https://git.ndscognitivelabs.com/estancia-profesional-itesm/experiencia-2-nvidia-chatbot/backend/-/tree/master/endpoint_stt]. La logica es la misma para *GCP, MONGO y el payload* con algunos cambios en funcionalidad.

## ESPECIFICACIONES

### ESTRUCTURA PROYECTO

Los archivos principales del proyecto son los siguientes:

* *config* es el directorio donde se encuentran los certificados para conectarse a GCP y MONGO, asi como configuraciones para el modelo TTS en español

* *TTS* es el directorio con dependencias del modelo TTS en español

* Los archivos con inicio *tts_* son los modelos TTS en ambos lenguajes.

### APP

La estructura basica de la app se divide en tres secciones:

1. Dependencias y credenciales
2. Funciones de programa
3. App de flask

En estas tres secciones, la estructura de la aplicacion es basicamente la misma. El unico cambio es en el nombre de variables y archivos de input y output, para reflejar las distintas funciones de las apps.

El lenguaje de funcionamiento de la app sigue "hardocodeado" a ingles. Cabe destacar que en la app STT no afecta este hecho, pues se utiliza un modelo bilingüe. No obstante, TTS utiliza dos modelos por separado, donde el lenguaje del payload afecta la seleccion de modelo.

El modelo de TTS en español está presente en la aplicación, pero está comentado por cuetiones de simplificar la POC.

### PAYLOAD

NOTA: Falta por confirmar el formato final del json schema.

*Formato de payload de entrada:*

Se requiere el id de la sesión y del texto input del modelo, en conjunto con el idioma a utilizar para la  aplicación.

```
{
    "text_id": "016c4b5a-5a24-4b6b-a72b-c4375870b598",
    "session_id": "uuid",
    "language": "english"
}
```

*Formato de payload de salida:*

```
{
    "user_id": "ca44a7d9-dd84-4222-99dc-5dfbf6ae5eb7",
    "uploadDate": {
        "$date": "2022-10-06T08:21:29.923Z"
    },
    "language": "english",
    "filename": "gs://bucket-nds-stt-endpoint/english/4/0ddf3f8d-f0d1-4d4c-8e13-3da163d30a86.wav",
    "audioOut": " i also need to learn how to manage my work load",
    "stage": "audio generado",
    "_id": {
        "$oid": "633e9009c4f12d25a0193e98"
    }
}
```

### BUGS

Actualmente, no bugs reportados para la POC.

## Servicios en la nube

### GCP

El formato de los directorios a utilizar sigue siendo "language/stage/uuid.extension". Por ejemplo: english/3/0ddf3f8d-f0d1-4d4c-8e13-3da163d30a86.txt

Los stages para TTS son 3 y 4, en ambos idiomas. El stage 3 es utilizado para el input .txt del TTS, mientras que el stage 4 es para los archivos .wav de salida.

### MONGO

La coleccion utilizada es "texto-audio". El formato es prácticamente el mismo que en STT.

### CREDENCIALES

Las credenciales se ubican en la carpeta config. El programa corre sin la necesidad de acciones adicionales. Los archivos son:

* *mongo_db_certificate.pem* para MONGO

* *nds-proyecto-123-credentials.json* para GCP