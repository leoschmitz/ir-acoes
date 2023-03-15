import logging
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import ClassVar
from typing import List

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
    """Buy op"""


@dataclass
class MonthlyBucket:
    ops: List[Operation] = field(default_factory=list)

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


@dataclass
class Monthly:
    month: int
    buy: MonthlyBucket = field(default_factory=MonthlyBucket)
    sell: MonthlyBucket = field(default_factory=MonthlyBucket)


class YearOperations:
    def __init__(self, previous_year, operations):
        self.stock = operations[0].stock
        self.months = [Monthly(i) for i in range(1, 13)]

        self.previous_total = 0.0
        self.previous_quantity = 0.0
        if previous_year:
            self.previous_total = previous_year['total']
            self.previous_quantity = previous_year['quantidade']

        for operation in operations:
            index_month = operation.date.month - 1
            if isinstance(operation, Buy):
                self.months[index_month].buy.ops.append(operation)
                continue
            self.months[index_month].sell.ops.append(operation)

    def accumulated_total(self, operation_type, month=12):
        sum_ = self.previous_total
        for month in self.months[:month]:
            sum_ += month.buy.total if operation_type == 'BUY' else month.sell.total
        return sum_

    def accumulated_quantity(self, operation_type, month=12):
        sum_ = self.previous_quantity
        for month in self.months[:month]:
            sum_ += month.buy.quantity if operation_type == 'BUY' else month.sell.quantity
        return sum_

    def accumulated_average(self, operation_type, month=12):
        quantity = self.accumulated_quantity(operation_type, month=month)
        if not quantity:
            return 0.0

        return self.accumulated_total(operation_type, month) / quantity
