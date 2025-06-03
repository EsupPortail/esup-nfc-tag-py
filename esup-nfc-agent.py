import threading
import pystray
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import configparser
import logging
import os
import time
import requests
import json
from smartcard.CardType import AnyCardType
from smartcard.CardType import ATRCardType
from smartcard.CardConnection import CardConnection
from smartcard.CardRequest import CardRequest
from smartcard.System import readers
from smartcard.util import toHexString, toBytes


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFC-Agent")

class NfcAgent:
    def __init__(self, server_url, numero_id):
        self.server_url = server_url
        self.numero_id = numero_id
        self.reader = None
        self.connection = None
        self.running = False        
        self.thread = threading.Thread(target=self.main_loop, daemon=True)


    def start(self):
        logger.info("Démarrage de l'agent NFC")
        self.running = True        
        self.thread.start()

    def stop(self, icon=None, item=None):
        logger.info("Arrêt de l'agent NFC")
        self.running = False
        if icon:
            icon.stop()
        
    def connect_reader(self):
        logger.info("[INFO] Surveillance des lecteurs NFC démarrée...")
        cardtype = ATRCardType(toBytes("3B 81 80 01 80 80"))
        cardrequest = CardRequest(timeout=600, cardType=cardtype)
        if self.connection:
            logger.info("Please remove the card")
            cardrequest.waitforcardevent()
            self.disconnect_reader()            
        cardservice = cardrequest.waitforcard()
        logger.info(f"[INFO] Carte détectée.")
        all_readers = readers()
        for reader in all_readers:
            try:
                self.reader = reader
                self.connection = self.reader.createConnection()
                self.connection.connect()
                logger.info(f"[INFO] Carte détectée sur {self.reader}.")
                return
            except:
                logger.info(f"[INFO] Carte retirée de {reader}.")

    def disconnect_reader(self):
        if self.connection:
            self.connection.disconnect()
            self.reader = None
            self.connection = None
            logger.info("Déconnecté du lecteur.")

    def read_csn(self):
        logger.info(self.connection)
        GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.connection.transmit(GET_UID_APDU)
        if sw1 == 0x90 and sw2 == 0x00:
            csn = ''.join(f"{byte:02X}" for byte in data)
            logger.info(f"CSN lu : {csn}")
            return csn
        else:
            raise Exception(f"Erreur lors de la lecture du CSN : SW1={sw1:02X}, SW2={sw2:02X}")

    def send_apdu(self, apdu_hex):
        apdu_bytes = toBytes(apdu_hex)
        data, sw1, sw2 = self.connection.transmit(apdu_bytes)
        response = ''.join(f"{byte:02X}" for byte in data) + f"{sw1:02X}{sw2:02X}"
        logger.info(f"APDU envoyé : {apdu_hex} | Réponse : {response}")
        return response

    def desfire_nfc_comm(self, card_id):
        # Session HTTP persistante avec cookies
        session = requests.Session()    
        result = ""
        while True:
            url = f"{self.server_url}/desfire-ws/?result={result}&numeroId={self.numero_id}&cardId={card_id}"
            response = session.get(url)
            if response.status_code != 200:
                raise Exception(f"Erreur HTTP : {response.status_code}")
            logger.info('Response : ' + response.text)
            nfc_result = response.json()
            apdu = nfc_result.get("fullApdu")
            if apdu == "END":
                logger.info("Communication terminée.")
                break
            elif apdu:
                result = self.send_apdu(apdu)
            else:
                raise Exception("APDU vide reçu du serveur.")


    def main_loop(self):
        logger.info("Agent NFC en attente de carte")
        while self.running:
            try:
                self.connect_reader()
                csn = self.read_csn()
                self.desfire_nfc_comm(csn)
            except Exception as e:
                logger.info(f"Erreur : {e}")

def run_systray(agent: NfcAgent):
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    icon_image = Image.open(icon_path)

    def on_quit(icon, item):
        agent.stop()
        icon.stop()

    menu = Menu(MenuItem('Quitter', on_quit))
    icon = Icon("NFC Agent", icon_image, "Agent NFC", menu)
    icon.run()

    
# Exemple d'utilisation
if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    agent = NfcAgent(
        server_url=config.get('general', 'server_url'),
        numero_id=config.get('general', 'numero_id')
    )
    agent.start()

    logger.info("Lancer le systray dans un thread séparé")
    systray_thread = threading.Thread(target=run_systray, args=(agent,), daemon=True)
    systray_thread.start()
    
    try:
        # Boucle principale légère pour maintenir l'application
        while systray_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interruption clavier - arrêt du programme.")
        agent.stop()
