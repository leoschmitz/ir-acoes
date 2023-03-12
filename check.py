import logging

logger = logging.getLogger(__name__)


def _average(operations):
    sum_ = 0.0
    total_operations = 0
    buy = {}
    sell = {}
    for operation in operations:
        total_operations += 1

    logger.info('Total operations %s', total_operations)

def averages(stocks):
    for stock, operations in stocks.items():
        logger.info('Averaging %s', stock)
        _average(operations)
