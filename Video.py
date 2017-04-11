import pickle
import struct
import threading
import time
import zlib
from socket import *

import cv2


class VideoServer(threading.Thread):
    def __init__(self, port, version):
        threading.Thread.__init__(self)
        self.daemon = True
        self.Addr = ('', port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        elif version == 6:
            self.sock = socket(AF_INET6, SOCK_STREAM)

    def __del__(self):
        self.sock.close()
        try:
            cv2.destroyAllWindows()
        except:
            pass

    def run(self):
        print("VIDEO server runs...")
        self.sock.bind(self.Addr)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("remote client successfully connected...")
        data = "".encode("UTF-8")
        payload_size = struct.calcsize("L")  # 计算Long的长度
        cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)
        while True:
            while len(data) < payload_size:
                # 当数据区不足数据包长度时读入
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            # 取出数据包大小
            data = data[payload_size:]
            # 去头
            msg_size = struct.unpack("L", packed_size)[0]
            # 解出数据包大小的真值
            while len(data) < msg_size:
                # 当数据区不足该数据包完整大小再拉取一部分
                data += conn.recv(81920)
            zframe_data = data[:msg_size]
            # 一帧数据（pickle打包后）
            data = data[msg_size:]
            frame_data = zlib.decompress(zframe_data)
            # 解压缩
            frame = pickle.loads(frame_data)
            cv2.imshow('Remote', frame)
            print("playing...")
            if cv2.waitKey(1) & 0xFF == 27:
                # 键盘退出
                break


class VideoClient(threading.Thread):
    def __init__(self, ip, port, version, level):
        threading.Thread.__init__(self)
        self.daemon = True
        self.Addr = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        elif version == 6:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)
        # 调用OpenCV捕获默认摄像头
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:
            self.fx = 0.3

    def __del__(self):
        self.sock.close()
        self.cap.release()

    def run(self):
        print("VIDEO client runs...")
        while True:
            try:
                print("try to connect..")
                self.sock.connect(self.Addr)
                break
            except:
                print("connect fails...")
                time.sleep(3)
                continue
        print("VIDEO client connected...")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            sframe = cv2.resize(frame, (0, 0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe)
            # 数据帧打包
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            # 压缩数据
            try:
                self.sock.sendall(struct.pack("L", len(zdata)) + zdata)
                # struct 将数据包长度作为Long类型装入
                print("VIDEO stream sended...")
            except:
                print("cap is closed!")
                break
            for i in range(self.interval):
                self.cap.read()
