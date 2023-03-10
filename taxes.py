#!/usr/bin/env python3
import os
import sys
import json
import logging


logging.basicConfig(
    format='%(asctime)s [%(levelname)s](%(funcName)s:%(lineno)d) %(message)s',
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def load_input_file(filename):
    if not os.path.exists(filename):
        logger.error('Missing %s', filename)
        sys.exit(1)

    with open(filename) as file:
        try:
            stocks = json.loads(file.read())
        except json.JSONDecodeError as error:
            logger.info('Invalid json file %s. Fix it and then retry.', filename)
            sys.exit(1)

    # sanity check
    for stock, details in stocks.items():
        logger.info('Checking %s...', stock)
        assert 'preco-medio' in details
        assert 'quantidade' in details

    logger.info('...all good!')

    return stocks



def run():
    load_input_file('posicoes-iniciais.json')



if __name__ == '__main__':
    run()
