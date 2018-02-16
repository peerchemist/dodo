from urllib.request import urlopen
from datetime import datetime
import json


class Coindar:

    url = 'https://coindar.org/api/v1/'

    @classmethod
    def _filter_ru(cls, res: list) -> list:

        for i in res:
            i.pop('caption_ru')
            i.pop('proof_ru')

        return res

    @classmethod
    def _filter_passed():
        '''filter events which have passed'''
        raise NotImplementedError

    @classmethod
    def _fetch(cls, command):

        return json.loads(urlopen(cls.url + command).read())

    @classmethod
    def query_coin_events(cls, coin):
        '''query for events for <coin>'''

        res = cls._fetch('coinEvents?' + f'name={coin.lower()}')
        return cls._filter_ru(res)

    @classmethod
    def query_events(cls, month, day=None):
        '''query for events happening this month'''

        year = datetime.now().year

        q = 'events?' + f'year={year}&' + f'month={month}'
        if day:
            q += f'&day={day}'

        res = cls._fetch(q)
        return cls._filter_ru(res)
