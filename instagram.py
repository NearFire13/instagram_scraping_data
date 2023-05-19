from instagrapi import Client
from datetime import datetime
import time
import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
API_USERNAME = os.environ.get("API_USERNAME")
API_PASSWORD = os.environ.get("API_PASSWORD")
IG_CREDENTIAL_PATH = "./ig_settings.json"
SLEEP_TIME = 60  # en secondes
NBR_THREADS = 6 # le nombre des dernières conversations à surveiller
NBR_MESSAGES = 100 # le nombre de derniers messages à surveiller

cl = Client()

if os.path.exists(IG_CREDENTIAL_PATH):
    cl.load_settings(IG_CREDENTIAL_PATH)
    cl.login(IG_USERNAME, IG_PASSWORD)
else:
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings(IG_CREDENTIAL_PATH)

processed_messages_file = "processed_messages.txt"  # Nom du fichier pour stocker les IDs des messages traités

# Charger les IDs des messages déjà traités depuis le fichier
try:
    with open(processed_messages_file, "r") as file:
        processed_messages = [line.strip() for line in file.readlines()]
except FileNotFoundError:
    processed_messages = []
    
# Connexion à l'API
api_token = "https://myimage-jhs5i76ama-ew.a.run.app/token/"
body = { "username": API_USERNAME, "password": API_PASSWORD }
headers_urlencoded = {'Content-Type': 'application/x-www-form-urlencoded'}
response_token = requests.post(api_token, data=body, headers=headers_urlencoded)
responseJSON = response_token.json();

if response_token.status_code == 200:
    print("Demande de token à l'API envoyé avec succès")
else:
    print("Erreur lors de la demande de token à l'API:", response_token.text)

token = responseJSON["access_token"]
newMessagesToSend = []

while True:

    found = False
    
    for thread in cl.direct_threads(NBR_THREADS) : # Show NBR_THREADS threads

        for message in cl.direct_messages(thread.id, NBR_MESSAGES) : # Show NBR_MESSAGES messages by thread

            if message.id in processed_messages:
                # Ce message a déjà été traité, passer au suivant
                continue
            
            found = True
            
            messageFormat = {
                "content": message.text,
                "date": message.timestamp.strftime("%Y-%m-%d"), #message.timestamp %d-%m-%Y %H:%M:%S
                "reseaux": "Instagram"
            }

            print(messageFormat)
            
            newMessagesToSend.append(messageFormat)
            processed_messages.append(message.id)
    
    # Vérifier si il y a des nouveaux messages
    if not found :
        print("Pas de nouveau message")
    else :
        # Envoyer les messages à l'API
        api_messages = "https://myimage-jhs5i76ama-ew.a.run.app/messages/"
        headers_json = {"Authorization": "Bearer {}".format(token)}
        response_messages = requests.post(api_messages, json=newMessagesToSend, headers=headers_json)
        print(newMessagesToSend)

        if response_messages.status_code == 200:
            print("Messages envoyés avec succès à l'API")
        else:
            print("Erreur lors de l'envoi des messages à l'API:", response_messages.text)
            
            
        # Enregistrer les IDs des messages traités dans le fichier
        with open(processed_messages_file, "w") as file:
            file.write("\n".join(processed_messages))
        print("Messages mis à jour dans le fichier")

    # Attendre pendant un certain temps avant la prochaine vérification
    time.sleep(SLEEP_TIME)  # Attendre SLEEP_TIME secondes avant la prochaine vérification