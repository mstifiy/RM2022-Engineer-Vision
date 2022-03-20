import threading
global run
global mutex
global GET_DIS_ON
GET_DIS_ON = False
mutex = threading.Lock()
run = 1