import threading
import Serial
import Detect

mutex = threading.Lock()

class DetectThread(threading.Thread):
    def run(self):
        Detect.detectmine()

class SerialThread(threading.Thread):
    def run(self):
        Serial.serial()

if __name__ == "__main__":
    dt = DetectThread()
    sr = SerialThread()
    dt.start()
    sr.start()
    dt.join()
    sr.join()
