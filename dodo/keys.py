import keyring

_key_prefix = 'dodo'
_secret_delimiter = '<\/&>'


def init_keyring(exchanges: list) -> None:
    '''fill the keyring with empty strings, as placeholder'''

    for i in exchanges:
        set_key(i, '', '')


def set_key(exchange: str, api: str, secret: str, id: str=None) -> None:
    '''set api/key for exchange'''

    print('Please use full name of the exchange (ie. bittrex).')

    if id:  # edge case for Bitstamp
        keyring.set_password(_key_prefix, exchange.lower(), api +
                             _secret_delimiter + secret +
                             _secret_delimiter + str(id))
    else:
        keyring.set_password(_key_prefix,
                             exchange.lower(), api + _secret_delimiter
                             + secret)


def read_keys(exchange: str) -> dict:
    '''load keys from the keystore'''

    try:
        if exchange is not "bitstamp":
            apikey, secret = keyring.get_password('dodo', exchange).split(_secret_delimiter)
            return {'apikey': apikey, 'secret': secret}
        else:
            apikey, secret, id = keyring.get_password('dodo', exchange).split(_secret_delimiter)
            return {'apikey': apikey, 'secret': secret, 'customer_id': id}

    except AttributeError:
        #print({'error': 'No secret entry for {0}.'.format(exchange)})
        return {'apikey': '', 'secret': ''}
