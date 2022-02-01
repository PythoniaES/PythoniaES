
from src.Bot import CriptoBot_I
from config import *

api_key = BINANCE['key']
api_secret = BINANCE['secret']



bot = CriptoBot_I()
bot.Set_Parameters(api_key = api_key, api_secret = api_secret, cripto = CRIPTO, ref = REF, period = PERIOD, capital = CAPITAL, EMA_S = EMA_S, EMA_F = EMA_F)
bot.run()
