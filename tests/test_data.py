from calendar import isleap
from calendar import mdays
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from taxes import data


def _now(delta_month=0):
    now_ = datetime.now().date()
    if not delta_month:
        return now_

    month = (now_.month + delta_month) % 12
    days = mdays[month] + (month == 2 and isleap(now_.year))
    return now_ + timedelta(days=days)


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

    def test_empty_total(self):
        self.assertEqual(self.bucket.total, 0.0)

    def test_total(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.23, date=_now()))
        self.assertEqual(self.bucket.total, 223.0)

    def test_empty_quantity(self):
        self.assertFalse(self.bucket.quantity)

    def test_quantity(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.bucket.add(data.Buy(stock='STOC4', quantity=300, price=1.0, date=_now()))
        self.assertEqual(self.bucket.quantity, 400)

    def test_empty_length(self):
        self.assertFalse(len(self.bucket))

    def test_lenght(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.bucket.add(data.Buy(stock='STOC4', quantity=300, price=1.0, date=_now()))
        self.assertEqual(len(self.bucket), 2)

    def test_add_different_op_types(self):
        self.bucket.add(data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now()))
        with self.assertRaises(AssertionError):
            self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))


class TestMonthOperations(TestCase):
    def setUp(self):
        self.month = data.MonthOperations(month=1)

    def test_adding_ops(self):
        self.month.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.month.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.month.add(data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now()))
        self.assertEqual(len(self.month.buy), 2)
        self.assertEqual(len(self.month.sell), 1)

    def test_adding_invalid_operation(self):
        with self.assertRaises(TypeError):
            self.month.add(
                data.Operation(stock='STOC4', quantity=100, price=1.0, date=_now())
            )


class TestYearOpsSingleStock(TestCase):
    # issue #1 will fix this
    def test_same_month_buy_sell(self):
        with self.assertRaises(AssertionError):
            data.YearOperations('STOC4', 2023, {}, [
                data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()),
                data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now())
            ])

    # issue #2 will fix this
    def test_sell_more_than_20k_in_a_month(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=1, price=20000.0, date=_now()),
            data.Sell(stock='STOC4', quantity=1, price=20000.01, date=_now(delta_month=1))
        ])
        with self.assertRaises(AssertionError):
            year.calculate_loss_or_profit()

    def test_calculate_loss_only_buy_ops(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now(delta_month=1))
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, 0.0)
        self.assertFalse(year.months[_now().month].has_loss)

    def test_calculate_loss_with_profit(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()),
            data.Sell(stock='STOC4', quantity=100, price=2.0, date=_now(delta_month=1))
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, 0.0)
        self.assertFalse(year.months[_now().month].has_loss)

    def test_calculate_loss_successfully(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=100, price=2.0, date=_now()),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=_now(delta_month=1))
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, -100.0)
        self.assertTrue(year.months[_now().month].has_loss)

    def test_calculate_profit_only_buy_ops(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now(delta_month=1))
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.tax_free_profit, 0.0)

    def test_calculate_profit_successfully(self):
        year = data.YearOperations('STOC4', 2023, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=_now()),
            data.Sell(stock='STOC4', quantity=100, price=2.0, date=_now(delta_month=1))
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.tax_free_profit, 100.0)
