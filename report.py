import logging
from calendar import month_name

from data import Buy
from data import YearOperations

logger = logging.getLogger(__name__)


class Report:
    def __init__(self, current_position, b3input):
        self.current = current_position
        self.b3input = b3input

    def execute(self):
        all_operations = []
        for stock, operations in self.b3input.items():
            logger.info('--------------')
            logger.info('Reporting for %s', stock)
            input_ = self.current.get(stock, {})
            logger.info('Input: %s', input_)
            logger.info('Total operations %s', len(operations))
            year = YearOperations(input_, operations)
            logger.info(
                'buy %s sell %s', year.accumulated_average('BUY'),
                year.accumulated_average('SELL'))
            all_operations.append(year)

        for month in range(12):
            sold = 0.0
            for stock_ops in all_operations:
                sold += stock_ops.months[month].sell.total

            logger.info('On %s you sold %s total', month_name[month+1], round(sold, 2))
