import logging
from data import Buy

logger = logging.getLogger(__name__)


def _average(operations):
    buy_sum = 0.0
    sell_sum = 0.0
    buy_qtty = 0
    sell_qtty = 0
    total_ops = 0
    for operation in operations:
        total_ops += 1
        if isinstance(operation, Buy):
            buy_sum += operation.total
            buy_qtty += operation.quantity
            continue

        sell_sum += operation.total
        sell_qtty += operation.quantity

    logger.info('Total operations %s', total_ops)

    buy_qtty = 1 if not buy_qtty else buy_qtty
    sell_qtty = 1 if not sell_qtty else sell_qtty

    return {'buy': buy_sum / buy_qtty, 'sell': sell_sum / sell_qtty}


def averages(stocks):
    for stock, operations in stocks.items():
        logger.info('Averaging %s', stock)
        av = _average(operations)
        logger.info('buy %s sell %s', av['buy'], av['sell'])
