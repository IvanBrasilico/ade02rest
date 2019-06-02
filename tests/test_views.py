import json
import os
import sys
from unittest import TestCase

sys.path.insert(0, 'apiserver')
from apiserver.main import create_app

from apiserver.models import orm


def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])


class ViewTestCase(TestCase):

    def setUp(self):
        session, engine = orm.init_db('sqlite:///:memory:')
        orm.Base.metadata.create_all(bind=engine)
        app = create_app(session, engine)
        self.client = app.app.test_client()
        with open(os.path.join(os.path.dirname(__file__),
                               'testes.json'), 'r') as json_in:
            self.testes = json.load(json_in)

    def test_home(self):
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.is_json is False
        assert b'html' in response.data


    def test_upload_invalid_file(self):
        files = {'file': (None, None, 'image/jpeg')}
        headers = {}
        data = {'IDEvento': 0, 'tipoevento': 'InspecaonaoInvasiva'}
        # headers['Content-Type'] = 'image/jpeg'
        response = self.client.post('upload_file',
                          data=data,
                          files=files,
                          headers=headers)
        assert response.status_code == 200
        assert response.is_json is True
