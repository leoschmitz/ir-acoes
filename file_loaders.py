import logging
import os
import sys
import json
from openpyxl import load_workbook

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


def _parse_b3_file(filename):
    workbook = load_workbook(filename, read_only=True)
    logger.info('%s', workbook)


def load_b3_file():
    xlsx_filenames = []
    logger.info('Loading B3 file')
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith('xlsx'):
            xlsx_filenames.append(filename)

    assert len(xlsx_filenames) == 1

    _parse_b3_file(xlsx_filenames[0])
