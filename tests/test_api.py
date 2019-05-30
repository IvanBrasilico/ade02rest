import json
import os
import sys
from unittest import TestCase

sys.path.insert(0, 'apiserver')
from apiserver.main import create_app
from apiserver.models import orm

class APITestCase(TestCase):

    def setUp(self):
        session, engine = orm.init_db('sqlite:///memory:')
        orm.Base.metadata.create_all(bind=engine)
        app = create_app(session, engine)
        self.client = app.app.test_client()
        with open(os.path.join(os.path.dirname(__file__),
                               'testes.json'), 'r') as json_in:
            self.testes = json.load(json_in)

    def test_health(self):
        response = self.client.get('/non_ecxiste')
        assert response.status_code == 404

    def test_home(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def test_api(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json=teste)
            assert rv.status_code == 201
