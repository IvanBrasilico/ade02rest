import json
import os
import sys
from unittest import TestCase

sys.path.insert(0, 'apiserver')
from apiserver.main import create_app

from apiserver.models import orm


def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])


class APITestCase(TestCase):

    def setUp(self):
        session, engine = orm.init_db('sqlite:///:memory:')
        orm.Base.metadata.create_all(bind=engine)
        app = create_app(session, engine)
        self.client = app.app.test_client()
        with open(os.path.join(os.path.dirname(__file__),
                               'testes.json'), 'r') as json_in:
            self.testes = json.load(json_in)

    def test_health(self):
        response = self.client.get('/non_ecxiste')
        assert response.status_code == 404


    def test1_evento_invalido_400(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json={'IDEEvento': 1})
            assert rv.status_code == 400
            assert rv.is_json is True
            rv = self.client.get(classe.lower() + '/1')
            assert rv.status_code == 404
            assert rv.is_json is True

    def test2_evento_nao_encontrado_404(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.get(classe.lower() + '/1')
            assert rv.status_code == 404
            assert rv.is_json is True

    def test3_api(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json=teste)
            assert rv.status_code == 201
            assert rv.is_json is True
            response_token = rv.json
            rv = self.client.get(classe.lower() + '/' + str(teste['IDEvento']))
            assert rv.status_code == 200
            assert rv.is_json is True
            response_json = rv.json
            for data in ['dataevento', 'dataregistro', 'dataoperacao', 'dataliberacao', 'dataagendamento']:
                if teste.get(data) is not None:
                    teste.pop(data)
                if response_json.get(data) is not None:
                    response_json.pop(data)
            sub_response = extractDictAFromB(teste, response_json)
            self.maxDiff = None
            # self.assertEqual(teste, sub_response)
            self.assertDictContainsSubset(teste, sub_response)
            # self.assertEqual(response_json, sub_teste)


    def test4_evento_duplicado_409(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json=teste)
            assert rv.status_code == 409
            assert rv.is_json is True
