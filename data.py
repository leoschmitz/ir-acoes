from dataclasses import dataclass
from datetime import datetime

@dataclass
class Operation:
    stock: str
    quantity: int
    price: float
    date: datetime.date


class Buy(Operation):
    """Buy op"""


class Sell(Operation):
    """Buy op"""
