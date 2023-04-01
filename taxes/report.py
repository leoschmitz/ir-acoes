import logging
from calendar import month_name

from taxes.data import Buy
from taxes.data import YearOperations

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
                'buy %s sell %s remaining stock %s',
                year.accumulated_average(),
                year.accumulated_average(operation_type='SELL'),
                year.accumulated_quantity(),
            )
            self.stocks.append(year)
            year.calculate_loss_or_profit()

        # stocks with no operations
        no_ops = set(self.current.keys()) - set(self.b3input.keys())
        year = self.stocks[0].year
        for stock in no_ops:
            logger.info('--------------')
            logger.info('%s had no change in %s', stock, year)
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
                round(year.accumulated_average(), 5),
            )

            logger.info(
                'Situação em 31/12/%s %s, Situação em 31/12/%s %s',
                year.year - 1,
                year.previous_total,
                year.year,
                round(year.accumulated_quantity() * year.accumulated_average(), 2)
            )

    def profit(self):
        logger.info('--------------')
        logger.info('RENDIMENTOS ISENTOS E NÃO TRIBUTÁVEIS')
        logger.info('Código 20 - Ganhos líquidos em operações no mercado à vista de '
                    'ações negociadas em bolsa de valores nas alienações realizadas até '
                    'R$ 20.000,00 em cada mês, para o conjuto de ações')
        tax_free = 0.0
        for year in self.stocks:
            tax_free += year.tax_free_profit
        logger.info('Valor %s', round(tax_free, 2))

    def losses(self):
        logger.info('--------------')
        logger.info('RENDA VARIÁVEL - GANHOS LÍQUIDOS OU PERDAS EM OPERAÇÕES COMUNS/DAY-'
                    'TRADE - TITULAR')
        for month_number in range(12):
            loss = 0.0
            for stock in self.stocks:
                # even though it will mostly be 0.0, I'd rather not accumulate error
                # doing floating point operations
                month = stock.months[month_number]
                if month.has_loss:
                    loss += month.loss
            logger.info(
                '%s Mercado à Vista %s',
                month_name[month_number+1],
                round(loss, 2),
            )
