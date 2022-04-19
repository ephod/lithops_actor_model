# The code related to the actor model implementation within Lithops was based on this source code:
#   https://github.com/danielBCN/lithops-actors
# The author is Daniel Barcelona: https://github.com/danielBCN

from queue import Empty
from threading import Thread
from typing import Any, Dict, Optional, TypeVar

import lithops.multiprocessing as mp
from lithops import FunctionExecutor

T = TypeVar("T")


def actor_process(
    actor_type: T, queue: mp.Queue, director_queue: mp.Queue
) -> None:
    """Send and retrieve messages for actors."""

    def send_to_director(name: str, msg: object) -> None:
        director_queue.put([name, *msg])

    instance = actor_type()
    instance.director = send_to_director
    while True:
        message = queue.get()
        # print(message)
        if message == "pls stop":
            break
        method_name, args, kwargs = message
        getattr(instance, method_name)(*args, **kwargs)


class Director:
    """Main actor."""

    container: Optional[Any]
    running: Optional[bool]
    thread: Optional[Thread]

    def __init__(self):
        self.actors: Dict[str, mp.Queue] = {}
        self.queue = mp.Queue()
        self.counter = 0
        self.waiting = True
        self.container = None

    def new_actor(self, actor_type: T, name: str) -> FunctionExecutor:
        actor_queue = mp.Queue()
        self.actors[name] = actor_queue
        fexec = FunctionExecutor()
        fexec.call_async(actor_process, (actor_type, actor_queue, self.queue))
        return fexec

    def run(self) -> None:
        def p() -> None:
            while self.running:
                try:
                    m = self.queue.get(timeout=1)
                    dest: str = m[0]
                    msg: object = m[1:]
                    if dest == "director":
                        msg_func, msg_args, msg_kwargs = msg
                        if msg_func == "container":
                            self.container = msg_args
                        else:
                            self.waiting = False
                    else:
                        self.actors[dest].put(msg)
                    self.counter += 1
                    # print(f"Queue message {self.counter}. 📮 {dest}. ✉ {msg}")
                    print(f"Queue message {self.counter}. 📮 {dest}.")
                except Empty:
                    pass

        self.running = True
        self.thread = Thread(target=p)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        self.thread.join()

    def msg_to(self, name: str, msg: object) -> None:
        self.actors[name].put(msg)

    def retrieve_actors(self):
        self.actors.keys()
