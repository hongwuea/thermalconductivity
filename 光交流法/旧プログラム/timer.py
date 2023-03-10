# import threading
#class threading.Timer(interval, function, args=None, kwargs=None)

# def hello():
#     print("hello, world")

# t = threading.Timer(5.0, hello)
# t.start()  # after 30 seconds, "hello, world" will be printed
import time
import threading



def worker():
    print(time.time()-最初)
    time.sleep(8)

def scheduler(interval, f, wait = True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target = f)
        t.start()
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)

最初=time.time()

scheduler(1, worker, False)