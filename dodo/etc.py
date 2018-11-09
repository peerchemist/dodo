
'''various helper methods'''

from random import sample
from cryptotik.common import ExchangeWrapper


def str_to_bitcoin(rate: str) -> float:
    '''convert amount of satoshi to Bitcoin'''

    btc = 0.00000001
    rate = ''.join(i for i in rate if i.isdigit())

    return float(rate) * btc


def satoshi_to_bitcoin(rate: int) -> float:

    return float(rate / 10**8)


def bitcoin_to_satoshi(rate: float) -> float:

    return int(rate * 10**8)


def n_worth(base: float, target_price: float,
            market_pair: str, exchange: ExchangeWrapper) -> float:

    '''calculate the amount of <coin> you would
    be able to purchase at <price> expressed in <base>'''

    last_price = float(exchange.get_market_ticker(market_pair)['last'])

    taker_fee = float(exchange.taker_fee)
    maker_fee = float(exchange.maker_fee)

    if last_price >= target_price:
        _base = base - (base * taker_fee)
        return _base / target_price

    else:
        _base = base - (base * maker_fee)
        return _base / target_price


def spread_it(rate: int, spread: int,
              levels: int) -> list:
    '''pick random price >levels< within a range
       only works with integers'''

    rng = range(int(rate - spread),
                int(rate + spread))

    return sample(rng, levels)


def ladder_price(amount: float, levels: int) -> list:
    '''calculate n levels from amount'''

    return [round(amount/levels, 6) for l in range(levels)]
