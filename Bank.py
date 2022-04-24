#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import List, Tuple
import requests

class Bank(ABC):
    NAME: str
    URL: str
    API: str
    TIME: str
    
    def _makeRequest(self, *args: Tuple[str]) -> str:
        """
        TODO: Mettre un paramettre verbose pour indique si oui ou non on veut print la request
        """
        query = self.__class__.API # Bank.API ne peu pas fonctionner a cause de l'héritage
        # query = self.Bank.API

        for arg in args:
            query += arg + '/'
        return query[:-1]
    
    def _request(self, query: str):
        data = requests.get(query)
        if data.status_code != 200:
            print(f"Error while executing request: {query}")
        return data.json()

    @abstractmethod
    def getHistoricalData(self, currency: str, start : str, end : str, granularity : int) -> List:
        pass

    @abstractmethod
    def getCurrencies(self) -> List:
        pass


if __name__ == "__main__":
    # test = Bank()
    pass