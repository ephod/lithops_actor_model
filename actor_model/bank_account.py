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

        current_time = time.monotonic()
        if math.ceil(current_time - start) > AWS_LAMBDA_TIMEOUT_SECONDS:
            break

    director.msg_to("bank_account_1", ("get_balance", (), {}))
    director.msg_to("bank_account_2", ("get_balance", (), {}))

    director.msg_to("bank", "pls stop")
    director.msg_to("bank_account_1", "pls stop")
    director.msg_to("bank_account_2", "pls stop")

    bank_ps.get_result()
    bank_account_1_ps.get_result()
    bank_account_2_ps.get_result()

    bank_ps.clean()
    bank_account_1_ps.clean()
    bank_account_2_ps.clean()
    director.stop()


if __name__ == "__main__":
    main()
