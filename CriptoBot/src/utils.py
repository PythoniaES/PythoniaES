import numpy as np
from typing import Tuple


def Get_Exchange_filters(info) -> Tuple:
        minQty = float(info.get('minQty'))
        stepSize = float(info.get('stepSize'))
        maxQty = float(info.get('maxQty'))
        return minQty, stepSize, maxQty


def Get_Capital(result, ref):
    for i in result:
        if i.get('asset') == ref:
            return float(i['free'])

def Calculate_max_Decimal_Qty(stepSize):
    max_decimal_quantity=0
    a = 10
    while stepSize*a<1:
      a = a*10**max_decimal_quantity
      max_decimal_quantity += 1
    return max_decimal_quantity

def Calculate_Qty(price, money, minQty, maxQty, maxDeciamlQty):

    Q = money / price
    if (Q < minQty or Q > maxQty):
        return False
    Q = np.round(Q, maxDeciamlQty)
    return Q



def Crossover(MF, MS):
    if (MF[0] < MS[0] and MF[1] >= MS[1]):
        return True
    else:
        return False




