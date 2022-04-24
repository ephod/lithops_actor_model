import logging
import math
import random
import time
from typing import Callable, Optional, TypeVar
from uuid import uuid4

from director import Director

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CheckingAccount:
    """A.k.a. checking-acc."""

    director: Optional[Callable[[str, object], None]]
    balance: int
    savings_account: str
    customer: str
    uuid: str = str(uuid4())

    def set_up(self, balance: int, my_savings: str, customer: str) -> None:
        self.balance = balance
        self.savings_account = my_savings
        self.customer = customer

    def deposit(self, amount: int) -> None:
        """Deposit request."""
        self.balance += amount
        print(
            f"Receipt for depositing {amount} into checking account {self.uuid}"
        )

    def show_balance(self) -> int:
        """Show balance request."""
        print(
            f"Current balance {self.balance} within checking account {self.uuid}"
        )
        return self.balance

    def withdrawal(self, amount: int) -> None:
        """Withdrawal request."""
        if self.balance >= amount:
            self.balance -= amount
            print(
                f"Withdrawal {amount}, your new balance is {self.balance} within checking account {self.uuid}"
            )
        else:
            print(
                f"Not enough funds within checking account {self.uuid}. "
                f"Amount {amount} is greater than {self.balance} balance. "
                f"Trying to withdraw from savings account"
            )
            self.director(self.savings_account, ("withdrawal", (amount,), {}))


class SavingsAccount:
    """A.k.a. savings-acc."""

    director: Optional[Callable[[str, object], None]]
    balance: int
    checking_account: str
    customer: str
    uuid: str = str(uuid4())

    def set_up(self, balance: int, my_checking: str, customer: str) -> None:
        self.balance = balance
        self.checking_account = my_checking
        self.customer = customer

    def deposit(self, amount: int) -> None:
        """Deposit request."""
        self.balance += amount
        print(
            f"Receipt for depositing {amount} into savings account {self.uuid}"
        )

    def show_balance(self) -> int:
        """Show balance request."""
        print(
            f"Current balance {self.balance} within savings account {self.uuid}"
        )
        return self.balance

    def withdrawal(self, amount: int) -> None:
        """Withdrawal request."""
        if self.balance >= amount:
            self.balance -= amount
            print(
                f"Withdrawal {amount}, your new balance is {self.balance} within savings account {self.uuid}"
            )

            self.director(self.checking_account, ("deposit", (amount,), {}))
            print(f"Deposit {amount} to {self.checking_account}")

            # Now that the checking account has the enough amount of cash, it can withdraw the necessary amount of money
            self.director(self.checking_account, ("withdrawal", (amount,), {}))
            print(f"Request {self.checking_account} to withdraw {amount}")
        else:
            print(
                f"Not enough funds within savings account {self.uuid}. "
                f"Amount {amount} is greater than {self.balance} balance"
            )

    def _send_transaction_to_customer(self, transaction: str):
        self.director(self.customer, ("get_transaction", (transaction,), {}))


class Customer:
    director: Optional[Callable[[str, object], None]]
    checking_account: str
    savings_account: str

    def set_up(self, checking_account: str, savings_account: str) -> None:
        self.checking_account = checking_account
        self.savings_account = savings_account

    def withdrawal(self, amount: int) -> None:
        print(
            f"Customer withdraws {amount} from {self.checking_account} checking account"
        )
        self.director(self.checking_account, ("withdrawal", (amount,), {}))

    def deposit(self, amount: int) -> None:
        print(
            f"Customer deposits {amount} from {self.checking_account} checking account"
        )
        self.director(self.checking_account, ("deposit", (amount,), {}))


class Bank:
    director: Optional[Callable[[str, object], None]]

    def transfer(
        self, amount: int, from_customer: str, to_customer: str
    ) -> None:
        print(f"🏦 transfer money from {from_customer} to {to_customer}")
        self.director(from_customer, ("withdrawal", (amount,), {}))
        self.director(to_customer, ("deposit", (amount,), {}))


def main() -> None:
    AWS_LAMBDA_TIMEOUT_SECONDS = 300
    start = time.monotonic()
    director = Director()
    director.run()

    bank_1_name = "bank_1"
    bank_1_ps = director.new_actor(Bank, bank_1_name)

    cx_1_name = "customer_1"
    cx_1_ps = director.new_actor(Customer, cx_1_name)
    cx_1_checking_acct_1_name = "customer_1_checking_account_1"
    cx_1_checking_acct_1_ps = director.new_actor(
        CheckingAccount, cx_1_checking_acct_1_name
    )
    cx_1_savings_acct_1_name = "customer_1_savings_account_1"
    cx_1_savings_acct_1_ps = director.new_actor(
        SavingsAccount, cx_1_savings_acct_1_name
    )

    director.msg_to(
        cx_1_checking_acct_1_name,
        ("set_up", (100, cx_1_savings_acct_1_name, cx_1_name), {}),
    )
    director.msg_to(
        cx_1_savings_acct_1_name,
        ("set_up", (1000, cx_1_checking_acct_1_name, cx_1_name), {}),
    )
    director.msg_to(
        cx_1_name,
        ("set_up", (cx_1_checking_acct_1_name, cx_1_savings_acct_1_name), {}),
    )

    cx_2_name = "customer_2"
    cx_2_ps = director.new_actor(Customer, cx_2_name)
    cx_2_checking_acct_1_name = "customer_2_checking_account_1"
    cx_2_checking_acct_1_ps = director.new_actor(
        CheckingAccount, cx_2_checking_acct_1_name
    )
    cx_2_savings_acct_1_name = "customer_2_savings_account_1"
    cx_2_savings_acct_1_ps = director.new_actor(
        SavingsAccount, cx_2_savings_acct_1_name
    )

    director.msg_to(
        cx_2_checking_acct_1_name,
        ("set_up", (100, cx_2_savings_acct_1_name, cx_2_name), {}),
    )
    director.msg_to(
        cx_2_savings_acct_1_name,
        ("set_up", (1000, cx_2_checking_acct_1_name, cx_2_name), {}),
    )
    director.msg_to(
        cx_2_name,
        ("set_up", (cx_2_checking_acct_1_name, cx_2_savings_acct_1_name), {}),
    )

    i = 0
    while director.waiting:
        # time.sleep(1)
        # print("Waiting a second ⌚")

        send_args = (random.randint(10, 100), cx_1_name, cx_2_name)
        if (i % 2) == 0:
            send_args = (random.randint(10, 100), cx_2_name, cx_1_name)
            print("🎲 Even")
        else:
            print("🎲 Odd")
        director.msg_to(bank_1_name, ("transfer", send_args, {}))
        print(f"Iteration {i}")
        if i >= AWS_LAMBDA_TIMEOUT_SECONDS:
            break
        i += 1

        current_time = time.monotonic()
        if math.ceil(current_time - start) > AWS_LAMBDA_TIMEOUT_SECONDS:
            break

    # Show balances
    director.msg_to(cx_2_checking_acct_1_name, ("show_balance", (), {}))
    director.msg_to(cx_2_savings_acct_1_name, ("show_balance", (), {}))

    director.msg_to(cx_1_checking_acct_1_name, ("show_balance", (), {}))
    director.msg_to(cx_1_savings_acct_1_name, ("show_balance", (), {}))

    # Stop execution petition
    director.msg_to(bank_1_name, "pls stop")

    director.msg_to(cx_2_savings_acct_1_name, "pls stop")
    director.msg_to(cx_2_checking_acct_1_name, "pls stop")
    director.msg_to(cx_2_name, "pls stop")

    director.msg_to(cx_1_savings_acct_1_name, "pls stop")
    director.msg_to(cx_1_checking_acct_1_name, "pls stop")
    director.msg_to(cx_1_name, "pls stop")

    # Retrieve results
    bank_1_ps.get_result()

    cx_2_savings_acct_1_ps.get_result()
    cx_2_checking_acct_1_ps.get_result()
    cx_2_ps.get_result()

    cx_1_savings_acct_1_ps.get_result()
    cx_1_checking_acct_1_ps.get_result()
    cx_1_ps.get_result()

    # Clean actors
    bank_1_ps.clean()

    cx_2_savings_acct_1_ps.clean()
    cx_2_checking_acct_1_ps.clean()
    cx_2_ps.clean()

    cx_1_savings_acct_1_ps.clean()
    cx_1_checking_acct_1_ps.clean()
    cx_1_ps.clean()

    director.stop()


if __name__ == "__main__":
    main()
