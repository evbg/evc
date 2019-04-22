# -*- coding: utf-8 -*-

import requests
try:
    import simplejson as json
except ImportError:
    import json

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

    def get(self, *args, **kwargs):

        kwargs_allowed = ('where', 'max_results', 'page', 'version', 'sort')

        def get_kwarg(key):
            kwarg = kwargs.get(key, None)
            if type(kwarg) is dict:
                return json.dumps(kwarg)
            else:
                return kwarg

        if not args:
            url = '{}'.format(self.api)
            self.response = requests.get(url)
            return self.__return()
        else:
            collection = args[0]

        kwargs_req = {'headers': self.headers}
        _id = kwargs.get('_id', None)
        if _id is not None:
            url = '{}/{}/{}'.format(self.api, collection, _id)
        else:
            url = '{}/{}'.format(self.api, collection)
        params = dict((k, v) for (k, v) in
                      map(lambda x: (x, get_kwarg(x)), kwargs_allowed)
                      if v is not None)
        if params != {}:
            kwargs_req['params'] = params
        self.response = requests.get(url, **kwargs_req)
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

    def upsert(self, collection, where, data, insert=True):
        res = self.get(collection, where=where)
        if self.response.status_code == 200:
            total = res.get('_meta', {}).get('total', None)
            if total == 1:
                item = res['_items'][0]
                _id = item['_id']
                _etag = item['_etag']
                if not data:
                    return self.delete(collection, _id, _etag)
                else:
                    return self.patch(collection, _id, _etag, data)
            elif total == 0:
                if insert:
                    return self.post(collection, data)
                else:
                    #  Return 404 (HTTP status code) with response from Eve
                    return self.patch(collection, None, None, None)
        else:
            return res

    def update(self, *args, **kwargs):
        kwargs['insert'] = False
        return self.upsert(*args, **kwargs)

    def delete(self, collection, _id, edit_tag):
        self.response = requests.delete(
            '{}/{}/{}'.format(self.api, collection, _id),
            headers={
                'Content-Type': self.content_type,
                'If-Match': edit_tag
            }
        )
        return self.__return(return_json=False)
