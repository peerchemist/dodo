#!/usr/bin/env python

from cryptotik import Wex, Poloniex, Bittrex
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


class Dodo(object):

    def __init__(self, exchange, secret):
        self.ex = exchange(secret[0], secret[1], timeout=5)

    def markets(self):

        pp.pprint(self.ex.get_markets()
                  )

    def depth(self, market_pair):

        pp.pprint(self.ex.get_market_depth(market_pair)
                  )

    def spread(self, market_pair):

        pp.pprint(self.ex.get_market_spread(market_pair)
                  )

    def volume(self, market_pair):

        pp.pprint(self.ex.get_market_volume(market_pair)
                  )

    def buy(self, market_pair, rate, amount):

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self.ex.buy(market_pair, rate, amount)
                  )

    def margin_buy(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged buy order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to long buy
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self.ex.name == "poloniex"

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self.ex.margin_buy(market_pair, rate, amount,
                  max_lending_rate)
                  )

    def sell(self, market_pair, rate, amount):

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self.ex.sell(market_pair, rate, amount)
                  )

    def margin_sell(self, market_pair, rate, amount, max_lending_rate=1):
        '''execute leveraged sell order
        : market_pair - [btc-xmr, btc-doge, btc-xrp, ...]
        : rate - market price, expressed in Bitcoin or satoshis
        : amount - quantity of coin to short sell
        : max_lending_rate - maximum accepted lending rate (1% by default)'''

        assert self.ex.name == "poloniex"

        if "sat" in rate:
            rate = satoshi_to_bitcoin(rate)

        pp.pprint(self.ex.margin_sell(market_pair, rate, amount,
                  max_lending_rate)
                  )

    def orders(self, market_pair=None):
        '''show open orders'''

        if market_pair:
            pp.pprint(self.ex.get_open_orders(market_pair)
                      )

        else:
            if self.ex.name == "poloniex":
                pp.pprint({k: v for k, v in self.ex.get_open_orders().items() if v}
                          )
            else:
                pp.pprint(self.ex.get_open_orders())

    def cancel_order(self, order_id):
        '''cancel order <id>'''

        pp.pprint(self.ex.cancel_order(order_id))

    def deposit(self, coin, new=None):
        '''show deposit address for <coin>
        : new - generate new deposit address before printing it out. [works only with poloniex.]'''

        if new and self.ex.name == "poloniex":
            print('Requesting for new deposit address...')
            print(self.ex.get_new_deposit_address(coin))

        pp.pprint(self.ex.get_deposit_address(coin))

    def deposit_history(self, coin=None):

        if not coin:
            pp.pprint(self.ex.get_deposit_history()
                      )
        else:
            pp.pprint([i for i in self.ex.get_deposit_history() if i['currency'] == coin.upper()]
                      )

    def new_deposit_address(self, coin):

        pp.pprint(self.ex.get_new_deposit_address(coin)
                  )

    def withdraw(self, coin, amount, address):
        '''withdraw cryptocurrency'''

        pp.pprint(self.ex.withdraw(coin, amount, address)
                  )

    def withdraw_history(self, coin=None):

        if not coin:
            pp.pprint(self.ex.get_withdraw_history()
                      )
        else:
            pp.pprint([i for i in self.ex.get_withdraw_history() if i['currency'] == coin.upper()]
                      )

    def balance(self, coin=None):
        '''show balances on trade account'''

        if self.ex.name == "poloniex":

            balances = {k:v for k, v in self.ex.get_balances().items() if float(v) > 0}

            if coin:
                pp.pprint(self.ex.get_balances(coin))
                return

        if self.ex.name == "bittrex":
            balances = self.ex.get_balances()

            if coin:
                pp.pprint([i for i in balances if i['Currency'] == coin.upper()])
                return

        if self.ex.name == "wex":
            balances = self.ex.get_balances()

            if coin:
                pp.pprint({k: v for k, v in balances.items() if k == coin.lower()})
                return

        pp.pprint(balances)

    def loans(self, coin):
        '''Works only with Poloniex!'''

        assert self.ex.name == 'poloniex'

        pp.pprint(self.ex.get_loans(coin))

    def ticker(self, market_pair):
        '''display basic market info like high, low and volume'''

        pp.pprint(self.ex.get_market_ticker(market_pair))


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
