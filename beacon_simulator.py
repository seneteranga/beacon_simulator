
import random as rnd
import os
import json
import time
from datetime import datetime
from winrt.windows.devices.bluetooth.advertisement import BluetoothLEAdvertisementPublisher, BluetoothLEAdvertisementDataSection
from winrt.windows.storage.streams import DataWriter
import socket

import websockets
from urllib.parse import urlparse, parse_qs
import asyncio
from bleak import BleakClient


def generate_beacons(n:int=5, type: str=''):
    return [
            {   
            'id': i+1,
            'uuid':'jkhziuzuiiziuehd',
            'major':1,
            'minor':rnd.choice([1,2,3,4]),
            'txpower':-49,
            'rssi': rnd.randint(-30, 20)
            }
            for i in range(n)
    ]
def get_beacon(beacons, id):
    for beacon in beacons:
        if(beacon['id']==id):
            return beacon
def beacon_simulator_server_tcp(host='127.0.0.1', port=5200):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ble_server:
            ble_server.bind((host, port))
            ble_server.listen(1)
            print(f"server is listenning in {host}:{port}")
            conn, addrr = ble_server.accept()
            print(f"nouveau appareil connecté: {addrr}")
            with conn:
                while True:
                    beacons = generate_beacons(5, 'ibeacons')
                    print(f"preparation des données encours .....")
                    datas = json.dumps(beacons).encode() 
                    print("preparation des données terminée !")
                    print("envoie des données encours ....")
                    conn.sendall(datas)
                    print(f"données envoyée !")
                    time.sleep(2)
    except Exception as e:
        print(f"ble_server error: {e} ")
def beacon_simulator_server_websocket(host='127.0.0.1', port=5200):
    async def handler(websocket):
        path = websocket.request.path
        allbeacons= generate_beacons(5, 'ibeacons')
        try:        
            if path == '/scan' :   
                n = rnd.choice([3, 4, 5, 2])  
                rnd.shuffle(allbeacons)
                beacons = []
                for i in range(n):
                    beacons.append(allbeacons[i])
                data = json.dumps(beacons)
                await websocket.send(data)
                ip_client, port_client = websocket.remote_address                
                os.system("cls")
                print(f"Serveur {host}:{port}")
                print(f"Appareil Scanner connecté {ip_client}:{port_client}....")
                print(f"{datetime.now()} ....")
            elif path == '/stream':
                while True:
                    n = rnd.choice([3, 4, 5, 2])
                    allbeacons= generate_beacons(5, 'ibeacons')
                    rnd.shuffle(allbeacons)
                    beacons = []
                    for i in range(n):
                        beacons.append(allbeacons[i])
                    data = json.dumps(beacons)
                    await websocket.send(data)
                    ip_client, port_client = websocket.remote_address                
                    os.system("cls")
                    print(f"Serveur {host}:{port}")
                    print(f"Appareil streamer connecté: {ip_client}:{port_client}....")
                    print(f"{datetime.now()} ....")
                    await asyncio.sleep(1)
            else:
                urls_args = urlparse(path)
                params = parse_qs(urls_args.query)
                id= params.get('b', [None])[0]
                print(id)
                beacon = get_beacon(allbeacons, int(id))
                print(beacon)
                if id:
                    while True:
                        beacon['rssi']= rnd.randint(-30, 20)
                        data = json.dumps(beacon)
                        print(data)
                        await websocket.send(data)
                        ip_client, port_client = websocket.remote_address                
                        os.system("cls")
                        print(f"Serveur {host}:{port}")
                        print(f"Appareil streamer connecté {ip_client}:{port_client}....")
                        print(f"{datetime.now()} ....")
                        await asyncio.sleep(1)            
                pass
        except websockets.exceptions.ConnectionClosed:
            print(f"Appareil deconnecté !")
        except Exception as e:
            print(f"Une erreur est survenue !{e}")        
    async def main():
        async with websockets.serve(handler, host, port):
            print(f"server is listenning in ws://{host}:{port}")
            await asyncio.Future()

    asyncio.run(main())
async def beacon_simulator_bluetooth():
    publisher = BluetoothLEAdvertisementPublisher()
    writer = DataWriter()
    uuid = bytes.fromhex('00112233445566778899aabbccddeeff')
    writer.write_bytes(uuid)
    writer.write_uint16(1)
    writer.write_int16(1)
    writer.write_uint16(200)
    section = BluetoothLEAdvertisementDataSection()
    section.data= writer.detach_buffer()
    publisher.advertisement.data_sections.append(section)
    publisher.start()

beacon_simulator_server_websocket()
