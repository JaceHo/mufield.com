import threading
from queue import Queue
import time


class MusicDownloader(object):
    # lock to serialize console output
    lock = threading.Lock()

    def do_work(self, item):
        time.sleep(.1)  # pretend to do some lengthy work.
        # Make sure the whole print completes or threads can mix up output in one line.
        with self.lock:
            print(threading.current_thread().name, item)

    # The worker thread pulls an item from the queue and processes it
    def worker(self):
        while True:
            item = self.q.get()
            self.do_work(item)
            self.q.task_done()

    # Create the queue and thread pool.
    q = Queue()
    for i in range(4):
        t = threading.Thread(target=worker)
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()

    # stuff work items on the queue (in this case, just a number).
    start = time.perf_counter()
    for item in range(20):
        q.put(item)

    q.join()  # block until all tasks are done

    # "Work" took .1 seconds per task.
    # 20 tasks serially would be 2 seconds.
    # With 4 threads should be about .5 seconds (contrived because non-CPU intensive "work")
    print('time:', time.perf_counter() - start)
