import six


if six.PY2:
    import Queue


    class Lock(object):
        """Implementation of a lock with a timeout for python 2.

        https://stackoverflow.com/questions/35149889/lock-with-timeout-in-python2-7
        """

        def __init__(self):
            self._queue = Queue.Queue(maxsize=1)
            self._queue.put(True, block=False)

        def acquire(self, timeout=-1):
            if timeout <= 0:
                timeout = None

            try:
                return self._queue.get(block=True, timeout=timeout)
            except Queue.Empty:
                return False

        def release(self):
            self._queue.put(True, block=False)

        def __enter__(self):
            self.acquire()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.release()
else:
    from threading import Lock
