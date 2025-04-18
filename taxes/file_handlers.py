import logging
import os
import sys
import json
from datetime import datetime
from enum import IntEnum
from openpyxl import load_workbook
from taxes.data import Buy
from taxes.data import Sell

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
    total = 8


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

    year = 0
    stocks = {}
    for row in rows:
        row = [cell.value for cell in row]
        logger.debug(row)

        op_type = row[col.type_].upper()
        assert op_type in ('VENDA', 'COMPRA')

        date = row[col.date]
        if isinstance(date, str):
            date = datetime.strptime(row[col.date], '%d/%m/%Y').date()
        else:
            date = date.date()
        # validate there is a single year in the Excel sheet
        if not year:
            year = date.year
        assert year == date.year

        quantity = row[col.quantity]
        assert isinstance(quantity, int)
        price = float(row[col.price])
        code = row[col.code]

        if op_type == 'COMPRA':
            operation = Buy(code, quantity, price, date)
        else:
            operation = Sell(code, quantity, price, date)

        try:
            assert round(operation.total, 2) == round(row[col.total], 2)
        except AssertionError:
            logger.warning("No match between %s and %s ", round(operation.total, 2), round(row[col.total], 2))
            if abs(round(operation.total, 2) - round(row[col.total], 2)) > 1.0:
                raise
        if operation.stock not in stocks:
            stocks[operation.stock] = [operation]
        else:
            stocks[operation.stock].append(operation)

    workbook.close()
    return {year: stocks}


def load_b3_file():
    xlsx_filenames = []
    logger.info('Loading B3 file')
    for filename in os.listdir(os.path.dirname(__file__).replace('taxes', '')):
        if filename.endswith('xlsx'):
            xlsx_filenames.append(filename)

    assert len(xlsx_filenames) == 1

    return _parse_b3_file(xlsx_filenames[0])


def pretty_json(year: int, content: dict):
    dump_args = {
        'sort_keys': True,
        'indent': 4,
        'ensure_ascii': False,
    }
    with open(f'posicoes-finais.{year}.json', 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, **dump_args)
        outfile.write('\n')


def save_output(stocks):
    content = {}
    for stock in stocks:
        if not stock.accumulated_quantity():
            continue

        content[stock.stock] = {
            'total': round(
                stock.accumulated_quantity() * stock.accumulated_average(), 2
            ),
            'preco-medio': round(stock.accumulated_average(), 9),
            'quantidade': stock.accumulated_quantity(),
        }
    pretty_json(stocks[0].year, content)
