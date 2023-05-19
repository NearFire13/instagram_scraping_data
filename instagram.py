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
IG_CREDENTIAL_PATH = "./ig_settings.json"
SLEEP_TIME = 60  # en secondes
NBR_THREADS = 6 # le nombre des dernières conversations à surveiller
NBR_MESSAGES = 100 # le nombre de derniers messages à surveiller
API_URL = "https://exemple.com/api/messages" # URL de l'API

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

while True:

    found = False
    
    for thread in cl.direct_threads(NBR_THREADS) : # Show NBR_THREADS threads

        for message in cl.direct_messages(thread.id, NBR_MESSAGES) : # Show NBR_MESSAGES messages by thread

            if message.id in processed_messages:
                # Ce message a déjà été traité, passer au suivant
                continue
            
            found = True
            
            messageFormat = {
                "message": message.text,
                "date": message.timestamp,
                "socialNetwork": "Instagram"
            }

            print(messageFormat)
            
            # Envoyer les messages à l'API REST
            api_endpoint = API_URL
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_endpoint, json=messageFormat, headers=headers)

            if response.status_code == 200:
                print("Message envoyé avec succès à l'API")
            else:
                print("Erreur lors de l'envoi du message à l'API:", response.text)
            
            
            # Ajouter l'ID du message à la liste des messages traités
            processed_messages.append(message.id)
    
    # Vérifier si il y a des nouveaux messages
    if not found :
        print("Pas de nouveau message")
    else :
        # Enregistrer les IDs des messages traités dans le fichier
        with open(processed_messages_file, "w") as file:
            file.write("\n".join(processed_messages))
        print("Messages mis à jour")

    # Attendre pendant un certain temps avant la prochaine vérification
    time.sleep(SLEEP_TIME)  # Attendre SLEEP_TIME secondes avant la prochaine vérification