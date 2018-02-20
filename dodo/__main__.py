#!/usr/bin/env python

from cryptotik import Wex, Poloniex, Bittrex, Binance, Bitstamp, Kraken
from cryptotik.common import ExchangeWrapper
import fire
import keyring
from dodo.config import Settings
import pprint
from operator import itemgetter
from datetime import datetime
from dodo.coindar import Coindar
from dodo.etc import n_worth, satoshi_to_bitcoin

supported = (Wex.name, Poloniex.name, Bittrex.name, Binance.name, Bitstamp.name, Kraken)
_secret_delimiter = '<\/&>'
pp = pprint.PrettyPrinter(width=80, compact=True)


def supported_exchanges():

    pp.pprint(supported)


def set_key(exchange: str, api: str, secret: str, id: str=None) -> None:
    '''set api/key for exchange'''

    print('Please use full name of the exchange (ie. bittrex).')

    if id:  # edge case for Bitstamp
        keyring.set_password("dodo", exchange.lower(), api +
                             _secret_delimiter + secret + _secret_delimiter + str(id))
    else:
        keyring.set_password("dodo", exchange.lower(), api + _secret_delimiter + secret)


def keys(exchange: str) -> dict:
    '''load keys from the keystore'''

    try:
        if exchange is not "bitstamp":
            apikey, secret = keyring.get_password('dodo', exchange).split(_secret_delimiter)
            return {'apikey': apikey, 'secret': secret}
        else:
            apikey, secret, id = keyring.get_password('dodo', exchange).split(_secret_delimiter)
            return {'apikey': apikey, 'secret': secret, 'customer_id': id}

    except AttributeError:
        print({'error': 'No secret entry for {0}.'.format(exchange)})


class Dodo(object):

    def __init__(self, exchange, kwargs, settings: object) -> None:

        if settings.timeout:
            self._ex = exchange(**kwargs,
                                timeout=int(settings.timeout), proxy=settings.proxy)
        else:
            self._ex = exchange(**kwargs,
                                proxy=settings.proxy)       

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

        if "sat" in str(rate):
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.buy_limit(market_pair, rate, amount)
                  )

    def buy_market(self, pair, amount):
        '''bitstamp specific method, buys at market price'''

        assert self._ex.name in ("bitstamp", "binance"), {'error': 'this only works with Bitstamp and Binance.'}

        pp.pprint(self._ex.buy_market(pair, amount))

    def buy_worth(self, market_pair: str, target_price: str, amount: float) -> None:
        '''Buy <amount> of base pair worth at <target price>
        : dodo btrx buy btc-xrp 2400sat 1btc'''

        if "sat" in str(target_price):
            target_price = satoshi_to_bitcoin(target_price)

        amount = n_worth(amount, target_price, market_pair, self._ex)

        pp.pprint(self._ex.buy_limit(market_pair, target_price, amount)
                  )

    def buy_margin(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged buy order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to long buy
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self._ex.name == "poloniex"

        if "sat" in str(rate):
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.buy_margin(market_pair, rate, amount,
                  max_lending_rate)
                  )

    def sell(self, market_pair, rate, amount):

        if "sat" in str(rate):
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.sell_limit(market_pair, rate, amount)
                  )

    def sell_market(self, pair, amount):
        '''bitstamp specific method, sells at market price'''

        assert self._ex.name in ("bitstamp", "binance"), {'error': 'this only works with Bitstamp and Binance.'}

        pp.pprint(self._ex.sell_market(pair, amount))

    def sell_margin(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged sell order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to short sell
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self._ex.name == "poloniex"

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self._ex.sell_margin(market_pair, rate, amount,
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

    def withdraw(self, coin, amount, address, name=None, tag=None):
        '''withdraw cryptocurrency'''

        if not tag:
            pp.pprint(self._ex.withdraw(coin, amount, str(address)))
        else:
            pp.pprint(self._ex.withdraw(coin, amount, str(address), str(tag)))

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

        if self._ex.name == 'binance':
            balances = self._ex.get_balances()

            if coin:
                pp.pprint([i for i in balances if coin.upper() in i['asset']])
                return

        if self._ex.name == "bitstamp":
            balances = self._ex.get_balances(coin)

        if self._ex.name == "kraken":
            balances = self._ex.get_balances()

            if coin:
                pp.pprint(balances[coin.upper()])
                return

        pp.pprint(balances)

    def loans(self, coin):
        '''Works only with Poloniex!'''

        assert self._ex.name == 'poloniex'

        pp.pprint(self._ex.get_loans(coin))

    def ticker(self, market_pair):
        '''display basic market info like high, low and volume'''

        pp.pprint(self._ex.get_market_ticker(market_pair))

    def top(self, base_pair='btc', top_n=15):
        '''display list of top markets, sorted by volume'''

        if self._ex.name == "bittrex":

            _sum = self._ex.get_summaries()

            markets = [i for i in _sum if i['MarketName'].split('-')[0] == base_pair.upper()]

            _filtered = [{"market": i['MarketName'], "volume": i['BaseVolume']} for i in markets]

            _sorted = sorted(_filtered, key=lambda k: k['volume'])[-top_n::]

            pp.pprint(_sorted)

        if self._ex.name == "binance":

            _sum = self._ex.get_summaries()

            markets = [i for i in _sum if base_pair.upper() in i['symbol']]

            _filtered = [{"market": i['symbol'], "volume": float(i['quoteVolume'])} for i in markets]

            _filtered.sort(key=itemgetter('volume'))

            pp.pprint(_filtered[-top_n::])


def events(month=datetime.now().month, day=None, coin=None):
    '''print out events'''

    if coin:
        pp.pprint(Coindar.query_coin_events(coin)[::-1])
        return
    if day:
        pp.pprint(Coindar.query_events(month, day)[::-1])
        return
    else:
        pp.pprint(Coindar.query_events(month)[::-1])
        return


def main():

    polo = Dodo(Poloniex, keys('poloniex'), settings=Settings)
    btrx = Dodo(Bittrex, keys('bittrex'), settings=Settings)
    wex = Dodo(Wex, keys('wex'), settings=Settings)
    bnb = Dodo(Binance, keys('binance'), settings=Settings)
    stamp = Dodo(Bitstamp, keys('bitstamp'), settings=Settings)
    kraken = Dodo(Kraken, keys('kraken'), settings=Settings)

    fire.Fire({
        'supported_exchanges': supported_exchanges,
        'polo': polo,
        'btrx': btrx,
        'wex': wex,
        'bnb': bnb,
        'stamp': stamp,
        'kraken': kraken,
        'events': events
    })


if __name__ == '__main__':
    main()
