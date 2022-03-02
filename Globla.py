import threading
global run
global mutex
mutex = threading.Lock()
run = 1