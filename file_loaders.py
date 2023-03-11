import logging
import os
import sys
import json
from datetime import datetime
from enum import IntEnum
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


class col(IntEnum):
    date = 0
    type_ = 1
    code = 5
    quantity = 6
    price = 7


def _parse_b3_file(filename):
    logger.info('parsing %s', filename)
    workbook = load_workbook(filename)

    worksheet = workbook['Negociação']
    rows = iter(worksheet.rows)
    titles = [title.value for title in next(rows)]
    logger.info('Loading -> %s', ', '.join(titles))

    assert 'Data do Negócio' == titles[col.date]
    assert 'Tipo de Movimentação' == titles[col.type_]
    assert 'Código de Negociação' == titles[col.code]
    assert 'Quantidade' == titles[col.quantity]
    assert 'Preço' == titles[col.price]

    stocks = {}
    for row in rows:
        operation = [cell.value for cell in row]

        op_type = operation[col.type_].upper()
        assert op_type in ('VENDA', 'COMPRA')

        date = operation[col.date]
        date = datetime.strptime(operation[col.date], '%d/%m/%Y').date()

        quantity = operation[col.quantity]
        assert isinstance(quantity, int)

        price = float(operation[col.price])

        values = [op_type, date, quantity, price]

        code = operation[col.code]
        if code not in stocks:
            stocks[code] = [values]
        else:
            stocks[code].append(values)

    workbook.close()
    return stocks


def load_b3_file():
    xlsx_filenames = []
    logger.info('Loading B3 file')
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith('xlsx'):
            xlsx_filenames.append(filename)

    assert len(xlsx_filenames) == 1

    return _parse_b3_file(xlsx_filenames[0])
