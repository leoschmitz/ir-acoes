#!/usr/bin/env python3
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s](%(funcName)s:%(lineno)d) %(message)s',
    level=logging.DEBUG,
)

from file_loaders import load_input_file
from file_loaders import load_b3_file
from report import Report

logger = logging.getLogger(__name__)


def run():
    logger.info('Loading input files')
    prev_stocks = load_input_file('posicoes-iniciais.json')
    current_stocks = load_b3_file()
    report = Report(prev_stocks, current_stocks)
    # throws some debugging logs
    report.prepare()
    # prints 'Bens e Direitos'
    report.net_worth()
    # prints 'Rendimentos isentos e não tributáveis'
    report.profit()


if __name__ == '__main__':
    run()
