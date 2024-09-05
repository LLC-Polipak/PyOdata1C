from typing import Any, Dict, List
from urllib.parse import urlencode, quote

import requests

from PyOdata1C.errors import throw_exception
from PyOdata1C.serializer import Serializer


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
    config: Config = None
    __select_params: str | None = None
    __filter_params: str | None = None
    __expand_params: str | None = None
    __top: int | None = None
    __skip: int | None = None
    serializer_class: Serializer | None = None

    @classmethod
    def _url(cls):
        return f'{cls.config.base_url}{cls.serializer_class.path}'

    def select(self, params: List[str] | None = None):
        if params:
            self.__select_params = ','.join(params)
        else:
            self.__select_params = ','.join(self.serializer_class.get_select())
        return self

    def expand(self, params: List[str] | None = None):
        if self.__expand_params:
            self.__expand_params = ','.join(params)
        else:
            self.__expand_params = ','.join(self.serializer_class.get_expand())
        return self

    def top(self, num: int):
        self.__top = num
        return self

    def skip(self, num: int):
        self.__skip = num
        return self

    def expand_all(self):
        self.__expand_params = '*'
        return self

    def filter(self, fmt_str: str):
        self.__filter_params = fmt_str
        return self

    def _configure_query_params(self):
        query_params = {}
        if self.__select_params:
            query_params['$select'] = self.__select_params
        if self.__filter_params:
            query_params['$filter'] = self.__filter_params
        if self.__expand_params:
            query_params['$expand'] = self.__expand_params
        if self.__top:
            query_params['$top'] = self.__top
        if self.__skip:
            query_params['$skip'] = self.__skip
        return urlencode(query_params, quote_via=quote)

    def get(self):
        r = requests.get(url=self._url(), params=self._configure_query_params(),
                         auth=self.config.get_auth_credentials(), headers=self.config.headers())
        if r.status_code != 200:
            throw_exception(r.json())
        data = r.json()['value']
        return self.serializer_class.deserialize(data)

    def create(self, body: Dict[str, Any]):
        r = requests.post(self._url(), data=body, auth=self.config.get_auth_credentials(), headers=self.config.headers())
        if r.status_code != 201:
            throw_exception(r.json())
