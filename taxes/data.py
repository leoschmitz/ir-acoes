import logging
from calendar import month_name
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Operation:
    stock: str
    quantity: int
    price: float
    date: datetime.date

    @property
    def total(self):
        return round(self.price * self.quantity, 6)


class Buy(Operation):
    """Buy op"""


class Sell(Operation):
    """Sell op"""


class MonthlyBucket:
    def __init__(self):
        self.ops = []

    def __len__(self):
        return len(self.ops)

    def add(self, op):
        if self.ops:
            assert isinstance(op, type(self.ops[0]))

        self.ops.append(op)

    @property
    def total(self):
        sum_ = 0.0
        for op in self.ops:
            sum_ += op.total
        return sum_

    @property
    def quantity(self):
        sum_ = 0
        for op in self.ops:
            sum_ += op.quantity
        return sum_


class MonthOperations:
    def __init__(self, month: int):
        self.month = month
        self.loss = 0.0
        self.profit = 0.0
        self.buy = MonthlyBucket()
        self.sell = MonthlyBucket()

    @property
    def has_loss(self):
        return self.loss + self.profit < 0.0

    def add(self, op):
        if isinstance(op, Buy):
            self.buy.add(op)
        elif isinstance(op, Sell):
            self.sell.add(op)
        else:
            raise TypeError('Only buy or sell allowed')


class YearOperations:
    def __init__(self, stock, year, previous_year, operations):
        self.stock = stock
        self.year = year
        self.accum_loss = 0.0
        self.tax_free_profit = 0.0
        self.operation_results = [0.0] * 12
        self.months = [MonthOperations(month=i) for i in range(1, 13)]

        self.previous_total = 0.0
        self.previous_quantity = 0
        if previous_year:
            self.previous_total = previous_year['total']
            self.previous_quantity = previous_year['quantidade']

        for operation in operations:
            index_month = operation.date.month - 1
            self.months[index_month].add(operation)

        # validate there is buy/sell at the same month
        # this is a TODO for this script (issue #1)
        for month in self.months:
            assert not (month.buy.quantity and month.sell.quantity)

    def calculate_loss_or_profit(self):
        for month_number, month in enumerate(self.months):
            if not month.sell.quantity:
                continue
            # this will start with zero, which is the correct first month (previous)
            buy_price = (
                self.accumulated_average(month=month_number) * month.sell.quantity
            )

            result = month.sell.total - buy_price
            assert month.sell.total < 20000.00  # TODO issue #2
            logger.info(
                'On %s sell quantity %s remains %s, buy price %s sold total %s diff %s',
                month_name[month_number + 1],
                month.sell.quantity,
                self.accumulated_quantity(month=month_number + 1),
                round(buy_price, 5),
                round(month.sell.total, 5),
                round(result, 5),
            )
            if result < 0.0:
                month.loss = result
                self.accum_loss += result
            else:
                month.profit = result
                self.tax_free_profit += result

            self.operation_results[month_number] = result

        logger.info(
            'Tax free profit: %s, loss: %s', self.tax_free_profit, self.accum_loss
        )

    def accumulated_total(self, operation_type, month=12):
        sum_ = self.previous_total if operation_type == 'BUY' else 0.0
        for month in self.months[:month]:
            sum_ += month.buy.total if operation_type == 'BUY' else month.sell.total
        return sum_

    def accumulated_quantity(self, operation_type='', month=12):
        sum_ = self.previous_quantity if operation_type in ('BUY', '') else 0
        for month in self.months[:month]:
            if operation_type == 'BUY':
                sum_ += month.buy.quantity
            elif operation_type == 'SELL':
                sum_ += month.sell.quantity

            if not operation_type:
                sum_ += month.buy.quantity - month.sell.quantity
        return sum_

    def accumulated_average(self, operation_type='', month=12):
        average = 0.0
        if operation_type in ('BUY', 'SELL'):
            quantity = self.accumulated_quantity(
                operation_type=operation_type, month=month
            )
            if not quantity:
                return average

            return self.accumulated_total(operation_type, month=month) / quantity

        result = 0.0
        accum_total = self.previous_total
        accum_quantity = self.previous_quantity
        for month in self.months[:month]:
            # issue #1 needs to account for buy & sell in the same month
            if month.buy.quantity:
                accum_total += month.buy.total
                accum_quantity += month.buy.quantity

            # issue #1 as well
            if month.sell.quantity:
                average = accum_total / accum_quantity
                accum_quantity -= month.sell.quantity
                accum_total = accum_quantity * average

            if not accum_quantity:
                accum_total = 0.0
                result = 0.0

        if not accum_quantity:
            return result

        return accum_total / accum_quantity
