import configparser
import logging
import os
import sys
import tempfile
import threading
import time

import pystray
import requests
from PIL import Image
from filelock import Timeout, FileLock
from pystray import Icon, Menu, MenuItem
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.System import readers
from smartcard.util import toBytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFC-Agent")

# Force GTK backend for pystray on Linux
if sys.platform.startswith('linux'):
    pystray._util._backend = 'gtk'

class NfcAgent:
    def __init__(self, server_url, numero_id):
        self.server_url = server_url
        self.numero_id = numero_id
        self.connection = None
        self.running = False        
        self.thread = threading.Thread(target=self.main_loop, daemon=True)

    def start(self):
        logger.info("Start NFC Agent")
        self.running = True
        self.thread.start()

    def stop(self):
        logger.info("Stopping NFC Agent")
        self.running = False
        
    def connect_reader(self):
        logger.info(f"Connecting to NFC reader...")
        card_type = AnyCardType
        card_request = CardRequest(timeout=600, cardType=card_type)
        if self.connection:
            logger.info("Please remove the card")
            card_request.waitforcardevent()
            self.disconnect_reader()            
        card_request.waitforcard()
        logger.info(f"Card detected, attempting to connect...")
        all_readers = readers()
        for reader in all_readers:
            try:
                self.connection = reader.createConnection()
                self.connection.connect()
                logger.info(f"Connected to reader: {reader}")
                return
            except:
                logger.info(f"Failed to connect to reader: {reader}")

    def disconnect_reader(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            logger.info("Disconnected from NFC reader")

    def read_csn(self):
        logger.info(self.connection)
        GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.connection.transmit(GET_UID_APDU)
        if sw1 == 0x90 and sw2 == 0x00:
            csn = ''.join(f"{byte:02X}" for byte in data)
            logger.info(f"CSN read : {csn}")
            return csn
        else:
            raise Exception(f"Failed to read CSN, SW1: {sw1:02X}, SW2: {sw2:02X}")

    def send_apdu(self, apdu_hex):
        apdu_bytes = toBytes(apdu_hex)
        data, sw1, sw2 = self.connection.transmit(apdu_bytes)
        response = ''.join(f"{byte:02X}" for byte in data) + f"{sw1:02X}{sw2:02X}"
        logger.info(f"APDU sent : {apdu_hex} | Response : {response}")
        return response

    def desfire_nfc_comm(self, card_id):
        # Session HTTP persistante avec cookies
        session = requests.Session()    
        result = ""
        while True:
            url = f"{self.server_url}/desfire-ws/?result={result}&numeroId={self.numero_id}&cardId={card_id}"
            response = session.get(url)
            if response.status_code != 200:
                raise Exception(f"HTTP Error : {response.status_code}")
            logger.info('Response : ' + response.text)
            nfc_result = response.json()
            apdu = nfc_result.get("fullApdu")
            if apdu == "END":
                logger.info("Communication ended.")
                break
            elif apdu:
                result = self.send_apdu(apdu)
            else:
                raise Exception("APDU empty or not found in response")


    def main_loop(self):
        logger.info("NFC Agent main loop started")
        while self.running:
            try:
                self.connect_reader()
                csn = self.read_csn()
                self.desfire_nfc_comm(csn)
            except Exception as e:
                logger.info(f"Error : {e}")

def run_systray(agent: NfcAgent):
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    icon_image = Image.open(icon_path)

    def on_quit(icon):
        agent.stop()
        icon.stop()

    menu = Menu(MenuItem('Exit', on_quit))
    icon = Icon("NFC Agent", icon_image, "Agent NFC", menu)
    icon.run()

def ensure_single_instance():
    lock_path = os.path.join(tempfile.gettempdir(), "esup-nfc-tag-py.lock")
    lock = FileLock(lock_path + ".lock")

    try:
        lock.acquire(timeout=0.1)  # Essaie de prendre le verrou rapidement
    except Timeout:
        print("Another instance is already running. Exiting.")
        sys.exit(1)

    return lock

if __name__ == "__main__":
    lock = ensure_single_instance()
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    agent = NfcAgent(
        server_url=config.get('general', 'server_url'),
        numero_id=config.get('general', 'numero_id')
    )
    agent.start()

    logger.info("systray icon starting...")
    systray_thread = threading.Thread(target=run_systray, args=(agent,), daemon=True)
    systray_thread.start()
    
    try:
        # Maintain the main thread alive while the systray icon is running
        while systray_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, stopping agent...")
        agent.stop()
