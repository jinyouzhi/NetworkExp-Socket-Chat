import argparse
import sys
import time

from Audio import AudioServer, AudioClient
from Video import VideoServer, VideoClient

parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--noself', type=bool, default=False)
parser.add_argument('--level', type=int, default=1)
parser.add_argument('-v', '--version', type=int, default=4)

args = parser.parse_args()

IP = args.host
PORT = args.port
VERSION = args.version
SHOWME = not args.noself
LEVEL = args.level

if __name__ == '__main__':
    vclient = VideoClient(IP, PORT, VERSION, LEVEL)
    vserver = VideoServer(PORT, VERSION)
    aclient = AudioClient(IP, PORT + 1, VERSION)
    aserver = AudioServer(PORT + 1, VERSION)
    vclient.start()
    vserver.start()
    aclient.start()
    aserver.start()
    while True:
        time.sleep(1)
        if not vserver.isAlive() or not vclient.isAlive():
            print("Video connection lost...")
            sys.exit(0)
        if not aserver.isAlive() or not aclient.isAlive():
            print("Audio connection lost...")
            sys.exit(0)
