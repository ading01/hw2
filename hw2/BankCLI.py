import sys
import pickle

from datetime import datetime
from Bank import Bank
from Transactions import Transaction
from Accounts import OverdrawError
from Accounts import TransactionLimitError, TransactionSequenceError
from decimal import Decimal, DecimalException
import logging

logging.basicConfig(filename='bank.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# -----------------BEFORE SUBMITTING-------------------------
# write error handling if a type of account is not checking or saving
# what if you try to open an account with a negative
# what happens when you don't enter a valid account number?
# what happens if you try to select an account and there are no accounts?
# trying to apply fees without an account selected
#when you do not select an account number after entering 3

class BankCLI():
    def __init__(self):
        self._bank = Bank()
        self._selected_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._list_transactions,
            "5": self._add_transaction,
            "6": self._monthy_triggers,
            "7": self._save,
            "8": self._load,
            "9": self._quit,
        }


    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: list transactions
5: add transaction
6: interest and fees
7: save
8: load
9: quit""")

    def run(self):        
        """Display the menu and respond to choices."""

        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))


    def _summary(self):
        for x in self._bank.show_accounts():
            print(x)

    def _load(self):
        with open("save.pickle", "rb") as f:
            self._bank = pickle.load(f)
        logging.debug("Loaded from bank.pickle")
        

    def _save(self):
        with open("save.pickle", "wb") as f:
            pickle.dump(self._bank, f)
        logging.debug("Saved to bank.pickle")

    def _quit(self):
        sys.exit(0)

    def _add_transaction(self):    
        if self._selected_account == None:
            print("This command requires that you first select an account.")
            return

        while True:
            try:
                amount = Decimal(input("Amount?\n>"))
                break
            except (ValueError, DecimalException):
                print("Please try again with a valid dollar amount.")
            
        while True:
            try:
                # date = datetime.strptime(input("Date? (YYYY-MM-DD)\n>"), "%Y-%m-%d")
                date = input("Date? (YYYY-MM-DD)\n>")
                datetime.strptime(date, "%Y-%m-%d")
                break
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")

        t = Transaction(amount, date)
        print("hello?")
        try:
            self._selected_account.add_transaction(t)
            print("2")
        except AttributeError:
            print("This command requires that you first select an account.")
        except OverdrawError:
            print("This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError:
            print("This transaction could not be completed because the account has reached a transaction limit.")
        except TransactionSequenceError as e:
            print("New transactions must be from {0} onward.".format(e))
        logging.debug(f"Created transaction: {self._selected_account.get_acct_num()}, {t.get_amount()}")


    def _open_account(self):
        while True:
            acct_type = input("Type of account? (checking/savings)\n>")
            if acct_type == "checking" or acct_type == "savings":
                break
            else:
                print("Please try again and enter either 'checking' or 'savings'")

        while True:
            try:
                initial_deposit = Decimal(input("Initial deposit amount?\n>"))
                break
            except (ValueError, DecimalException):
                print("Please try again with a valid dollar amount.")

        

        t = Transaction(initial_deposit)

        try: 
            a = self._bank.add_account(acct_type)
            a.add_transaction(t)
        except OverdrawError:
            print("Cannot open an account with negative value")
        logging.debug(f"Created account: {a.get_acct_num()}")
        
    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthy_triggers(self):
        try:
            self._selected_account.assess_interest_and_fees()
        except TransactionSequenceError as e:
            month = datetime.strftime(e.latest_date, "%B")
            print(f"Cannot apply interest and fees again in the month of {month}.")
        except AttributeError:
            print("This command requires that you first select an account.")
        logging.debug("Triggered fees and interest")
            

    def _list_transactions(self):
        try: 
            for x in self._selected_account.get_transactions():
                print(x)
        except AttributeError:
            print("This command requires that you first select an account.")
            




if __name__ == "__main__":
    BankCLI().run()
    # try:
    #     BankCLI().run()
    # except Exception:
    #     print("Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.")
