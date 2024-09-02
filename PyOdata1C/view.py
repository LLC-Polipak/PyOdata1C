from typing import Any, Dict, List
from urllib.parse import urlencode, quote

import requests

from .errors import throw_exception
from .serializer import Serializer


class Config:
    # ???
    username: str | None = None
    password: str | None = None
    base_url: str | None = None
    accept: str = 'application/json'

    @classmethod
    def get_auth_credentials(cls) -> tuple:
        return cls.username, cls.password

    @classmethod
    def headers(cls) -> dict:
        return {
            'accept': cls.accept
        }


class View:
    config: Config = Config
    __select_params: str | None = None
    __filter_params: str | None = None
    __expand_params: str | None = None
    serializer_class: Serializer = Serializer
    # pagination_class = OdataPagination
    url = f'{config.base_url}{serializer_class.path}'

    def select(self, params: List[str]):
        self.__select_params = ','.join(params)
        return self

    def expand(self, params: List[str]):
        self.__expand_params = ','.join(params)
        return self

    def expand_all(self):
        self.__expand_params = '*'
        return self

    def filter(self, fmt_str: str):
        self.__filter_params = fmt_str
        return self

    def get(self):
        query_params = {}
        if self.__select_params:
            query_params['$select'] = self.__select_params
        if self.__filter_params:
            query_params['$filter'] = self.__select_params
        if self.__expand_params:
            query_params['$expand'] = self.__expand_params

        encoded_query_params = urlencode(query_params, quote_via=quote)
        r = requests.get(url=self.url, params=encoded_query_params,
                         auth=self.config.get_auth_credentials(), headers=self.config.headers())
        if r.status_code != 200:
            throw_exception(r.json())


    def create(self, body: Dict[str, Any]):
        r = requests.post(self.url, data=body, auth=self.config.get_auth_credentials(), headers=self.config.headers())
        if r.status_code != 201:
            throw_exception(r.json())


