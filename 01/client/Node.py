import random
import threading
import time
import requests

from config import NODES, NODE_PORT, REQUEST_TIME, REQUESTS_TIMEOUT


def _send(signature, json) -> {}:
    try:
        res = requests.post(f'http://{signature}:{NODE_PORT}/endpoint', json=json, timeout=REQUESTS_TIMEOUT)
        res_json = res.json()
        if 'status' in res_json and res_json['status'] > 0:
            print('Something went wrong during message handling...', flush=True)
        else:
            if 'data' in res_json:
                return res_json['data']

    except requests.exceptions.Timeout or requests.exceptions.ConnectionError:
        print(f'Connection to \'{signature}\' refused!', flush=True)
    except:
        print(f'Connection to \'{signature}\' failed!', flush=True)

    return {}


class Node:
    __signature = None
    __id = -1  # set according to the index of signature
    __color = 'black'
    __force_repaint_flag = False

    __disabled = False
    __timeout = -1
    __is_coordinator = False
    __wait_for_coordinator = False
    __sem = threading.Semaphore(1)

    def __init__(self, signature):
        self.__signature = signature
        self.__id = NODES.index(self.__signature) + 1

    # Set new timeout
    def __set_timeout(self, value=-1):
        # Lock SEM
        self.__sem.acquire()
        # Set
        if value < 0:
            self.__timeout = random.uniform(REQUEST_TIME * 8, REQUEST_TIME * 12)
        else:
            self.__timeout = value
        # Release SEM
        self.__sem.release()

    # Send election message
    def __send_election(self) -> bool:  # returns True on successful takeover, otherwise False
        res = False
        # Send only to nodes with greater ID than the current node
        for i in range(self.__id - 1, len(NODES)):
            if self.__signature != NODES[i]:
                # Send
                req_res = _send(NODES[i], {'type': 'election'})
                # If election response says the asked nodes takes over the election...
                if 'data' in req_res and 'election_takeover' in req_res['data']:
                    res = True
                    break
        return res

    # Send answer (alive) message
    def __send_answer(self) -> bool:  # returns True if all answered nodes answered back, otherwise False
        res = True
        # Send to all nodes with lower ID except the current one
        for i in range(0, self.__id):
            if self.__signature != NODES[i]:
                req_res = _send(NODES[i], {'type': 'answer'})
                # If not echo (the answered node is not responding)...
                if ('data' not in req_res) or ('data' in req_res and 'answer_echo' not in req_res['data']):
                    res = False
        return res

    # Send coordinator (victory) message
    def __send_victory(self):
        # Send to all nodes except the current one
        for i in range(len(NODES)):
            if self.__signature != NODES[i]:
                _send(NODES[i], {'type': 'coordinator'})

    # Send paint (repaint) message
    def __send_paint(self):
        total_greens = -(-len(NODES) // 3.0) - 1
        for i in range(0, self.__id):
            if self.__signature != NODES[i]:
                if total_greens > 0:
                    _send(NODES[i], {'type': 'paint', 'color': 'green'})
                    total_greens -= 1
                else:
                    _send(NODES[i], {'type': 'paint', 'color': 'red'})
            else:
                self.__color = 'green'

    # Enable node
    def enable(self):
        self.__disabled = False
        self.__color = 'black'

    # Disable node
    def disable(self):
        self.__disabled = True
        self.__color = 'gray'

    def about(self) -> {}:
        return {'id': self.__id,
                'signature': self.__signature,
                'color': self.__color,
                'is_coordinator': self.__is_coordinator,
                'wait_for_coordinator': self.__wait_for_coordinator}

    # Any data received on endpoint goes here to process
    def receive(self, json) -> {}:
        res = {}

        # If election message
        if 'type' in json and json['type'] == 'election':
            # Create response back to asking node to let it know the current node takes over the job of election
            res = {'election_takeover': True}
            self.__set_timeout(0)  # force timeout to earlier node election

        # If coordinator (victory) message
        elif 'type' in json and json['type'] == 'coordinator':
            self.__set_timeout()  # reset timeout counter
            self.__is_coordinator = False
            self.__wait_for_coordinator = False

        # If answer (alive) message
        elif 'type' in json and json['type'] == 'answer':
            self.__set_timeout()  # reset timeout counter
            res = {'answer_echo': True}

        # If answer (alive) message
        elif 'type' in json and json['type'] == 'paint':
            self.__color = json['color']

        return res

    # The main process method that is processed in the monitor loop
    def process(self):
        # If node is disabled, ignore...
        if self.__disabled:
            time.sleep(REQUEST_TIME)
            return

        # Active waiting for timeout
        self.__set_timeout()
        while self.__timeout > 0:
            # Run timeout only if the node is not coordinator or not waiting for winning message
            if not self.__is_coordinator and not self.__wait_for_coordinator:
                self.__timeout -= REQUEST_TIME
            # If the node is coordinator...
            if self.__is_coordinator:
                print(f'Sending answer message...', flush=True)
                if not self.__send_answer() or self.__force_repaint_flag:
                    print(f'Sending paint message...', flush=True)
                    self.__send_paint()
                    self.__force_repaint_flag = False
            # If node is disabled, interrupt...
            if self.__disabled:
                return
            # Delay
            time.sleep(REQUEST_TIME)
            print(f'About: {self.about()}', flush=True)

        # Do whatever here upon timeout

        # Send election
        # ... and if election was successful takeover...
        print(f'Sending election message...', flush=True)
        if self.__send_election():
            self.__wait_for_coordinator = True

        # Otherwise, no response
        # => the current node is the new leader...
        else:
            # Send winning message
            print(f'Sending coordinator message...', flush=True)
            self.__send_victory()
            self.__is_coordinator = True
            self.__force_repaint_flag = True
