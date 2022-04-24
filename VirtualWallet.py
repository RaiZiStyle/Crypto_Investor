#!/usr/bin/env python3

from typing import List


class VirtualWallet:
    def __init__(self, value: float):
        self._value = value
        self._coins = 0
        # [action, solde_euros, solde_coins, date, heure, taux_coin, numero_opération]
        self._transations = []

    def getTotalFunds(self) -> float:
        return self._value

    def getTotalCoins(self) -> float:
        return self._coins

    def getTransactions(self) -> List:
        return self._transations

    def showTransactions(self) -> None:
        for transation in self._transations:
            if transation[0] == 'buy':
                print(
                    f"{transation[3]} - {transation[4]} : achat de {transation[2]} coin pour {transation[1]} € (taux : {transation[5]}")
            else:
                print(
                    f"{transation[3]} - {transation[4]} : vente de {transation[2]} coins pour {transation[1]} € (taux : {transation[5]}")

    def buy(self, value: float, coinRate: float, date: str, time: str, num_op: int) -> None:
        if value > self._value:
            print(f"Not enougt funds in wallet")
        self._value -= value
        self._coins -= value / coinRate
        self._transations.append(
            ('buy', value, self._coins, date, time, coinRate, num_op))

    def sell(self, coin: float, coinRate: float, date: str, time: str, num_op: int) -> None:
        if coin > self._coins:
            print(f"Not enought coins in wallet")
        self._coins -= coin
        self._value = coin * coinRate
        self._transations.append(
            ('sell', self._value, coin, date, time, coinRate, num_op))
