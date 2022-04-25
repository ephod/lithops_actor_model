import logging
import math
import time
from typing import Callable, Optional, TypeVar

from director import Director

T = TypeVar("T")

logger = logging.getLogger(__name__)


class Pinger(object):
    director: Optional[Callable[[str, object], None]]
    pings_left: Optional[int]
    judge: Optional[str]
    ponger: Optional[str]

    def set_up(self, pings: int, judge: str, ponger: str) -> None:
        self.pings_left = pings
        self.judge = judge
        self.ponger = ponger

        # self.judge.ping_ready()
        self.director(self.judge, ("ping_ready", (), {}))
        print("Ping Ready")

    def pong(self) -> None:
        if self.pings_left > 0:
            # self.ponger.ping()
            self.director(self.ponger, ("ping", (), {}))
            # print("Ping 🏓")
            self.pings_left -= 1
        else:
            # self.judge.finish()
            self.director(self.judge, ("finish", (), {}))
            print("Finished playing ping pong 🏁")


class Ponger(object):
    director: Optional[Callable[[str, object], None]]
    pinger: Optional[str]

    def set_up(self, judge: str, pinger: str) -> None:
        self.pinger = pinger
        # judge.pong_ready()
        self.director(judge, ("pong_ready", (), {}))
        print("Pong Ready")

    def ping(self) -> None:
        # self.pinger.pong()
        self.director(self.pinger, ("pong", (), {}))
        # print("Pong 🏓")


class Judge(object):
    # https://stackoverflow.com/questions/34230618/python-3-5-type-hinting-dynamically-generated-instance-attributes
    director: Optional[Callable[[str, object], None]]
    pings: Optional[int]
    pinger: Optional[str]
    ponger: Optional[str]
    ping_ok: Optional[bool]
    pong_ok: Optional[bool]
    init: Optional[float]
    end: Optional[float]

    def set_up(self, num_pings: int, pinger: str, ponger: str) -> None:
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
        print("Judge Ready 👨‍")

    def ping_ready(self) -> None:
        self.ping_ok = True
        self.run()

    def pong_ready(self) -> None:
        self.pong_ok = True
        self.run()

    def run(self) -> None:
        if self.ping_ok and self.pong_ok:
            self.init = time.time()
            # self.pinger.pong()
            self.director(self.pinger, ("pong", (), {}))
            print("First sent")

    def finish(self) -> None:
        self.end = time.time()
        total = self.end - self.init
        print(f"Did {self.pings} pings in {total} s")
        print(f"{self.pings / total} pings per second")
        self.director("director", ("finish", (), {}))


def main() -> None:
    AWS_LAMBDA_TIMEOUT_SECONDS = 300
    start = time.monotonic()
    director = Director()
    director.run()
    judge_ps = director.new_actor(Judge, "judge")
    ping_ps = director.new_actor(Pinger, "ping")
    pong_ps = director.new_actor(Ponger, "pong")

    director.msg_to("judge", ("set_up", (1_000, "ping", "pong"), {}))

    while director.waiting:
        current_time = time.monotonic()
        if math.ceil(current_time - start) > AWS_LAMBDA_TIMEOUT_SECONDS:
            break

    director.msg_to("judge", "pls stop")
    director.msg_to("ping", "pls stop")
    director.msg_to("pong", "pls stop")

    judge_ps.get_result()
    # judge_ps.plot(dst="./lithops_plots/judge")
    ping_ps.get_result()
    # ping_ps.plot(dst="./lithops_plots/ping")
    pong_ps.get_result()
    # pong_ps.plot(dst="./lithops_plots/pong")

    judge_ps.clean()
    ping_ps.clean()
    pong_ps.clean()
    director.stop()


if __name__ == "__main__":
    main()
