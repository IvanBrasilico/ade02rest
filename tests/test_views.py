import json
import os
import sys
from base64 import b64decode
from io import BytesIO
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
        self.inspecao_modelo = {
            "IDEvento": 1001,
            "dataevento": "2019-05-28T12:18:41.204Z",
            "dataregistro": "2019-05-28T12:18:41.204Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "anexos": [
                {
                    "nomearquivo": "",
                    "content": "",
                    "contentType": "",
                    "datacriacao": "2019-05-31T02:55:50.300000+00:00",
                    "datamodificacao": "2019-05-31T02:55:50.300000+00:00"
                }
            ],
            "identificadores": [
                {
                    "identificador": "string"
                }
            ],
            "retificador": False,
            "capturaautomatica": True,
            "documentotransporte": "150",
            "numero": "TESTE1234",
            "placa": "TST1234",
            "placasemireboque": "TST5678",
            "tipodocumentotransporte": "CE"
        }
        images_dir = os.path.join(os.getcwd(), 'tests', 'images')
        self.filename = os.listdir(images_dir)[0]
        self.image = open(
            os.path.join(images_dir, self.filename), 'rb').read()
        self.file = (BytesIO(self.image), self.filename)

    def test_home(self):
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.is_json is False
        assert b'html' in response.data

    def test_inclui_inspecao(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo)
        assert r.status_code == 201
        assert r.is_json
        r = self.client.get('inspecaonaoinvasiva/1001')
        assert r.status_code == 200
        assert r.is_json
        response_json = r.json
        teste = self.inspecao_modelo
        for data in ['dataevento', 'dataregistro', 'dataoperacao', 'dataliberacao', 'dataagendamento']:
            if teste.get(data) is not None:
                teste.pop(data)
            if response_json.get(data) is not None:
                response_json.pop(data)

        self.assertDictContainsSubset(teste,
                                      response_json)

    def test_upload_invalid_file(self):
        files = {'file': (None, None, 'image/jpeg')}
        headers = {}
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'files': [files]}
        # headers['Content-Type'] = 'image/jpeg'
        response = self.client.post('upload_file',
                                    data=data,
                                    headers=headers)
        assert response.status_code == 400
        assert response.is_json is True

    def test_arquivo_invalido(self):
        file = (b'', '')
        headers = {}
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': file}
        # headers['Content-Type'] = 'image/jpeg'
        r = self.client.post('upload_file',
                             data=data,
                             headers=headers)
        assert r.status_code == 400
        assert r.is_json

    def test_evento_naoexistente(self):
        data = {'IDEvento': '100000',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': self.file}
        headers = {}
        # headers['Content-Type'] = 'image/jpeg'
        r = self.client.post('upload_file',
                             data=data,
                             content_type='multipart/form-data',
                             headers=headers)
        assert r.status_code == 404
        assert r.is_json

    def test_upload_file(self):
        # print(self.image)
        # print(self.filename)
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': self.file}
        headers = {}
        # headers['Content-Type'] = 'image/jpeg'
        r = self.client.post('upload_file',
                             data=data,
                             content_type='multipart/form-data',
                             headers=headers)
        print(r.data)
        assert r.status_code == 201
        assert r.is_json
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva'}
        r = self.client.get('get_file', data=data)
        assert r.status_code == 200
        assert r.is_json is False
        assert b64decode(r.data) == self.image
