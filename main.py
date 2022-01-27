import threading
import SerialThread
import DetectThread

if __name__ == "__main__":
    dt = threading.Thread(target=DetectThread.Detect,args=())
    sr = threading.Thread(target=SerialThread.Serial,args=())
    dt.start()
    sr.start()
    dt.join()
    sr.join()
