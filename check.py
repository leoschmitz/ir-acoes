import logging
from data import Buy
from data import Year

logger = logging.getLogger(__name__)


def averages(stocks):
    for stock, operations in stocks.items():
        logger.info('--------------')
        logger.info('Averaging %s', stock)
        year = Year.from_operations(operations)
        logger.info('buy %s sell %s', year.average('BUY'), year.average('SELL'))
