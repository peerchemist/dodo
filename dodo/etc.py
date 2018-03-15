
'''various helper methods'''

from cryptotik.common import ExchangeWrapper

def satoshi_to_bitcoin(rate: str) -> float:
    '''convert amount of satoshi to Bitcoin'''

    btc = 0.00000001
    rate = ''.join(i for i in rate if i.isdigit())

    return float(rate) * btc


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
