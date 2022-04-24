#!/usr/bin/env python3

from Bank import Bank
from typing import Dict, List, Tuple


class CoinBasePro(Bank):
    NAME: str = 'Coinbase Pro'
    URL: str = 'https://pro.coinbase.com/'
    API: str = 'https://api.pro.coinbase.com/'
    TIME: str = 'GMT12:00:00'

    def __init__(self):
        super().__init__()

    def getCurrencies(self) -> List:
        return self._request(self._makeRequest('products'))

    def getHistoricalData(self, currency: str, start: str, end: str, granularity: int) -> List:
        print(f"Request : {CoinBasePro.API}products/{currency}/candles?start={start}{CoinBasePro.TIME}&end={end}{CoinBasePro.TIME}&granularity={granularity}")
        return self._request(self._makeRequest(f"products/{currency}/candles?start={start}{CoinBasePro.TIME}&end={end}{CoinBasePro.TIME}&granularity={granularity}"))
