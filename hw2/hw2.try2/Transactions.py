from datetime import datetime
from decimal import Decimal, setcontext, BasicContext
import logging

# context with ROUND_HALF_UP
setcontext(BasicContext)

class ComparableMixin():
    "Assumes that __lt__ is appropriately implemented and derives the remaining comparison methods from these"
    
    def __ge__(self, other) -> bool:
        return not self.__lt__(other)

    def __gt__(self, other) -> bool:
        return other.__lt__(self)

    def __le__(self, other) -> bool:
        return not self.__gt__(other)

    def __eq__(self, other) -> bool:
        return not self.__lt__(other) and not self.__gt__(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Transaction(ComparableMixin):
    def __init__(self, amt, acct_num, date=None, exempt=False):
        """
        Args:
            amt (string): String representing dollar amount of the transaction. Converted to Decimal.
            date (string, optional): Date string in the format YYYY-MM-DD. Defaults to None.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """        
        self._amt = Decimal(amt) # convert from string to Decimal to avoid rounding errors
        if date is None:
            self._date = datetime.now().date()
        else:
            self._date = datetime.strptime(date, "%Y-%m-%d").date()
        self._exempt = exempt
        #logging.debug(f"Created transaction: {self.acct_num}, {self.get_amount}")

    
    def get_amount(self):
        return self._amt

    def __str__(self):
        return f"{self._date}, ${self._amt:,.2f}"

    def is_exempt(self):
        return self._exempt

    def in_same_day(self, other):
        return self._date == other._date

    def in_same_month(self, other):
        return self._date.month == other._date.month and self._date.year == other._date.year

    def __radd__(self, other):
        # allows us to use sum() with transactions
        return other + self._amt

    def check_balance(self, balance):
        return self._amt >= 0 or balance > abs(self._amt)

    def __lt__(self, value):
        return self._date < value._date

    def change_date(self, new_date):
        self._date = new_date




