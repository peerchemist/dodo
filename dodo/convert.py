from urllib.request import urlopen
import json


class Converter:

    url = "https://min-api.cryptocompare.com/data/price?"

    @classmethod
    def _fetch(cls, command: str) -> list:

        return json.loads(urlopen(cls.url + command).read())

    @classmethod
    def convert(cls, c1: str, c2: str) -> dict:
        '''convert from coin to coin'''

        return cls._fetch('fsym={c1}&tsyms={c2}'.format(c1=c1.upper(),
                                                        c2=c2.upper())
                                                         )
