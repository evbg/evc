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

    def get(self, collection, _id=None, where=None):
        if _id is not None:
            url = '{}/{}/{}'.format(self.api, collection, _id)
            kwargs = {'headers': self.headers}
        else:
            url = '{}/{}'.format(self.api, collection)
            kwargs = {'headers': self.headers}
            if where is not None:
                kwargs['params'] = {'where': json.dumps(where)}
        return json.loads(requests.get(url, **kwargs).text)

    def get_by_id(self, collection, _id):
        url = '{}/{}/{}'.format(self.api, collection, _id)
        return json.loads(requests.get(url).text)

    def get_items(self, collection, _id=None, where=None):
        return self.get(collection, _id, where).get('_items', [{}])

    def get_first_item(self, collection, _id=None, where=None):
        return self.get_items(collection, _id, where)[0]

    def post(self, collection, data):
        return json.loads(
            requests.post(
                '{}/{}'.format(self.api, collection),
                headers=self.headers,
                data=json.dumps(data)
            ).text
        )

    def patch(self, collection, _id, edit_tag, data):
        return json.loads(
            requests.patch(
                '{}/{}/{}'.format(self.api, collection, _id),
                headers={
                    'Content-Type': self.content_type,
                    'If-Match': edit_tag
                },
                data=json.dumps(data)
            ).text
        )

    def delete(self, collection, _id, edit_tag):
        return requests.delete(
                '{}/{}/{}'.format(self.api, collection, _id),
                headers={
                    'Content-Type': self.content_type,
                    'If-Match': edit_tag
                }
        ).text
