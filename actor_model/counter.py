import logging
import random
import string
from typing import Callable, Optional, TypeVar

from director import Director

T = TypeVar("T")
logger = logging.getLogger(__name__)


class Counter:
    director: Optional[Callable[[str, object], None]]

    def __init__(self):
        self.value = 0
        self.message = ""

    def increment(self) -> int:
        self.value += 1
        print(self.value)
        return self.value

    def get_value(self) -> int:
        print(self.value)
        return self.value

    def receive_message(self, message: str) -> None:
        self.message = message

    def retrieve_message(self) -> str:
        return self.message

    def __getstate__(self):
        """Pickle."""
        return self.value, self.message, self._thread

    def __setstate__(self, state):
        """Unpickle."""
        (self.value, self.message, self._thread) = state


def main():
    director = Director()
    director.run()
    count_ps = director.new_actor(Counter, "count")

    N = 4_096
    current_msg = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(N)
    )
    for i in range(100):
        director.msg_to("count", ("receive_message", (current_msg,), {}))
        director.msg_to("count", ("retrieve_message", (), {}))

    director.msg_to("count", ("increment", (), {}))
    director.msg_to("count", ("get_value", (), {}))
    director.msg_to("count", "pls stop")
    count_ps.get_result()
    director.stop()


if __name__ == "__main__":
    main()
