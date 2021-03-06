import datetime
import os
import sys
from base64 import b64decode, b64encode
from io import BytesIO

from apiserver.main import create_app
from tests.basetest import BaseTestCase

sys.path.insert(0, 'apiserver')


class ViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        app = create_app(self.db_session, self.engine)
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
                    "datacriacao": "2019-05-31T02:55:50.300000Z",
                    "datamodificacao": "2019-05-31T02:55:50.300000Z"
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
        self.image = open(os.path.join(images_dir, self.filename), 'rb')
        self.base64_bytes = b64encode(self.image.read())
        # base64_string = base64_bytes.decode('utf-8')
        self.file = (BytesIO(self.base64_bytes), self.filename)
        self.get_token()

    def tearDown(self) -> None:
        super().tearDown()

    def test0_home(self):
        response = self.client.get('/', headers=self.headers)
        assert response.status_code == 200
        assert response.is_json is False
        assert b'html' in response.data

    def test1_inclui_inspecao(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo,
                             headers=self.headers)
        assert r.status_code == 201
        assert r.is_json
        r = self.client.get('inspecaonaoinvasiva/1001', headers=self.headers)
        assert r.status_code == 200
        assert r.is_json
        response_json = r.json
        teste = self.inspecao_modelo
        for data in ['dataevento', 'dataregistro', 'dataoperacao',
                     'dataliberacao', 'dataagendamento']:
            if teste.get(data) is not None:
                teste.pop(data)
            if response_json.get(data) is not None:
                response_json.pop(data)

        self.compare_dict(teste,
                          response_json)

    def test2_upload_invalid_file(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo,
                             headers=self.headers)
        file = (None, None, 'image/jpeg')

        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': file}
        # headers['Content-Type'] = 'image/jpeg'
        response = self.client.post('upload_file',
                                    data=data,
                                    headers=self.headers)
        assert response.status_code == 400
        assert response.is_json is True

    def test3_arquivo_invalido(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo,
                             headers=self.headers)
        file = (b'', '')
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': file}
        # headers['Content-Type'] = 'image/jpeg'
        r = self.client.post('upload_file',
                             data=data,
                             headers=self.headers)
        assert r.status_code == 400
        assert r.is_json

    def test4_evento_naoexistente(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo,
                             headers=self.headers)
        file = (None, None, 'image/jpeg')
        data = {'IDEvento': '100000',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': self.file}
        r = self.client.post('upload_file',
                             data=data,
                             content_type='multipart/form-data',
                             headers=self.headers)
        assert r.status_code == 404
        assert r.is_json is True

    def test5_upload_file(self):
        r = self.client.post('inspecaonaoinvasiva',
                             json=self.inspecao_modelo,
                             headers=self.headers)
        # print(self.image)
        # print(self.filename)
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva',
                'file': self.file}

        # headers['Content-Type'] = 'image/jpeg'
        r = self.client.post('upload_file',
                             data=data,
                             content_type='multipart/form-data',
                             headers=self.headers)
        print(r.data)
        assert r.status_code == 201
        assert r.is_json
        data = {'IDEvento': '1001',
                'tipoevento': 'InspecaonaoInvasiva'}
        r = self.client.get('get_file', data=data, headers=self.headers)
        assert r.status_code == 200
        assert r.is_json is False
        if r.data is not None and r.data is not b'':
            assert b64decode(r.data) == self.base64_bytes

    def test_posicaoconteiner_list(self):
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
                                 json=posicaoconteiner,
                                 headers=self.headers)
            assert r.status_code == 201
            assert r.is_json is True

        query = {'recinto': '00001',
                 'datainicial': '2019-01-01',
                 'datafinal': datetime.datetime.now().isoformat()}
        r = self.client.post('posicaoconteiner/list',
                             json=query,
                             headers=self.headers)
        assert r.status_code == 200
        assert r.is_json is True
        lista = r.json
        print(r.json)
        assert len(lista) == 2
        query['altura'] = 0
        r = self.client.post('posicaoconteiner/list',
                             json=query,
                             headers=self.headers)
        assert r.status_code == 200
        assert r.is_json is True
        lista = r.json
        assert len(lista) == 1

    def test_eventos_lote(self):
        self.cria_lote()
        data = {'file': (BytesIO(open('test.json', 'rb').read()), 'test.json')}
        r = self.client.post('eventosnovos/upload',
                             data=data,
                             headers=self.headers)
        assert r.status_code == 201
        query = {'IDEvento': 0,
                 'tipoevento': 'PesagemMaritimo'}
        r = self.client.get('eventosnovos/get',
                            data=query,
                            headers=self.headers)
        assert r.status_code == 200

        print(r.data)
        assert r.is_json is True
        assert len(r.json) == 10
        self.compara_eventos(self.pesagens[0], r.json[0])

    def test_get_file_errors(self):
        data = {'IDEvento': '42',
                'tipoevento': 'InspecaonaoInvasiva'}
        r = self.client.get('get_file', data=data, headers=self.headers)
        assert r.status_code == 404
        assert r.is_json is True
        data = {'tipoevento': 'Festa'}
        r = self.client.get('get_file', data=data, headers=self.headers)
        assert r.status_code == 400
        assert r.is_json is True


