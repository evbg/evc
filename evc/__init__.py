# -*- coding: utf-8 -*-

import requests
import simplejson as json

__all__ = ['Evc']


class Evc(object):

    def __init__(self,
                 api='http://127.0.0.1:5005',
                 content_type='application/json'):
        self.api = api
        self.content_type = content_type
        self.headers = {'Content-Type': content_type}
        self.response = None

    def __return(self, return_json=True):
        if return_json:
            try:
                return self.response.json()
            except ValueError:
                return None
        else:
            return self.response.text

    def get(self, collection, _id=None, where=None):
        kwargs = {'headers': self.headers}
        if _id is not None:
            url = '{}/{}/{}'.format(self.api, collection, _id)
        else:
            url = '{}/{}'.format(self.api, collection)
            if where is not None:
                kwargs['params'] = {'where': json.dumps(where)}
        self.response = requests.get(url, **kwargs)
        return self.__return()

    def get_items(self, collection, where=None):
        return self.get(collection, where=where).get('_items', [{}])

    def post(self, collection, data):
        self.response = requests.post(
            '{}/{}'.format(self.api, collection),
            headers=self.headers,
            data=json.dumps(data)
        )
        return self.__return()

    def patch(self, collection, _id, edit_tag, data):
        self.response = requests.patch(
            '{}/{}/{}'.format(self.api, collection, _id),
            headers={
                'Content-Type': self.content_type,
                'If-Match': edit_tag
            },
            data=json.dumps(data)
        )
        return self.__return()

    def upsert(self, collection, where, data):
        res = self.get(collection, where=where)
        if self.response.status_code == 200:
            total = res.get('_meta', {}).get('total', None)
            if total == 1:
                item = res['_items'][0]
                _id = item['_id']
                _etag = item['_etag']
                return self.patch(collection, _id, _etag, data)
            elif total == 0:
                return self.post(collection, data)
            else:
                self.response = None
                return None

    def delete(self, collection, _id, edit_tag):
        self.response = requests.delete(
            '{}/{}/{}'.format(self.api, collection, _id),
            headers={
                'Content-Type': self.content_type,
                'If-Match': edit_tag
            }
        )
        return self.__return(return_json=False)
