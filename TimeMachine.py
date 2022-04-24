from Bank import Bank
import VirtualWallet
import Strategy

from typing import Callable, List
import sqlite3
from datetime import datetime, date, timedelta


class TimeMachine:
    def __init__(self, start: str, end: str, devise: str = 'EUR'):
        self._start = date.fromisoformat(start)
        self._end = date.fromisoformat(end)
        self._devise = devise
        self._db = None
        self._bank = None
        self._wallet = None

    def __del__(self):
        if self.isDBDefined():
            r = self._db.execute('drop table if exists TMP_HISTORIC')
            self._db.close()

    def isDBDefined(self) -> bool:
        return self._db is not None

    def isBankDefined(self) -> bool:
        return self._bank is not None

    def isWalletDefined(self) -> bool:
        return self._wallet is not None

    def initDB(self) -> None:
        if not self.isBankDefined():
            print(f"You must define a bank before initializing Database !")
            exit(1)
        self._db = sqlite3.connect('timeMachine.db')
        self._db.execute(
            'create table if not exists CURRENCIES (name text, id text)')
        if self._db.execute('select count(*) from CURRENCIES').fetchone() == (0,):
            data = self._bank.getCurrencies()
            for currency in data:
                self._db.execute('insert into CURRENCIES values (:name, :id)',
                                 {
                                     'name': currency['base_currency'],
                                     'id': currency['id']
                                 }
                                 )

        self._db.commit()

    def attachWallet(self, wallet: VirtualWallet) -> None:
        self._wallet = wallet

    def chooseBank(self, bank: Callable[[], Bank]) -> None:
        self._bank = bank()

    def existsCurrency(self, currency: str) -> bool:
        if not self.isDBDefined():
            print(f"You must initialize the Database first !")
            exit(1)
        result = self._db.execute(
            'select * from CURRENCIES where name = :currency', {'currency': currency})
        data = result.fetchone()
        if data is None:
            return False
        else:
            return True

    def getData(self, currency: str):
        if self._bank is None:
            print("You must specify a bank before !")
        else:
            if not self.existsCurrency(currency):
                print(
                    f"The currency {currency} is not available in your bank {self._bank.NAME}")
                exit(2)
            d = self._end - self._start
            h_total = d.days * 24
            if h_total <= 300:
                self._historicalDateToDB(self._bank.getHistoricalData(
                    currency + '-' + self._devise, self._start, self._end, 3600))
            else:
                steps = 300
                start = self._start
                end = self._start + timedelta(hours=steps)
                while h_total > 0:
                    if h_total >= steps:
                        h_total -= steps
                        end = start + timedelta(hours=steps)
                    else:
                        end = self._end
                        h_total = 0
                    self._historicalDateToDB(self._bank.getHistoricalData(
                        currency + '-' + self._devise, start, end, 3600))
                    start = end

    def _historicalDateToDB(self, data: List[List]) -> None:
        self._db.execute(
            'create table if not exists TMP_HISTORIC (date text, time text, cost real)')
        for row in data:
            # print(f"#DEBUG - row[0] {row[0]}")
            date_cur = datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d')
            time = datetime.fromtimestamp(row[0]).strftime('%H:%M:%S')
            self._db.execute('insert into TMP_HISTORIC values (:date, :time, :cost)',
                             {
                                 'date': date_cur,
                                 'time': time,
                                 'cost': row[1]
                             })

        self._db.commit()

    def showData(self, type: str = 'csv', extra: List = None):
        result = self._db.execute('select * from TMP_HISTORIC order by date,time')
        if type == "graph":
            data = []
            xAxisValues = []
            xAxisStep = 0
            import matplotlib.pyplot as plt
        
        for row in result.fetchall():
            if type == 'csv':
                print(f"{row[0]};{row[1]};{row[2]}")
            elif type == 'graph':
                data.append(row[2])
                if xAxisStep % 100 == 0:
                    xAxisValues.append(row[0])
                else:
                    xAxisValues.append('')
                xAxisStep += 1
            else: 
                print('ShowData : Unsupported type')
                exit(3)
        if type == 'graph':
            plt.plot(data)
            plt.xlabel('Time')
            plt.ylabel(f"Value ({self._devise})")
            plt.tick_params(axis='x', length=0)
            plt.ylim(bottom=0)
            for i in range(len(xAxisValues)):
                if xAxisValues[i] != '':
                    plt.plot([i,i] , [0 , data[i]] , linestyle='dashed', color='#cfd7e6')
            plt.xticks(list(range(len(xAxisValues))) , xAxisValues, rotation=45)
            if extra is not None:
                for transation in extra:
                    if transation[0] == "buy":
                        plt.plot(transation[6], transation[5], color='#f00', marker='v')
                    else:
                        plt.plot(transation[6], transation[5], color='#0f0', marker='^')
                    
            plt.show()

    def testStrategy(self, strategy: Strategy) -> List:
        if not self.isWalletDefined():
            print("You must attach a Wallet first ! ")
            exit(1)
        result = self._db.execute('select * from TMP_HISTORIC order by date,time')
        last_op = None
        n = 0
        for row in result.fetchall():
            if last_op == None:
                self._wallet.buy(self._wallet.getTotalFunds(), row[2], row[0] , row[1] , n)
                buyRate = row[2]
                last_op = 'buy'
            else:
                if last_op == 'buy':
                    if strategy.getAction('sell') == 'up':
                        if row[2] >= buyRate + buyRate * strategy.getRate('sell') / 100:
                            self._wallet.sell(self._wallet.getTotalCoins(), row[2], row[0], row[1], n)
                            last_op = 'sell'
                            buyRate = row[2]
                    if strategy.getAction('sell') == 'down':
                        if row[2] >= buyRate - buyRate * strategy.getRate('sell') / 100:
                            self._wallet.sell(self._wallet.getTotalCoins(), row[2], row[0], row[1], n)
                            last_op = 'sell'
                            buyRate = row[2]
                    elif last_op == 'sell':
                        if strategy.getAction('buy') == 'up':
                            if row[2] >= buyRate + buyRate * strategy.getRate('buy') / 100:
                                self._wallet.buy(self._wallet.getTotalFunds(), row[2], row[0], row[1], n)
                                last_op = 'buy'
                                buyRate = row[2]
                        if strategy.getAction('buy') == 'down':
                            if row[2] >= buyRate + buyRate * strategy.getRate('buy') / 100:
                                self._wallet.buy(self._wallet.getTotalFunds(), row[2], row[0], row[1], n)
                                last_op = 'buy'
                                buyRate = row[2]
            n += 1

        self._wallet.showTransactions()
        return self._wallet.getTransactions()