import pickle
import struct
import threading
import time
from socket import *

from pyaudio import *

CHUNK = 1024
FORMAT = paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5


class AudioServer(threading.Thread):
    def __init__(self, port, version):
        threading.Thread.__init__(self)
        self.daemon = True
        self.Addr = ('', port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        elif version == 6:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.p = PyAudio()
        self.stream = None

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def run(self):
        print("AUDIO server runs...")
        self.sock.bind(self.Addr)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("remote AUDIO client successfully connected...")
        data = "".encode("UTF-8")
        payload_size = struct.calcsize("L")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer=CHUNK
                                  )
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += conn.recv(81920)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frames = pickle.loads(frame_data)
            for frame in frames:
                self.stream.write(frame, CHUNK)


class AudioClient(threading.Thread):
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.daemon = True
        self.Addr = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        elif version == 6:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.p = PyAudio()
        self.stream = None

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def run(self):
        print("AUDIO client runs...")
        while True:
            try:
                print("try to connect..")
                self.sock.connect(self.Addr)
                break
            except:
                print("connect fails...")
                time.sleep(3)
                continue
        print("AUDIO client connected...")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK
                                  )
        while self.stream.is_active():
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            senddata = pickle.dumps(frames)
            try:
                self.sock.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break


if __name__ == "__main__":
    aserver = AudioServer(5000, 4)
    aclient = AudioClient('127.0.0.1', 5000, 4)
    aclient.start()
    time.sleep(1)
    aserver.start()
    while True:
        pass
