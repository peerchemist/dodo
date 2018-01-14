#!/usr/bin/env python

from cryptotik import Wex, Poloniex, Bittrex
from cryptotik.common import ExchangeWrapper
import fire
import keyring
import pprint

supported = (Wex.name, Poloniex.name, Bittrex.name)
_secret_delimiter = '<\/&>'
pp = pprint.PrettyPrinter(width=80, compact=True)


def supported_exchanges():

    pp.pprint(supported)


def set_key(exchange: str, api: str, secret: str) -> None:
    '''set api/key for exchange'''

    assert exchange.lower() in supported, {'error': 'Unsupported exchange.'}

    keyring.set_password("dodo", exchange.lower(), api+_secret_delimiter+secret)


def keys(exchange: str) -> tuple:
    '''load keys from the keystore'''

    try:
        apikey, secret = keyring.get_password('dodo', exchange).split(_secret_delimiter)
        return apikey, secret
    except AttributeError:
        print({'error': 'No secret entry for {0}.'.format(exchange)})


def satoshi_to_bitcoin(rate: str) -> float:
    '''convert amount of satoshi to Bitcoin'''

    btc = 0.00000001
    rate = ''.join(i for i in rate if i.isdigit())

    return float(rate) * btc


def n_worth(base: float, target_price: float,
            market_pair: str, exchange: ExchangeWrapper) -> float:

    '''calculate the amount of <coin> you would
    be able to purchase at <price> expressed in <base>'''

    if exchange.name == "poloniex" or exchange.name == "wex":
        last_price = float(exchange.get_market_ticker(market_pair)['last'])
    if exchange.name == "bittrex":
        last_price = float(exchange.get_market_ticker(market_pair)['Last'])

    taker_fee = float(exchange.taker_fee)
    maker_fee = float(exchange.maker_fee)

    if last_price >= target_price:
        _base = base - (base * taker_fee)
        return _base / target_price

    else:
        _base = base - (base * maker_fee)
        return _base / target_price


class Dodo(object):

    def __init__(self, exchange, secret: str) -> None:
        self._ex = exchange(secret[0], secret[1], timeout=5)

    def markets(self) -> None:

        pp.pprint(self._ex.get_markets()
                  )

    def depth(self, market_pair: str) -> None:

        pp.pprint(self._ex.get_market_depth(market_pair)
                  )

    def spread(self, market_pair: str) -> None:

        pp.pprint(self._ex.get_market_spread(market_pair)
                  )

    def volume(self, market_pair: str) -> None:

        pp.pprint(self._ex.get_market_volume(market_pair)
                  )

    def buy(self, market_pair, rate, amount):

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.buy(market_pair, rate, amount)
                  )

    def buy_worth(self, market_pair: str, target_price: str, amount: float) -> None:
        '''Buy <amount> of base pair worth at <target price>
        : dodo btrx buy btc-xrp 2400sat 1btc'''

        if "sat" in str(target_price):
            target_price = satoshi_to_bitcoin(target_price)

        amount = n_worth(amount, target_price, market_pair, self._ex)

        pp.pprint(self._ex.buy(market_pair, target_price, amount)
                  )

    def margin_buy(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged buy order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to long buy
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self._ex.name == "poloniex"

        if "sat" in str(rate):
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.margin_buy(market_pair, rate, amount,
                  max_lending_rate)
                  )

    def sell(self, market_pair, rate, amount):

        if "sat" in str(rate):
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.sell(market_pair, rate, amount)
                  )

    def margin_sell(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged sell order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to short sell
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self._ex.name == "poloniex"

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.margin_sell(market_pair, rate, amount,
                  max_lending_rate)
                  )

    def orders(self, market_pair=None):
        '''show open orders'''

        if market_pair:
            pp.pprint(self._ex.get_open_orders(market_pair)
                      )

        else:
            if self._ex.name == "poloniex":
                pp.pprint({k: v for k, v in self._ex.get_open_orders().items() if v}
                          )
            else:
                pp.pprint(self._ex.get_open_orders())

    def cancel_order(self, order_id):
        '''cancel order <id>'''

        pp.pprint(self._ex.cancel_order(order_id))

    def cancel_all_orders(self):
        '''cancel all active orders'''

        pp.pprint(self._ex.cancel_all_orders())

    def deposit(self, coin, new=None):
        '''show deposit address for <coin>
        : new - generate new deposit address before printing it out. [works only with poloniex.]'''

        if new and self._ex.name == "poloniex":
            print('Requesting for new deposit address...')
            print(self._ex.get_new_deposit_address(coin))

        pp.pprint(self._ex.get_deposit_address(coin))

    def deposit_history(self, coin=None):

        if not coin:
            pp.pprint(self._ex.get_deposit_history()
                      )
        else:
            pp.pprint([i for i in self._ex.get_deposit_history() if i['currency'] == coin.upper()]
                      )

    def new_deposit_address(self, coin):

        pp.pprint(self._ex.get_new_deposit_address(coin)
                  )

    def withdraw(self, coin, amount, address):
        '''withdraw cryptocurrency'''

        pp.pprint(self._ex.withdraw(coin, amount, str(address))
                  )

    def withdraw_history(self, coin=None):

        if not coin:
            pp.pprint(self._ex.get_withdraw_history()
                      )
        else:
            pp.pprint([i for i in self._ex.get_withdraw_history() if i['currency'] == coin.upper()]
                      )

    def balance(self, coin=None):
        '''show balances on trade account'''

        if self._ex.name == "poloniex":

            balances = {k:v for k, v in self._ex.get_balances().items() if float(v) > 0}

            if coin:
                pp.pprint(self._ex.get_balances(coin))
                return

        if self._ex.name == "bittrex":
            balances = self._ex.get_balances()

            if coin:
                pp.pprint([i for i in balances if i['Currency'] == coin.upper()])
                return

        if self._ex.name == "wex":
            balances = self._ex.get_balances()

            if coin:
                pp.pprint({k: v for k, v in balances.items() if k == coin.lower()})
                return

        pp.pprint(balances)

    def loans(self, coin):
        '''Works only with Poloniex!'''

        assert self._ex.name == 'poloniex'

        pp.pprint(self._ex.get_loans(coin))

    def ticker(self, market_pair):
        '''display basic market info like high, low and volume'''

        pp.pprint(self._ex.get_market_ticker(market_pair))


    def top(self, base_pair, top_n=15):
        '''display list of top markets, sorted by volume'''

        if self._ex.name == "bittrex":

            _sum = self._ex.get_summaries()

            markets = [i for i in _sum if i['MarketName'].split('-')[0] == base_pair.upper()]

            _filtered = [{"market": i['MarketName'], "volume": i['BaseVolume']} for i in markets]

            _sorted = sorted(_filtered, key=lambda k: k['volume'])[-top_n::]


        pp.pprint(_sorted)


def main():

    polo = Dodo(Poloniex, keys('poloniex'))
    btrx = Dodo(Bittrex, keys('bittrex'))
    wex = Dodo(Wex, keys('wex'))

    fire.Fire({
        'supported_exchanges': supported_exchanges,
        'polo': polo,
        'btrx': btrx,
        'wex': wex
    })


if __name__ == '__main__':
    main()
