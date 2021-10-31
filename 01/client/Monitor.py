import socket
import threading
import time

from Node import Node


def get_backend_signature():
    return socket.gethostname()


class MonitorThread(threading.Thread):
    node = Node(get_backend_signature())

    def run(self):
        print("Starting monitor system thread...", flush=True)

        try:
            # Init delay
            time.sleep(1)

            # Monitor the system forever while powered
            while 1:
                self.node.process()

        except KeyboardInterrupt:
            pass
