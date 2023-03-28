from datetime import datetime
from unittest import TestCase

from taxes import data


def _now():
    return datetime.now().date()


class TestOperation(TestCase):
    def test_total(self):
        op = data.Operation(stock='STOC4', quantity=100, price=1.234567, date=_now())
        self.assertEqual(op.total, 123.4567)

    def test_buy_inheritance(self):
        op = data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now())
        self.assertEqual(op.total, 100)

    def test_sell_type(self):
        op = data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now())
        self.assertTrue(isinstance(op, data.Sell))
        self.assertFalse(isinstance(op, data.Buy))


class TestMonthlyBucket(TestCase):
    def setUp(self):
        self.bucket = data.MonthlyBucket()

    def test_total(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.23, date=_now()))
        self.assertEqual(self.bucket.total, 223.0)

    def test_quantity(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.assertEqual(self.bucket.quantity, 200)

    def test_add_different_op_types(self):
        self.bucket.add(data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now()))
        with self.assertRaises(AssertionError):
            self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
