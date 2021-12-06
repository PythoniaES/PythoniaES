from binance.client import Client
import datetime as dt
import pytz
from src.utils import*
import time
import pandas as pd


class CriptoBot_I():
    def __init__(self):
        self.quantity = None
        self.buysignal = None
        self.sellsignal = None
        self.RUN = True
        self.error_update = True
        self.orden = None

    def Set_Parameters(self, api_key, api_secret, cripto, ref, capital, EMA_F, EMA_S, period):
        self.client = Client(api_key, api_secret)

        # Parameeters
        self.cripto = cripto
        self.ref = ref
        self.exchange = self.cripto + self.ref
        self.single_operation_capital = capital
        self.EMA_F = EMA_F
        self.EMA_S = EMA_S
        self.interval = period

        # Data

        self.df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume', 'start', 'EMA_F', 'EMA_S'])
        self.H_df = pd.DataFrame(
            columns=['start', 'open', 'high', 'low', 'close', 'volume', 'EMA_F', 'EMA_S', 'operacion', 'avg_price'])

        # Filters
        info = self.client.get_symbol_info(self.exchange)['filters'][2]
        self.minQty, self.stepSize, self.maxQty = Get_Exchange_filters(info)

        self.maxDeciamlQty = Calculate_max_Decimal_Qty(self.stepSize)

        self.capital = Get_Capital(self.client.get_account()['balances'], self.ref)


    def Order(self,side,price):
        Qty = Calculate_Qty(price, self.single_operation_capital, self.minQty, self.maxQty, self.maxDeciamlQty)
        if not Qty:
            self.RUN = False
        else:
            if side == 'BUY':
                self.quantity = Qty
            else:
                Qty = self.quantity
                self.quantity = None
                pass
            try:
                self.orden = self.client.create_order(
                    symbol=self.exchange,
                    side=side,
                    type='MARKET',
                    quantity=Qty)
            except:
                print('Order error')


    def parser(self, data):
        df = pd.DataFrame(data)
        df = df.drop([6, 7, 8, 9, 10, 11], axis=1)

        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names

        for col in col_names:
            df[col] = df[col].astype(float)

        df['start'] = pd.to_datetime(df['time'] * 1000000)
        df['EMA_F'] = np.nan
        df['EMA_S'] = np.nan
        if self.df.shape[0] != 0:
            if self.df.start.iloc[-1] == df.start.iloc[-1]:
                pass
            else:
                self.error_update = False
        return df

    def last_data(self):

        if self.df.shape[0] == 0:
            candles = self.client.get_klines(symbol=self.cripto + self.ref, interval=self.interval,
                                                     limit=self.EMA_S + 1)
            self.df = self.parser(candles)
        else:
            while self.error_update:
                try:
                    candles = self.client.get_klines(symbol=self.cripto + self.ref, interval=self.interval,
                                                             limit=1)
                    df_temp = self.parser(candles)
                    time.sleep(1)
                except:
                    print('Error on data extraction')

            self.df = self.df.append(df_temp, ignore_index=True)
            self.df.drop(index=0, inplace=True)
            self.df.index = list(range(self.EMA_S + 1))

        self.df.EMA_F = self.df.open.ewm(self.EMA_F).mean()
        self.df.EMA_S = self.df.open.ewm(self.EMA_S).mean()

        self.buysignal = Crossover(self.df.EMA_F.values[-2:], self.df.EMA_S.values[-2:])
        self.sellsignal = Crossover(self.df.EMA_S.values[-2:], self.df.EMA_F.values[-2:])

        self.error_update = True
        self.H_df = self.H_df.append(self.df.iloc[-1, :])
        if self.H_df.shape[0] > 100000:
            self.H_df = self.H_df.tail(10000)




    def Single_Operation(self):
        self.capital = Get_Capital(self.client.get_account()['balances'], self.ref)
        if self.capital <= self.single_operation_capital:
            print('money finished')
            self.RUN = False
        self.last_data()
        price = float(list(x for x in self.client.get_symbol_ticker() if x.get('symbol')==self.exchange)[0].get('price'))
        self.H_df.avg_price.iloc[-1] = price

        if (not self.orden or self.orden.get('status') in ['FILLED', 'CANCELED', 'REJECTED', 'EXPIRED']):

            if not self.quantity:
                if self.buysignal:
                    try:
                        self.Order(side='BUY', price=price)
                        self.H_df.operacion.iloc[-1] = 'BUY'
                    except Exception as e:
                        print(e)
                        self.H_df.operacion.iloc[-1] = 'ERROR'
            else:
                if self.sellsignal:
                    try:
                        self.Order(side='SELL',price=price)
                        self.H_df.operacion.iloc[-1] = 'SELL'
                    except Exception as e:
                        print(e)
                        self.H_df.operacion.iloc[-1] = 'ERROR'




        self.H_df.to_csv('./{}_{}_{}_{}.csv'.format(self.cripto+self.ref, self.interval, self.EMA_F,self.EMA_S))


    def run(self):
        if 'm' in self.interval:
            if len(self.interval) == 2:
                step = int(self.interval[0])
            else:
                step = int(self.interval[:2])
        elif self.interval == '1h':
            step = 60
        else:
            print('interval error')
            return
        self.last_data()
        START = self.df.start.iloc[-1] + dt.timedelta(minutes=step)
        print(START)
        while dt.datetime.now(dt.timezone.utc) < pytz.UTC.localize(START):
            time.sleep(1)
            pass
            print('Strarting Bot...\n')
        time.sleep(3)  # para ser seguros de encontrar los datos de la velas siguente
        print('Bot started')
        while self.RUN:
            temp = time.time()
            self.Single_Operation()
            retraso = time.time() - temp
            time.sleep(60 * step - retraso)




