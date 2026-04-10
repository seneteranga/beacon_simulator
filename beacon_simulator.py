
import random as rnd
import json
import time
from winrt.windows.devices.bluetooth.advertisement import BluetoothLEAdvertisementPublisher, BluetoothLEAdvertisementDataSection
from winrt.windows.storage.streams import DataWriter
import socket

import websockets
import asyncio
from bleak import BleakClient


def generate_beacons(n:int, type: str):
    return [
             {   
            'uuid':'jkhziuzuiiziuehd',
            'major':1,
            'minor':rnd.choice([1,2,3,4]),
            'txpower':-49,
            'rssi': rnd.randint(-30, 20)
            }
            for _ in range(n)
    ]

def beacon_simulator_server_tcp(host='127.0.0.1', port=5200):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ble_server:
            ble_server.bind((host, port))
            ble_server.listen(1)
            print(f"server is listenning in {host}:{port}")

            conn, adrr = ble_server.accept()
            with conn:
                while True:
                    beacons = generate_beacons(5, 'ibeacons')
                    datas = json.dumps(beacons).encode()
                    conn.sendall(datas)
                    print(f"données envoyées: {datas}")
                    time.sleep(2)
    except Exception as e:
        print(f"ble_server error: {e} ")

def beacon_simulator_server_websocket(host='127.0.0.1', port=5200):

    async def handler(websocket):
        try:
            while True:
                beacons = generate_beacons(5, 'ibeacons')
                data = json.dumps(beacons)
                await websocket.send(data)
                print(f"Client Connecté !")

                await asyncio.sleep(2)
        except websockets.exceptions.ConnectionClosed:
            print(f"Client deconnecté !")
        except Exception as e:
            print(f"Une erreur est survenue !{e}")
        
    async def main():
        async with websockets.serve(handler, host, port):
            print(f"server is listenning ind ws://{host}:{port}")
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
