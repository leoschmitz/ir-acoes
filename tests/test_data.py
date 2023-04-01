from datetime import date
from unittest import TestCase

from taxes import data

YEAR = 2023
NOW = date(day=1, month=1, year=YEAR)
FEB = date(day=1, month=2, year=YEAR)


class TestOperation(TestCase):
    def test_total(self):
        op = data.Operation(stock='STOC4', quantity=100, price=1.234567, date=NOW)
        self.assertEqual(op.total, 123.4567)

    def test_buy_inheritance(self):
        op = data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW)
        self.assertEqual(op.total, 100)

    def test_sell_type(self):
        op = data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW)
        self.assertTrue(isinstance(op, data.Sell))
        self.assertFalse(isinstance(op, data.Buy))


class TestMonthlyBucket(TestCase):
    def setUp(self):
        self.bucket = data.MonthlyBucket()

    def test_empty_total(self):
        self.assertEqual(self.bucket.total, 0.0)

    def test_total(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.23, date=NOW))
        self.assertEqual(self.bucket.total, 223.0)

    def test_empty_quantity(self):
        self.assertFalse(self.bucket.quantity)

    def test_quantity(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.bucket.add(data.Buy(stock='STOC4', quantity=300, price=1.0, date=NOW))
        self.assertEqual(self.bucket.quantity, 400)

    def test_empty_length(self):
        self.assertFalse(len(self.bucket))

    def test_lenght(self):
        self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.bucket.add(data.Buy(stock='STOC4', quantity=300, price=1.0, date=NOW))
        self.assertEqual(len(self.bucket), 2)

    def test_add_different_op_types(self):
        self.bucket.add(data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW))
        with self.assertRaises(AssertionError):
            self.bucket.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))


class TestMonthOperations(TestCase):
    def setUp(self):
        self.month = data.MonthOperations(month=1)

    def test_adding_ops(self):
        self.month.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.month.add(data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.month.add(data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW))
        self.assertEqual(len(self.month.buy), 2)
        self.assertEqual(len(self.month.sell), 1)

    def test_adding_invalid_operation(self):
        with self.assertRaises(TypeError):
            self.month.add(
                data.Operation(stock='STOC4', quantity=100, price=1.0, date=NOW)
            )


class TestYearOpsSingleStock(TestCase):
    # issue #1 will fix this
    def test_same_month_buy_sell(self):
        with self.assertRaises(AssertionError):
            data.YearOperations('STOC4', YEAR, {}, [
                data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
                data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW)
            ])

    # issue #2 will fix this
    def test_sell_more_than_20k_in_a_month(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=1, price=20000.0, date=NOW),
            data.Sell(stock='STOC4', quantity=1, price=20000.01, date=FEB)
        ])
        with self.assertRaises(AssertionError):
            year.calculate_loss_or_profit()

    def test_calculate_loss_only_buy_ops(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, 0.0)
        self.assertFalse(year.months[NOW.month].has_loss)

    def test_calculate_loss_with_profit(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Sell(stock='STOC4', quantity=100, price=2.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, 0.0)
        self.assertFalse(year.months[NOW.month].has_loss)

    def test_calculate_loss_successfully(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=2.0, date=NOW),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, -100.0)
        self.assertTrue(year.months[NOW.month].has_loss)

    def test_calculate_loss_successfully_with_input(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 200.0,
            'quantidade': 100,
        }, [
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.accum_loss, -100.0)
        self.assertTrue(year.months[NOW.month].has_loss)

    def test_calculate_profit_only_buy_ops(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.tax_free_profit, 0.0)

    def test_calculate_profit_successfully(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Sell(stock='STOC4', quantity=100, price=2.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.tax_free_profit, 100.0)

    def test_calculate_profit_successfully_with_input(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 100,
        }, [
            data.Sell(stock='STOC4', quantity=100, price=2.0, date=FEB)
        ])
        year.calculate_loss_or_profit()
        self.assertEqual(year.tax_free_profit, 100.0)

    def test_getting_accumulated_total_no_op(self):
        year = data.YearOperations('STOC4', YEAR, {}, [])
        self.assertFalse(year.accumulated_total('BUY'))
        self.assertFalse(year.accumulated_total('SELL'))

    def test_getting_accumulated_total_buy_only(self):
        year = data.YearOperations('STOC4', YEAR, {}, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        self.assertEqual(year.accumulated_total('BUY'), 200.0)
        self.assertEqual(year.accumulated_total('SELL'), 0.0)

    def test_getting_accumulated_total_buy_with_input(self):
        year = data.YearOperations('STOC4', YEAR,  {
            'total': 100.0,
            'quantidade': 100,
        }, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=NOW),
        ])
        self.assertEqual(year.accumulated_total('BUY'), 200.0)
        self.assertEqual(year.accumulated_total('SELL'), 0.0)

    def test_getting_accumulated_total_sell_only(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 200,
        }, [
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=FEB)
        ])
        self.assertEqual(year.accumulated_total('BUY'), 100.0)
        self.assertEqual(year.accumulated_total('SELL'), 200.0)

    def test_getting_acumulated_quantity_empty_class(self):
        year = data.YearOperations('STOC4', YEAR, {}, [])
        self.assertFalse(year.accumulated_quantity())

    def test_getting_acumulated_quantity_input_only(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 200,
        }, [])
        self.assertEqual(year.accumulated_quantity(), 200)
        self.assertEqual(year.accumulated_quantity(month=0), 200)

    def test_getting_acumulated_quantity_successfully(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 200,
        }, [
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=date(day=1, month=3, year=YEAR)),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=date(day=1, month=4, year=YEAR)),
        ])
        self.assertEqual(year.accumulated_quantity(month=0), 200)
        self.assertEqual(year.accumulated_quantity(month=1), 100)
        self.assertEqual(year.accumulated_quantity(month=2), 200)
        self.assertEqual(year.accumulated_quantity(month=3), 100)
        self.assertEqual(year.accumulated_quantity(), 0)

    def test_getting_accumulated_quantity_buy_or_sell_successfully(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 200,
        }, [
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=NOW),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=date(day=1, month=3, year=YEAR)),
            data.Sell(stock='STOC4', quantity=100, price=1.0, date=date(day=1, month=4, year=YEAR)),
        ])

        self.assertEqual(year.accumulated_quantity(operation_type='BUY'), 300)
        self.assertEqual(year.accumulated_quantity(operation_type='SELL'), 300)

    def test_getting_acumulated_average_empty_class(self):
        year = data.YearOperations('STOC4', YEAR, {}, [])
        self.assertFalse(year.accumulated_average())

    def test_getting_acumulated_average_input_only(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 100,
        }, [])
        self.assertEqual(year.accumulated_average(), 1.0)

    def test_getting_accumulated_average_successfully(self):
        year = data.YearOperations('STOC4', YEAR, {
            'total': 100.0,
            'quantidade': 200,
        }, [
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB),
            data.Buy(stock='STOC4', quantity=100, price=1.0, date=FEB),
        ])
        self.assertEqual(year.accumulated_average(), 0.75)
