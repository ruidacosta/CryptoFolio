#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import requests
import pickle
import configparser
import os
from prettytable import PrettyTable


__version__ = '0.1'


class Position:
    def __init__(self, ticker: str, quantity: float, buy_price: float):
        self.ticker = ticker
        self.quantity = quantity
        self.buy_price = buy_price
        self.current_price = 0
        self.pnl = 0

    def calc_pnl(self, current_price: float):
        self.current_price = current_price
        self.pnl = (self.current_price * self.quantity) - (self.buy_price * self.quantity)

    def as_prettytable_row(self):
        return [self.ticker, self.quantity, self.buy_price, self.current_price, self.pnl]


class Style:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def process_arguments():
    parser = argparse.ArgumentParser(
        description='Control cryptocurrency protfolio PNL (Profit and Loss) using IEX Cloud API.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help='show version')
    parser.add_argument('-d', '--data', action='store', dest='data', help='data file')
    parser.add_argument('-c', '--config', action='store', dest='config', help='')

    subparsers = parser.add_subparsers(dest='command', help='Subparsers')

    list_command = subparsers.add_parser('list', help='list command')

    add_command = subparsers.add_parser('add', help='add command')
    add_command.add_argument('ticker', help='ticker to add')
    add_command.add_argument('quantity', help='quantity of ticket')
    add_command.add_argument('buy_price', help='buy price of ticket')

    del_command = subparsers.add_parser('del', help='delete command')
    del_command.add_argument('ticker', help='ticker of portfolio to delete')

    edit_command = subparsers.add_parser('modify', help='edit command')
    edit_command.add_argument('ticker', help='ticker to edit')
    edit_command.add_argument('quantity', help='quantity to edit')
    edit_command.add_argument('buy_price', help='buy price to edit')

    args = parser.parse_args()
    return vars(args)


def load_config(config: str):
    if config:
        config_file_path = os.path.expanduser(config)
    else:
        config_file_path = os.path.expanduser('~/.cryptofolio/cryptofolio.config')
    config = configparser.ConfigParser()
    if os.path.exists(config_file_path):
        config.read(config_file_path)
    else:
        create_config_file(config, config_file_path)
    return config


def create_config_file(config: configparser.ConfigParser, filename: str):
    config['MAIN'] = {'DataFile': '~/.cryptofolio/folio.data'}
    config['IEX CLOUD API'] = {'URL': '',
                               'Tokem': ''}
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as df:
        config.write(df)


def load_data(file_data: str) -> list[Position]:
    file_path = os.path.expanduser(file_data)
    if not os.path.exists(file_path):
        return []
    else:
        with open(file_path, 'rb') as fd:
            data = pickle.load(fd)
        return data


def save_data(file_data: str, data: list[Position]):
    file_path = os.path.expanduser(file_data)
    with open(file_path, 'wb') as fd:
        pickle.dump(data, fd, pickle.HIGHEST_PROTOCOL)


def get_crypto_price_from_api(url: str, ticker: str, token: str):
    url = f'{url}/{ticker}/price?token={token}'
    r = requests.get(url)
    return r.json()


def add_position(ticker: str, quantity: float, buy_price: float, data: list[Position]) -> (str, list, list[Position]):
    temp = Position(ticker, quantity, buy_price)
    data.append(temp)
    return f'Position added to Folio => Ticker: {ticker}, Quantity: {quantity}, Price: {buy_price}', [[ticker, quantity, buy_price]], data


def del_position(ticker: str, data: list[Position]) -> (str, list, list[Position]):
    result = [s for s in data if s.ticker != ticker]
    if len(result) == len(data):
        return f'{ticker} was not found in your Folio', None, result
    else:
        return f'{ticker} position was removed from your Folio', None, result


def edit_position(ticker: str, quantity: float, buy_price: float, data: list[Position]) -> (str, list, list[Position]):
    for i in range(len(data)):
        if data[i].ticker == ticker:
            data[i].quantity = quantity
            data[i].buy_price = buy_price
            break
    return f'{ticker} position was modified in your Folio', [[ticker, quantity, buy_price]], data


def list_positions(data: list[Position], configs: configparser.ConfigParser) -> (str, list, list[Position]):
    # msg = ''
    rows = []
    for position in data:
        api_data = get_crypto_price_from_api(configs['IEX CLOUD API']['url'], position.ticker,
                                             configs['IEX CLOUD API']['tokem'])
        position.calc_pnl(float(api_data['price']))
        rows.append(position.as_prettytable_row())
    return None, rows, data


def process_command(args, configs):
    data: list[Position]
    if args['data']:
        data = load_data(args['data'])
    else:
        data = load_data(configs['MAIN']['datafile'])
    if args['command'] == 'list':
        msg, rows, data = list_positions(data, configs)
    elif args['command'] == 'add':
        msg, rows, data = add_position(args['ticker'], float(args['quantity']), float(args['buy_price']), data)
    elif args['command'] == 'del':
        msg, rows, data = del_position(args['ticker'], data)
    elif args['command'] == 'modify':
        msg, rows, data = edit_position(args['ticker'], float(args['quantity']), float(args['buy_price']), data)
    else:
        msg = 'No command'
    save_data(configs['MAIN']['datafile'], data)
    return msg, rows


def print_prettytable(headers: list, rows: list):
    table = PrettyTable(headers)
    table.add_rows(rows)
    print(table)


def add_colors_to_table(rows: list[list]):
    for i in range(len(rows)):
        if len(rows[i]) > 3:
            if rows[i][4] < 0:
                rows[i][4] = f'{Style.RED}{rows[i][4]}{Style.ENDC}'
            else:
                rows[i][4] = f'{Style.GREEN}{rows[i][4]}{Style.ENDC}'


def print_output(msg: str, rows: list, colors: bool = True):
    if msg:
        print(msg)
    if rows:
        if colors:
            add_colors_to_table(rows)
        if len(rows) > 0 and len(rows[0]) == 3:  # Add and edit commands
            print_prettytable(['Ticker', 'Quantity', 'Buy Price'], rows)
        elif len(rows) > 0 and len(rows[0]) > 3:  # list command
            print_prettytable(['Ticker', 'Quantity', 'Buy Price', 'Current Price', 'PNL'], rows)


def main():
    args = process_arguments()
    configs = load_config(args['config'])
    msg, rows = process_command(args, configs)
    print_output(msg, rows)


if __name__ == '__main__':
    main()
