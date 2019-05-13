# -*- coding: utf-8 -*-

import time
import unittest
from multiprocessing import Process
from uuid import uuid4

import six
from evc import Evc
from eve import Eve
from pymongo import MongoClient

if six.PY3:
    from functools import reduce


def map2(*args, **kwargs):
    if six.PY3:
        return [x for x in map(*args, **kwargs)]
    return map(*args, **kwargs)


class TestEvc(unittest.TestCase):

    port = 5135
    collection = 'users'
    mongo_dbname = 'evc_test_{}'.format(uuid4())
    wait = 0.1
    print_success_asserts = True

    post_ids = []

    @classmethod
    def setUpClass(cls):
        settings = {}
        settings['SERVER_NAME'] = '127.0.0.1:{}'.format(cls.port)
        settings['MONGO_DBNAME'] = cls.mongo_dbname
        settings['RESOURCE_METHODS'] = ['GET', 'POST', 'DELETE']
        settings['ITEM_METHODS'] = ['GET', 'PATCH', 'PUT', 'DELETE']
        settings['DOMAIN'] = {
            cls.collection: {'versioning': True, 'allow_unknown': True, 'schema': {}}
        }
        eve_service = Eve(settings=settings)
        cls.p = Process(target=eve_service.run)
        print('=' * 70)
        print('sleep({})'.format(cls.wait))
        cls.p.start()
        time.sleep(cls.wait)
        print('=' * 70)

    @classmethod
    def tearDownClass(cls):
        cls.p.terminate()
        try:
            MongoClient().drop_database(cls.mongo_dbname)
            print("Removed test database: {}".format(cls.mongo_dbname))
        except (Exception):
            print("Could not connect to MongoDB")

    def _assertsIn(self, response, attrs):
        def assertIn_response(x):
            ret = self.assertIn(x, response)
            if self.print_success_asserts:
                print('{} in {}'.format(x, response))
            return ret

        map2(assertIn_response, attrs)

    def setUp(self):
        self.evc = Evc('http://127.0.0.1:{}'.format(self.port))

        self.get_attrs = """

        _id
        _etag
        _created
        _updated
        _version
        _latest_version
        _links

        """.split()

        self.post_attrs = (
            self.get_attrs
            + """

        _status

        """.split()
        )

        self.patch_attrs = self.post_attrs
        self.update_attrs = self.post_attrs

        self.upsert_attrs = (
            self.post_attrs
            + """

        _upsert_method

        """.split()
        )

        update_asserts = [
            lambda response: self.assertIsInstance(response, dict),
            lambda response: self.assertNotEquals(response, {}),
            lambda response: self._assertsIn(response, self.update_attrs),
        ]

        delete_asserts = [lambda response: self.assertEqual(response, '')]

        self.post_data = [
            {'data': {'name': 'Alis', 'age': 20}},
            {
                'data': {'name': 'Bob', 'age': 23},
                'patches': [
                    {'data': {'email': 'bob1@bobmail.com'}},
                    {'data': {'email': 'bob2@bobmail.com'}},
                    {'data': {'email': 'bob3@bobmail.com'}},
                    {'data': {'email': 'bob4@bobmail.com'}},
                ],
            },
        ]

        self.upsert_data = [
            {
                'where': {'name': 'Alis'},
                'data': {'name': 'Alis', 'age': 30},
                'asserts': update_asserts,
            },
            {
                'where': {'name': 'Bob'},
                'data': {'name': 'Bob', 'age': 33},
                'asserts': update_asserts,
            },
            {
                'where': {'name': 'Carl'},
                'data': {'name': 'Carl', 'age': 40},
                'asserts': update_asserts,
            },
            {
                'where': {'name': 'Carl'},
                'data': {'name': 'Carl', 'age': 50},
                'asserts': update_asserts,
            },
            {
                'where': {'name': 'Carl'},
                'data': {'name': 'Carl', 'age': 60},
                'asserts': update_asserts,
            },
            {
                'where': {'name': 'Dan'},
                'data': {'name': 'Dan', 'age': 51},
                'asserts': update_asserts,
            },
            {'where': {'name': 'Dan'}, 'data': {}, 'asserts': delete_asserts},
        ]

    def tearDown(self):
        del self.evc

    def post_asserts(self, response):
        post_attrs = self.post_attrs

        assertIsInstance = self.assertIsInstance
        assertEqual = self.assertEqual
        assertNotEqual = self.assertNotEqual

        assertIsInstance(response, dict)
        assertNotEqual(response, {})

        self._assertsIn(response, post_attrs)

        _id = response.get('_id', None)
        _etag = response.get('_etag', None)
        _status = response.get('_status', None)
        _latest_version = response.get('_latest_version', None)
        _created = response.get('_created', None)
        _updated = response.get('_updated', None)

        assertEqual(len(_id), 24)
        assertEqual(len(_etag), 40)
        assertEqual(_status, 'OK')
        assertEqual(_latest_version, 1)
        assertEqual(_created, _updated)

    def patch_asserts(self, response):
        collection = self.collection
        post_attrs = self.post_attrs

        assertIsInstance = self.assertIsInstance
        assertEqual = self.assertEqual
        assertNotEqual = self.assertNotEqual
        assertIn = self.assertIn

        assertIsInstance(response, dict)
        assertNotEqual(response, {})

        self._assertsIn(response, post_attrs)

        _id = response.get('_id', None)
        _etag = response.get('_etag', None)
        _status = response.get('_status', None)
        _links = response.get('_links', None)
        # _latest_version = response.get('_latest_version', None)
        _created = response.get('_created', None)
        _updated = response.get('_updated', None)

        assertEqual(len(_id), 24)
        assertEqual(len(_etag), 40)
        assertEqual(_status, 'OK')
        assertIn('self', _links)
        assertIn(collection, _links.get('self', {}).get('href', ''))
        href = _links.get('self', {}).get('href', '')
        assertEqual('{}/{}'.format(collection, _id), href)
        # to fix: _latest_version == 2 for first patch only
        # assertEqual(_latest_version, 2)
        assertNotEqual(_created, _updated)

    def test_010_post_and_patch(self):
        evc = self.evc
        collection = self.collection
        post_ids = self.post_ids
        post_data = self.post_data

        def _post(post_data):
            response = evc.post(collection, post_data['data'])
            self.post_asserts(response)
            _id = response.get('_id', None)
            _etag = response.get('_etag', None)

            patch_data_list = post_data.get('patches', [])
            if patch_data_list:

                def _patch(_etag, patch_data):
                    time.sleep(1)
                    response = evc.patch(collection, _id, _etag, patch_data['data'])
                    self.patch_asserts(response)
                    _patch_id = response.get('_id', None)
                    post_ids.append(_patch_id)
                    _etag = response.get('_etag', None)
                    return _etag

                reduce(_patch, patch_data_list, _etag)
            else:
                post_ids.append(_id)

        map2(_post, post_data)

    def test_020_get_default(self):
        evc = self.evc
        assertIsInstance = self.assertIsInstance
        assertNotEqual = self.assertNotEqual
        assertEqual = self.assertEqual
        assertIsNotNone = self.assertIsNotNone
        collection = self.collection

        response = evc.get()
        assertIsInstance(response, dict)
        assertNotEqual(response, {})

        _links = response.get('_links', None)
        assertIsNotNone(_links)
        assertIsInstance(_links, dict)

        child = _links.get('child', None)
        assertIsNotNone(child)
        assertIsInstance(child, list)
        assertEqual(child, [{'href': collection, 'title': collection}])

    def test_021_get(self):
        evc = self.evc
        collection = self.collection
        assertIsInstance = self.assertIsInstance
        assertNotEqual = self.assertNotEqual
        assertIn = self.assertIn
        attrs = """

        _items
        _meta
        _links

        """.split()

        response = evc.get(collection)
        assertIsInstance(response, dict)
        assertNotEqual(response, {})

        def assertIn_response(x):
            return assertIn(x, response)

        map2(assertIn_response, attrs)

        items = response.get('_items', [])
        assertNotEqual(items, [])

    def test_022_get_by_id(self):
        evc = self.evc
        assertEqual = self.assertEqual
        assertIn = self.assertIn
        collection = self.collection
        post_ids = self.post_ids
        post_data = self.post_data
        get_attrs = self.get_attrs

        def _get_by_id(n):
            response = evc.get_by_id(collection, post_ids[n])

            def assertIn_response(x):
                return assertIn(x, response)

            map2(assertIn_response, get_attrs)

            doc = post_data[n]['data']
            for key in doc:
                assertEqual(response.get(key, 1), doc.get(key, 2))

        map2(_get_by_id, range(len(self.post_data)))

    def test_023_get_items(self):
        evc = self.evc
        response = evc.get_items(self.collection)
        self.assertIsInstance(response, list)
        self.assertNotEqual(response, [])
        self.assertEqual(len(response), len(self.post_data))

    def test_024_get_first_item(self):
        evc = self.evc
        collection = self.collection
        assertIsInstance = self.assertIsInstance
        assertEqual = self.assertEqual
        assertNotEqual = self.assertNotEqual
        post_data = self.post_data

        response = evc.get_first_item(collection)
        assertIsInstance(response, dict)
        assertNotEqual(response, {})
        data = post_data[0]['data']
        for key in data:
            assertEqual(response.get(key, 1), data.get(key, 2))

    def test_030_upsert(self):
        evc = self.evc
        collection = self.collection

        def _upsert(item):
            where, data = item.get('where', None), item.get('data', None)
            response = evc.upsert(collection, where, data)
            asserts = item.get('asserts', [])
            map2(lambda _assert: _assert(response), asserts)

        map2(_upsert, self.upsert_data)

    def test_990_delete_all(self):
        evc = self.evc
        collection = self.collection
        assertIsInstance = self.assertIsInstance
        assertEqual = self.assertEqual
        assertNotEqual = self.assertNotEqual
        assertIn = self.assertIn

        response = evc.get(collection)
        assertIsInstance(response, dict)
        assertNotEqual(response, {})
        assertIn('_items', response)

        _items = response.get('_items', [])

        def delete(item):
            _id = item.get('_id', None)
            _etag = item.get('_etag', None)
            return evc.delete(collection, _id, _etag)

        result = map2(delete, _items)
        assertEqual([x for x in filter(lambda x: x != '', result)], [])

        response = evc.get_items(collection)
        assertEqual(response, [])
