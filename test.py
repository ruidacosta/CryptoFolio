import os
import unittest

import cryptofolio


class TestCryptoFolio(unittest.TestCase):
    """
    Test calc_pnl
    """
    def test_calc_pnl(self):
        position = cryptofolio.Position('BTCEUR', 1.5, 25000)
        position.calc_pnl(50000)
        self.assertTrue(position.ticker == 'BTCEUR'
                        and position.quantity == 1.5
                        and position.buy_price == 25000
                        and position.current_price == 50000
                        and position.pnl == 37500)

    """
    Test as_prettytable_row
    """
    def test_as_prettytable_row(self):
        position = cryptofolio.Position('BTCEUR', 1.5, 25000)
        position.calc_pnl(50000)
        self.assertEqual(position.as_prettytable_row(), ['BTCEUR', 1.5, 25000, 50000, 37500])

    """
    Test save_data
    """
    def test_save_and_load_data(self):
        data = [{'name': 'Costa', 'first_name': 'Rui', 'age': 36, 'place': 'Vila Praia de Âncora'},
                {'name': 'Silva', 'first_name': 'Joaquim', 'age': 65, 'place': 'Caminha'},
                {'name': 'Torres', 'first_name': 'Maria', 'age': 42, 'place': 'Viana do Castelo'}]
        filename = 'test.data'
        cryptofolio.save_data(filename, data)
        loaded_data = cryptofolio.load_data(filename)
        os.remove(filename)
        self.assertEqual(loaded_data, data)

    """
    Test add_position
    """
    def test_add_position(self):
        ticker = 'BTCEUR'
        quantity = 0.56
        buy_price = 48000
        data = []
        position = cryptofolio.Position(ticker, quantity, buy_price)
        expect_data = [position]
        _, _, data = cryptofolio.add_position(ticker, quantity, buy_price, data)
        self.assertTrue(expect_data[0].ticker == data[0].ticker
                        and expect_data[0].quantity == data[0].quantity
                        and expect_data[0].buy_price == data[0].buy_price)

    """
    Test del_position
    """
    def test_del_position(self):
        ticker = 'ETHEUR'
        quantity = 4.351
        buy_price = 3548
        position = cryptofolio.Position(ticker, quantity, buy_price)
        data = [position]
        _, _, data = cryptofolio.del_position(ticker, data)
        self.assertListEqual(data, [])

    """
    Test edit_position
    """
    def test_edit_position(self):
        ticker = 'BTCEUR'
        quantity = 0.56
        buy_price = 48000
        position = cryptofolio.Position(ticker, quantity, buy_price)
        data = [position]
        new_quantity = 0.75
        new_buy_price = 48567
        new_position = cryptofolio.Position(ticker, new_quantity, new_buy_price)
        expect_data = [new_position]
        _, _, data = cryptofolio.edit_position(ticker, new_quantity, new_buy_price, data)
        self.assertTrue(data[0].ticker == expect_data[0].ticker
                        and data[0].quantity == expect_data[0].quantity
                        and data[0].buy_price == expect_data[0].buy_price)


if __name__ == '__main__':
    unittest.main()
