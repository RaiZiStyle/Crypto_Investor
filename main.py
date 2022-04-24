#!/usr/bin/env python3

from TimeMachine import TimeMachine
from CoinBasePro import CoinBasePro
from Strategy import Strategy
from VirtualWallet import VirtualWallet

if __name__ == '__main__':
    wallet = VirtualWallet(1000)
    
    strat = Strategy('5 percent')
    strat.defRule('buy', 'down', 5)
    strat.defRule('sell', 'up', 5)

    timeMachine = TimeMachine(start='2021-05-01', end='2021-06-21')
    timeMachine.chooseBank(CoinBasePro)
    timeMachine.attachWallet(wallet)
    timeMachine.initDB()
    timeMachine.getData('ETH')
    transactions = timeMachine.testStrategy(strat)
    timeMachine.showData(type='graph', extra=transactions)