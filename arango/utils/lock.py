import six
from threading import current_thread


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


    class RLock(Lock):
        """Implementation of a reentrant lock with a timeout"""

        def __init__(self):
            super(RLock, self).__init__()
            self._thread_id = None
            self._current_thread_count = 0

        def acquire(self, timeout=-1):
            if current_thread() is self._thread_id:
                self._current_thread_count += 1
                return True
            else:
                res = Lock.acquire(self, timeout)
                self._thread_id = current_thread()
                self._current_thread_count = 1
                return res

        def release(self):
            if current_thread() is self._thread_id:
                self._current_thread_count -= 1
                if self._current_thread_count == 0:
                    self._thread_id = None
                    Lock.release(self)
            else:
                raise RuntimeError("Tried to release a lock which was not "
                                   "owned by this thread.")

else:
    from threading import Lock, RLock
