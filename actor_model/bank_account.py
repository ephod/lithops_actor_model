import logging
import math
import time
from typing import Callable, Optional, TypeVar

from director import Director

T = TypeVar("T")

logger = logging.getLogger(__name__)


class BankAccount:
    account_number: int
    balance: int
    director: Optional[Callable[[str, object], None]]

    def set_up(
        self, account_number: Optional[int], balance: Optional[int] = 100
    ):
        self.account_number = account_number
        self.balance = balance
        print(f"Set up balance: {self.balance}")

    def save(self) -> None:
        self.balance += 10

    def spend(self) -> None:
        self.balance -= 10

    def transfer(self, amount: int, to_account: str) -> bool:
        if not (self.balance >= amount):
            logger.info("Balance is running low")
            print("⚠️️  Balance is running low")
            return False
        self.balance -= amount
        print(f"💸 transfer {amount}. Balance: {self.balance}")
        self.director(to_account, ("deposit", (amount,), {}))

        return True

    def deposit(self, amount: int) -> None:
        self.balance += amount
        print(f"💰 deposit {amount}. Balance: {self.balance}")

    def get_balance(self):
        print(f"Balance {self.balance}; Account number: {self.account_number}")
        return self.balance


class Bank:
    director: Optional[Callable[[str, object], None]]

    def transfer(self, amount: int, from_account: str, to_account: str) -> None:
        print(f"🏦 transfer money from {from_account} to {to_account}")
        self.director(from_account, ("transfer", (amount, to_account), {}))


class Pinger:
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


class Ponger:
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


class Judge:
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
    bank_ps = director.new_actor(Bank, "bank")
    bank_account_1_ps = director.new_actor(BankAccount, "bank_account_1")
    bank_account_2_ps = director.new_actor(BankAccount, "bank_account_2")

    director.msg_to("bank_account_1", ("set_up", (1, 100), {}))
    director.msg_to("bank_account_2", ("set_up", (2, 100), {}))

    i = 0
    while director.waiting:
        # time.sleep(1)
        # print("Waiting a second ⌚")

        send_args = (10, "bank_account_1", "bank_account_2")
        if (i % 2) == 0:
            send_args = (10, "bank_account_2", "bank_account_1")
            print("🎲 Even")
        else:
            print("🎲 Odd")
        director.msg_to("bank", ("transfer", send_args, {}))
        print(f"Iteration {i}")
        if i >= AWS_LAMBDA_TIMEOUT_SECONDS:
            break
        i += 1
        # director.msg_to('bank_account_1', ('save', (), {}))
        # director.msg_to('bank_account_1', ('spend', (), {}))
        # director.msg_to('bank_account_2', ('save', (), {}))
        # director.msg_to('bank_account_2', ('spend', (), {}))

        current_time = time.monotonic()
        if math.ceil(current_time - start) > AWS_LAMBDA_TIMEOUT_SECONDS:
            break

    director.msg_to("bank_account_1", ("get_balance", (), {}))
    director.msg_to("bank_account_2", ("get_balance", (), {}))

    director.msg_to("bank", "pls stop")
    director.msg_to("bank_account_1", "pls stop")
    director.msg_to("bank_account_2", "pls stop")

    bank_ps.get_result()
    # bank_ps.plot(dst='./lithops_plots/bank')
    bank_account_1_ps.get_result()
    # bank_account_1_ps.plot(dst='./lithops_plots/bank_account_1')
    bank_account_2_ps.get_result()
    # bank_account_2_ps.plot(dst='./lithops_plots/bank_account_2')

    bank_ps.clean()
    bank_account_1_ps.clean()
    bank_account_2_ps.clean()
    director.stop()


if __name__ == "__main__":
    main()
