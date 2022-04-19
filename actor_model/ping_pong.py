import logging
import time
from typing import Callable, Optional

from director import Director

logging_level = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(logging_level)

# Set up a stream handler to log to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging_level)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(stream_handler)


class Pinger(object):
    director: Optional[Callable[[str, object], None]]

    def __init__(self):
        self.ponger = None
        self.judge = None
        self.pings_left = None
        logger.info("Pinger constructor")

    def set_up(self, pings, judge, ponger):
        self.pings_left = pings
        self.judge = judge
        self.ponger = ponger

        # self.judge.ping_ready()
        self.director(self.judge, ("ping_ready", (), {}))
        print("Ping Ready")
        logger.info("Ping Ready")

    def pong(self):
        if self.pings_left > 0:
            # self.ponger.ping()
            self.director(self.ponger, ("ping", (), {}))
            self.pings_left -= 1
        else:
            # self.judge.finish()
            self.director(self.judge, ("finish", (), {}))


class Ponger(object):
    director: Optional[Callable[[str, object], None]]

    def set_up(self, judge, pinger):
        self.pinger = pinger
        # judge.pong_ready()
        self.director(judge, ("pong_ready", (), {}))
        print("Pong Ready")
        logger.info("Pong Ready")

    def ping(self):
        # self.pinger.pong()
        self.director(self.pinger, ("pong", (), {}))


class Judge(object):
    director: Optional[Callable[[str, object], None]]

    def set_up(self, num_pings, pinger, ponger):
        self.pings = num_pings
        self.pinger = pinger
        self.ponger = ponger
        # self.pinger.set_up(self.pings,'judge', self.ponger)
        self.director(
            self.pinger, ("set_up", (self.pings, "judge", self.ponger), {})
        )
        # self.ponger.set_up('judge', self.pinger)
        self.director(self.ponger, ("set_up", ("judge", self.pinger), {}))

        self.ping_ok = False
        self.pong_ok = False
        print("Judge Ready")

    def ping_ready(self):
        self.ping_ok = True
        self.run()

    def pong_ready(self):
        self.pong_ok = True
        self.run()

    def run(self):
        if self.ping_ok and self.pong_ok:
            self.init = time.time()
            # self.pinger.pong()
            self.director(self.pinger, ("pong", (), {}))
            print("First sent")
            logger.info("First sent")

    def finish(self):
        self.end = time.time()
        total = self.end - self.init
        print(f"Did {self.pings} pings in {total} s")
        logger.info(f"Did {self.pings} pings in {total} s")
        print(f"{self.pings / total} pings per second")
        logger.info(f"{self.pings / total} pings per second")


def main():
    director = Director()
    director.run()
    judge_ps = director.new_actor(Judge, "judge")
    ping_ps = director.new_actor(Pinger, "ping")
    pong_ps = director.new_actor(Ponger, "pong")

    director.msg_to("judge", ("set_up", (10, "ping", "pong"), {}))

    time.sleep(5)
    director.msg_to("judge", "pls stop")
    director.msg_to("ping", "pls stop")
    director.msg_to("pong", "pls stop")

    # judge_ps.join()
    # ping_ps.join()
    # pong_ps.join()

    judge_ps.get_result()
    ping_ps.get_result()
    pong_ps.get_result()

    director.stop()


if __name__ == "__main__":
    main()
