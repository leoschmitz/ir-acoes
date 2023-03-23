import logging
from calendar import month_name

from data import Buy
from data import YearOperations

logger = logging.getLogger(__name__)


class Report:
    def __init__(self, current_position, b3input):
        # at least one operation is required and 1 year only
        assert len(b3input) == 1
        self.year = list(b3input.keys())[0]
        self.current = current_position
        self.b3input = b3input[self.year]
        self.stocks = []

    def prepare(self):
        self.stocks = []
        for stock, operations in self.b3input.items():
            logger.info('--------------')
            logger.info('Reporting for %s', stock)
            input_ = self.current.get(stock, {})
            logger.info('Input: %s', input_)
            logger.info('Total operations %s', len(operations))
            year = YearOperations(stock, operations[0].date.year, input_, operations)
            logger.info(
                'buy %s sell %s',
                year.accumulated_average(),
                year.accumulated_average(operation_type='SELL'))
            self.stocks.append(year)
            year.calculate_loss_or_profit()

        # stocks with no operations
        no_ops = set(self.current.keys()) - set(self.b3input.keys())
        year = self.stocks[0].year
        for stock in no_ops:
            logger.info('--------------')
            logger.info('%s had no change this year %s')
            self.stocks.append(YearOperations(
                stock,
                self.year,
                self.current[stock],
                [],
            ))

        logger.info('--------------')
        for month in range(12):
            sold = 0.0
            for stock_ops in self.stocks:
                sold += stock_ops.months[month].sell.total

            logger.info('On %s you sold %s total', month_name[month+1], round(sold, 2))

    def net_worth(self):
        logger.info('--------------')
        logger.info('BENS E DIREITOS')
        logger.info('Grupo 3 - Participações societárias')
        logger.info('Código 1 - Ações (inclusive as listadas em bolsa)')
        for year in self.stocks:
            logger.info(
                '%s - %s ACOES - PRECO MEDIO %s',
                year.stock,
                year.accumulated_quantity(),
                year.accumulated_average(),
            )

            logger.info(
                'Situação em 31/12/%s %s, Situação em 31/12/%s %s',
                year.year - 1,
                year.previous_total,
                year.year,
                year.accumulated_quantity() * year.accumulated_average()
            )
