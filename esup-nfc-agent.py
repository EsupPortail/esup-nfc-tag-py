import configparser
import os
import time
import requests
import json
from smartcard.System import readers
from smartcard.util import toHexString, toBytes

class EncodingService:
    def __init__(self, server_url, numero_id):
        self.server_url = server_url
        self.numero_id = numero_id
        self.reader = None
        self.connection = None

    def connect_reader(self):
        print("[INFO] Surveillance des lecteurs NFC démarrée...")
        
        while True:
            all_readers = readers()
            for reader in all_readers:
                try:
                    self.reader = reader
                    self.connection = self.reader.createConnection()
                    self.connection.connect()
                    print(f"[INFO] Carte détectée sur {self.reader}.")
                    return
                except:
                    print(f"[INFO] Carte retirée de {reader}.")

                time.sleep(0.5)  # Polling toutes les 500ms

    def disconnect_reader(self):
        if self.connection:
            self.connection.disconnect()
            print("Déconnecté du lecteur.")

    def read_csn(self):
        GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.connection.transmit(GET_UID_APDU)
        if sw1 == 0x90 and sw2 == 0x00:
            csn = ''.join(f"{byte:02X}" for byte in data)
            print(f"CSN lu : {csn}")
            return csn
        else:
            raise Exception(f"Erreur lors de la lecture du CSN : SW1={sw1:02X}, SW2={sw2:02X}")

    def send_apdu(self, apdu_hex):
        apdu_bytes = toBytes(apdu_hex)
        data, sw1, sw2 = self.connection.transmit(apdu_bytes)
        response = ''.join(f"{byte:02X}" for byte in data) + f"{sw1:02X}{sw2:02X}"
        print(f"APDU envoyé : {apdu_hex} | Réponse : {response}")
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
            print('Response : ' + response.text)
            nfc_result = response.json()
            apdu = nfc_result.get("fullApdu")
            if apdu == "END":
                print("Communication terminée.")
                break
            elif apdu:
                result = self.send_apdu(apdu)
            else:
                raise Exception("APDU vide reçu du serveur.")


# Exemple d'utilisation
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    service = EncodingService(
        server_url=config.get('general', 'server_url'),
        numero_id=config.get('general', 'numero_id')
    )
    while True:        
        try:
            service.connect_reader()
            csn = service.read_csn()
            # Choisissez l'une des méthodes suivantes selon votre besoin
            service.desfire_nfc_comm(csn)
            # service.csn_nfc_comm(csn)
        except Exception as e:
            print(f"Erreur : {e}")
        finally:
            service.disconnect_reader()
