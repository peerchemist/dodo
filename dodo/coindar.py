from urllib.request import urlopen
from datetime import datetime
import json


def to_datetime(string: str) -> datetime.strptime:
    '''convert string to datetime'''

    if len(string.split()) == 1:

        if len(string.split('-')) == 2:
            return datetime.strptime(string, '%Y-%m')

        if len(string.split('-')) == 3:
            return datetime.strptime(string, '%Y-%m-%d')

    if len(string.split()) > 0:

        return datetime.strptime(string, '%Y-%m-%d %H:%M')


class Coindar:

    url = 'https://coindar.org/api/v1/'

    @classmethod
    def _filter_ru(cls, res: list) -> list:

        for i in res:
            i.pop('caption_ru')
            i.pop('proof_ru')

        return res

    @classmethod
    def _filter_passed(cls, res: list) -> list:
        '''filter events which have passed'''

        return [i for i in res if datetime.now() <= to_datetime(i['start_date'])]

    @classmethod
    def _fetch(cls, command: str) -> list:

        return json.loads(urlopen(cls.url + command).read())

    @classmethod
    def query_coin_events(cls, coin: str) -> list:
        '''query for events for <coin>'''

        res = cls._fetch('coinEvents?' + f'name={coin.lower()}')
        res = cls._filter_ru(res)
        res = cls._filter_passed(res)

        return res

    @classmethod
    def query_events(cls, month: int, day: int=None) -> list:
        '''query for events happening this month'''

        year = datetime.now().year

        q = 'events?' + f'year={year}&' + f'month={month}'
        if day:
            q += f'&day={day}'

        res = cls._fetch(q)
        res = cls._filter_ru(res)
        res = cls._filter_passed(res)

        return res
