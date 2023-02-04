from utils.utils import *


class Market:

    def __init__(self, asOf, curves_map, market_prices):
        self._envDate = asOf
        self._curves_map = curves_map
        self._market_prices = market_prices

    def get_bond_clean_price(self, isin):
        return self._market_prices[isin]

    def get_curve(self, name):
        return self._curves_map[name]

