from logging import raiseExceptions
import logging
from unittest.mock import Base
from Transactions import Transaction
from decimal import Decimal
import calendar
import datetime

class OverdrawError(Exception):
    pass

class TransactionLimitError(Exception):
    pass

class TransactionSequenceError(Exception):
    def __init__(self, latest_date):
        self.latest_date = latest_date
        
logging.basicConfig(filename='bank.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')



class Account:
    """This is an abstract class for accounts.  Provides default functionality for adding transactions, getting balances, and assessing interest and fees.  
    Accounts should be instantiated as SavingsAccounts or CheckingAccounts
    """

    def __init__(self, acct_num):
        self._transactions = []
        self._account_number = acct_num
        self.last_exempt = None
        self.latest_date = None # should be of type date

    def get_acct_num(self):
        return self._account_number


    def add_transaction(self, t):
        """Checks a pending transaction to see if it is allowed and adds it to the account if it is.

        Args:
            t (Transaction): incoming transaction
        """

        if self.latest_date == None:
            self.latest_date = t._date
        elif t._date < self.latest_date:
            raise TransactionSequenceError(self.latest_date)

        balance_ok = self._check_balance(t)
        if balance_ok == False and not self.last_exempt:
            print("hey")
            raise OverdrawError
        limits_ok = self._check_limits(t)
        if limits_ok == False:
            raise TransactionLimitError

        if t.is_exempt() or (balance_ok and limits_ok):
            self._transactions.append(t)
            self.last_exempt = t.is_exempt()
            self.latest_date = t._date

    def _check_balance(self, t):
        """Checks whether an incoming transaction would overdraw the account

        Args:
            t (Transaction): pending transaction

        Returns:
            bool: false if account is overdrawn
        """
        return t.check_balance(self.get_balance())

    def _check_limits(self, t):
        return True

    def get_balance(self):
        """Gets the balance for an account by summing its transactions

        Returns:
            Decimal: current balance
        """
        # could have a balance variable updated when transactions are added (or removed) which is faster
        # but this is more foolproof since it's always in sync with transactions
        return sum(x for x in self._transactions)

    def _interest(self):
        """Calculates interest for an account balance and adds it as a new transaction exempt from limits.
        """        
        last_day_in_month = calendar.monthrange(self.latest_date.year, self.latest_date.month)[1]
        new_date = self.latest_date.replace(day=last_day_in_month)
        datetime.strptime(new_date, "%Y-%m-%d")
        t = Transaction(self.get_balance() * self._interest_rate, date=new_date, exempt=True)
        self.add_transaction(t)

    def _fees(self):
        pass

    def assess_interest_and_fees(self):
        "Trigger interest and fees calculation for this account"
        if self.last_exempt:
            raise TransactionSequenceError(self.latest_date)
        self._interest()
        self._fees()



    def __str__(self):
        """Formats the account number and balance of the account.
        For example, '#000000001,<tab>balance: $50.00'
        """    
        return f"#{self._account_number:09},\tbalance: ${self.get_balance():,.2f}"

    def get_transactions(self):
        return sorted(self._transactions)


class SavingsAccount(Account):
    """Concrete Account class with daily and monthly account limits and high interest rate.
    """    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.025")
        self._daily_limit = 2
        self._monthly_limit = 5

    def _check_limits(self, t1:Transaction) -> bool:
        """determines if the incoming trasaction is within the accounts transaction limits

        Args:
            t1 (Transaction): pending transaction to be checked

        Returns:
            bool: true if within limits and false if beyond limits
        """    
        num_today = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_day(t1)])
        num_this_month = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_month(t1)])
        return num_today < self._daily_limit and num_this_month < self._monthly_limit

    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Savings#000000001,<tab>balance: $50.00'
        """ 
        return "Savings" + super().__str__()


class CheckingAccount(Account):
    """Concrete Account class with lower interest rate and low balance fees.
    """  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0015")
        self._balance_threshold = 100
        self._low_balance_fee = -10

    def _fees(self):
        """Adds a low balance fee if balance is below a particular threshold. Fee amount and balance threshold are defined on the CheckingAccount.
        """
        last_day_in_month = calendar.monthrange(self.latest_date.year, self.latest_date.month)[1]
        new_date = self.latest_date.replace(day=last_day_in_month)

        if self.get_balance() < self._balance_threshold:
            t = Transaction(self._low_balance_fee, date=str(new_date), exempt=True)
            self.add_transaction(t)

    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Checking#000000001,<tab>balance: $50.00'
        """ 
        return "Checking" + super().__str__()
