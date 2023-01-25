import requests
import json
from config import API_KEY, currencies


class APIException(Exception):
    pass


class Converter:
    @staticmethod
    def get_convert(curr_from, curr_to, amount):
        try:
            curr_from_key = currencies[curr_from]
        except KeyError:
            raise APIException(f'Валюта {curr_from} не найдена!\nСписок доступных валют см. /values')
        try:
            curr_to_key = currencies[curr_to]
        except KeyError:
            raise APIException(f'Валюта {curr_to} не найдена!\nСписок доступных валют см. /values')
        if curr_from_key == curr_to_key:
            raise APIException(f'Невозможно перевести одинаковые валюты {curr_from}')
        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f'Неудалось обработать количество: {amount}')

        url = f"https://api.apilayer.com/exchangerates_data/convert?to={curr_to_key}&from={curr_from_key}&amount={amount}"
        payload = {}
        headers = {"apikey": API_KEY}
        r = requests.request("GET", url, headers=headers, data=payload)
        resp = json.loads(r.content)
        result = resp['result']
        return round(result, 3)


