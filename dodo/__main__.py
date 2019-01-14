#!/usr/bin/env python

from cryptotik import (PoloniexNormalized,
                       BittrexNormalized,
                       BinanceNormalized,
                       BitstampNormalized,
                       KrakenNormalized,
                       HitbtcNormalized)

import fire
import pprint
from operator import itemgetter

from dodo.config import Settings
from dodo.keys import read_keys, set_key
from dodo.convert import Converter
from dodo.etc import (n_worth,
                      str_to_bitcoin,
                      satoshi_to_bitcoin,
                      bitcoin_to_satoshi,
                      spread_it,
                      ladder_price
                      )

supported = (PoloniexNormalized.name,
             BittrexNormalized.name, BinanceNormalized.name,
             BitstampNormalized.name, KrakenNormalized.name,
             HitbtcNormalized.name)


pp = pprint.PrettyPrinter(width=80)


def supported_exchanges():

    pp.pprint(supported)


class Dodo(object):

    def __init__(self, exchange, kwargs, settings: object) -> None:

        if settings.timeout:
            self._ex = exchange(**kwargs,
                                timeout=int(settings.timeout),
                                proxy=settings.proxy)
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

    def buy(self,
            market_pair: str,
            rate: float,
            amount: float,
            spread: float=None,
            ladder: int=None
            ) -> None:

        '''limit buy order'''

        if "sat" in str(rate):
            rate = str_to_bitcoin(rate)

        if spread:

            if "sat" in str(spread):
                spread = str_to_bitcoin(spread)

            _ladder = spread_it(bitcoin_to_satoshi(rate),
                                bitcoin_to_satoshi(spread),
                                ladder)
            _amounts = ladder_price(amount, ladder)

            for r, a in zip(_ladder, _amounts):
                pp.pprint(
                    self._ex.buy_limit(market_pair,
                                       satoshi_to_bitcoin(r),
                                       a)
                )

        else:
            pp.pprint(self._ex.buy_limit(market_pair, rate, amount)
                      )

    def buy_market(self, pair, amount):
        '''buys at market price'''

        assert self._ex.name in ("bitstamp", "binance", "kraken"), {'error': 'this only works with Bitstamp, Kraken and Binance.'}

        pp.pprint(self._ex.buy_market(pair=pair, amount=amount))

    def buy_worth(self, market_pair: str, target_price: str, amount: float) -> None:
        '''Buy <amount> of base pair worth at <target price>
        : dodo btrx buy btc-xrp 2400sat 1btc'''

        if "sat" in str(target_price):
            target_price = str_to_bitcoin(target_price)

        amount = n_worth(amount, target_price, market_pair, self._ex)

        pp.pprint(self._ex.buy_limit(market_pair, target_price, amount)
                  )

    def long(self, market_pair: str,
             rate: float,
             amount: float,
             leverage: int=None,
             max_lending_rate: float=0.5) -> None:
        '''execute leveraged buy order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price
        : amount - quantity of coin to long buy
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        if "sat" in str(rate):
            rate = str_to_bitcoin(rate)

        if self._ex.name == "poloniex":

            pp.pprint(self._ex.buy_margin(market_pair, rate, amount,
                      max_lending_rate)
                      )

        if self._ex.name == "kraken":

            pp.pprint(self._ex.buy_limit(pair=market_pair,
                                         rate=rate,
                                         amount=amount,
                                         leverage=leverage)
                      )

    def sell(self,
             market_pair: str,
             rate: float,
             amount: float,
             spread: float=None,
             ladder: int=None
             ) -> None:
        '''limit sell order'''

        if "sat" in str(rate):
            rate = str_to_bitcoin(rate)

        if spread:

            if "sat" in str(spread):
                spread = str_to_bitcoin(spread)

            _ladder = spread_it(bitcoin_to_satoshi(rate),
                                bitcoin_to_satoshi(spread),
                                ladder)
            _amounts = ladder_price(amount, ladder)

            for r, a in zip(_ladder, _amounts):
                pp.pprint(
                    self._ex.sell_limit(market_pair,
                                        satoshi_to_bitcoin(r),
                                        a)
                )

        else:
            pp.pprint(self._ex.sell_limit(market_pair, rate, amount)
                      )

    def sell_market(self, pair, amount):
        '''bitstamp specific method, sells at market price'''

        assert self._ex.name in ("bitstamp", "binance", "kraken"), {'error': 'this only works with Bitstamp, Kraken and Binance.'}

        pp.pprint(self._ex.sell_market(pair, amount))

    def short(self, market_pair: str,
              rate: float,
              amount: float,
              leverage: int=None,
              max_lending_rate: float=0.5) -> None:
        '''execute leveraged sell order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price
        : amount - quantity of coin to short sell
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        if "sat" in str(rate):
            rate = str_to_bitcoin(rate)

        if self._ex.name == "poloniex":

            pp.pprint(self._ex.sell_margin(market_pair, rate, amount,
                      max_lending_rate)
                      )

        if self._ex.name == "kraken":

            pp.pprint(self._ex.sell_limit(pair=market_pair,
                                          rate=rate,
                                          amount=amount,
                                          leverage=leverage)
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

        if address in Settings.alias:
            address = Settings.alias[address]

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


def ratio(c1, c2):

    pp.pprint(Converter.convert(c1, c2))


def convert(coin1, quantity, coin2):

    ratio = Converter.convert(coin1, coin2)

    pp.pprint(quantity * ratio[coin2.upper()])


def main():

    polo = Dodo(PoloniexNormalized, read_keys('poloniex'), settings=Settings)
    btrx = Dodo(BittrexNormalized, read_keys('bittrex'), settings=Settings)
    bnb = Dodo(BinanceNormalized, read_keys('binance'), settings=Settings)
    stamp = Dodo(BitstampNormalized, read_keys('bitstamp'), settings=Settings)
    kraken = Dodo(KrakenNormalized, read_keys('kraken'), settings=Settings)
    hitbtc = Dodo(HitbtcNormalized, read_keys('hitbtc'), settings=Settings)

    fire.Fire({
        'setup': set_key,
        'supported_exchanges': supported_exchanges,
        'polo': polo,
        'btrx': btrx,
        'bnb': bnb,
        'stamp': stamp,
        'kraken': kraken,
        'hitbtc': hitbtc,
        'ratio': ratio,
        'convert': convert
    })


if __name__ == '__main__':
    main()
