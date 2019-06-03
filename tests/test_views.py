import datetime
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
        self.engine = engine
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

    def tearDown(self) -> None:
        orm.Base.metadata.drop_all(bind=self.engine)

    def test0_home(self):
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.is_json is False
        assert b'html' in response.data

    def test1_inclui_inspecao(self):
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

    def test2_upload_invalid_file(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo)
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

    def test3_arquivo_invalido(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo)
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

    def test4_evento_naoexistente(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo)
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
        assert r.is_json is True

    def test5_upload_file(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo)
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
        if r.data is not None:
            assert b64decode(r.data) == self.image

    def test_eventos_list(self):
        posicaoconteiner = {
            "dataevento": "2019-05-24T16:48:21.245Z",
            "dataregistro": "2019-05-24T16:48:21.245Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "retificador": False,
            "altura": 0,
            "emconferencia": True,
            "numero": "string",
            "placa": "string",
            "posicao": "string",
            "solicitante": "RFB"
        }
        for r in range(2):
            posicaoconteiner['IDEvento'] = 10000 + r
            posicaoconteiner['altura'] = r
            r = self.client.post('posicaoconteiner',
                                 json=posicaoconteiner)
            assert r.status_code == 201
            assert r.is_json is True

        query = {'recinto': '00001',
                 'datainicial': '2019-01-01',
                 'datafinal': datetime.datetime.now().isoformat()}
        r = self.client.post('posicaoconteiner/list',
                             json=query)
        assert r.status_code == 200
        assert r.is_json is True
        lista = r.json
        print(r.json)
        assert len(lista) == 2
        query['altura'] = 0
        r = self.client.post('posicaoconteiner/list',
                             json=query)
        assert r.status_code == 200
        assert r.is_json is True
        lista = r.json
        assert len(lista) == 1
