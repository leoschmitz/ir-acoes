#!/usr/bin/env python3
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s](%(funcName)s:%(lineno)d) %(message)s',
    level=logging.DEBUG,
)

from file_loaders import load_input_file
from file_loaders import load_b3_file

logger = logging.getLogger(__name__)


def run():
    logger.info('Loading input files')
    prev_year = load_input_file('posicoes-iniciais.json')
    workbook = load_b3_file()


if __name__ == '__main__':
    run()
