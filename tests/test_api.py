import datetime
import json
import os
import random
from io import BytesIO
from unittest import TestCase

from apiserver.main import create_app
from apiserver.models import orm


def random_str(num, fila):
    result = ''
    for i in range(num):
        result += random.choice(fila)
    return result


def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])


print('Creating memory database')
session, engine = orm.init_db('sqlite:///:memory:')
orm.Base.metadata.create_all(bind=engine)
with open(os.path.join(os.path.dirname(__file__),
                       'testes.json'), 'r') as json_in:
    testes = json.load(json_in)


class APITestCase(TestCase):

    def setUp(self):
        self.engine = engine
        self.testes = testes
        app = create_app(session, engine)
        self.client = app.app.test_client()

    def tearDown(self) -> None:
        pass
        # orm.Base.metadata.create_all(bind=self.engine)


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

    def compara_eventos(self, teste, response_json):
        for data in ['dataevento', 'dataregistro', 'dataoperacao', 'dataliberacao', 'dataagendamento']:
            if teste.get(data) is not None:
                teste.pop(data)
            if response_json.get(data) is not None:
                response_json.pop(data)
        sub_response = extractDictAFromB(teste, response_json)
        self.maxDiff = None
        self.assertDictContainsSubset(teste, sub_response)

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
            self.compara_eventos(teste, rv.json)

    def test4_evento_duplicado_409(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json=teste)
            assert rv.status_code == 409
            assert rv.is_json is True

    def cadastro_fluxo(self, cadastro, classe, acao):
        rv = self.client.post(classe.lower(), json=cadastro)
        assert rv.status_code == 201
        assert rv.is_json is True
        response_token = rv.json
        rv = self.client.get(classe.lower() + '/' + str(cadastro['IDEvento']))
        assert rv.status_code == 200
        assert rv.is_json is True
        self.compara_eventos(cadastro, rv.json)
        rv = self.client.post(classe.lower() + '/' +
                              str(cadastro['IDEvento']) + '/' + acao)
        assert rv.status_code == 201
        assert rv.is_json is True

    def test_cadastrorepresentacao(self):
        cadastro = {
            "IDEvento": 0,
            "dataevento": "2019-06-03T23:23:02.889Z",
            "dataregistro": "2019-06-03T23:23:02.889Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "cpfcnpjrepresentado": "string",
            "cpfrepresentante": "string",
            "inicio": "2019-06-03T23:23:02.889Z"
        }

    def test_(self):

        informacaobloqueio = {
        "IDEvento": 0,
        "dataevento": "2019-06-03T23:33:36.294Z",
        "dataregistro": "2019-06-03T23:33:36.294Z",
        "operadorevento": "string",
        "operadorregistro": "string",
        "retificador": True,
        "documentotransporte": "string",
        "motivo": "string",
        "numero": "string",
        "placa": "string",
        "solicitante": "RFB",
        "tipodocumentotransporte": "CE"
        }

    def test_(self):

        agendamentoconferencia = {
            "IDEvento": 0,
            "dataevento": "2019-06-03T23:35:22.842Z",
            "dataregistro": "2019-06-03T23:35:22.842Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "retificador": true,
            "artefato": "string",
            "dataagendamento": "2019-06-03T23:35:22.842Z",
            "documentotransporte": "string",
            "local": "string",
            "numero": "string",
            "placa": "string",
            "placasemireboque": "string",
            "tipodocumento": "RG"}

    def test_(self):

        artefatorecinto = {
            "IDEvento": 0,
            "dataevento": "2019-06-03T23:35:22.844Z",
            "dataregistro": "2019-06-03T23:35:22.844Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "retificador": True,
            "codigo": "string",
            "coordenadasartefato": [
                {
                    "lat": 0,
                    "long": 0,
                    "ordem": 0
                }
            ],
            "tipoartefato": "Area (poligono)"
        }

    def cria_lote(self):
        letras = 'ABCDEFGHIJKLMNOPQRSTUVXZ'
        numeros = ''.join([str(i) for i in range(10)])
        textos = 'ABCDEFGHIJKLMNOPQRSTUVXZ          abcdefghijklmnopqrstuvwxyz'
        placas = [random_str(3, letras) + random_str(5, numeros) for i in range(100)]
        reboques = [random_str(3, letras) + random_str(5, numeros) for i in range(200)]
        conteineres = [random_str(4, letras) + random_str(7, numeros) for i in range(200)]
        operadores = [random_str(11, letras) for i in range(10)]
        motoristas = [random_str(11, letras) for i in range(50)]
        textos = [random_str(random.randint(10, 20), textos) for i in range(50)]

        self.pesagens = []
        for r in range(10):
            data = datetime.datetime.now().isoformat()
            operador = random.choice(operadores)
            conteiner = random.choice(conteineres)
            tara = random.randint(9000, 12000)
            pesobrutodeclarado = random.randint(3000, 15000)
            pesobalanca = tara + random.randint(-2000, 2000)
            placa = random.choice(placas)
            reboque = random.choice(reboques)
            texto = random.choice(textos)
            pesagem = \
                {'IDEvento': r + 500,
                 'capturaautomatica': True,
                 'numero': random.choice(conteineres),
                 'dataevento': data,
                 'dataregistro': data,
                 'retificador': False,
                 'documentotransporte': texto,
                 'operadorevento': operador,
                 'operadorregistro': operador,
                 'pesobalanca': pesobalanca,
                 'pesobrutodeclarado': pesobrutodeclarado,
                 'placa': placa,
                 'placasemireboque': reboque,
                 'taraconjunto': tara,
                 'tipodocumentotransporte': 'CE'}
            self.pesagens.append(pesagem)
            json_pesagens = {'PesagemMaritimo': self.pesagens}
            with open('test.json', 'w', encoding='utf-8', newline='') as json_out:
                json.dump(json_pesagens, json_out)

    def test_eventos_lote(self):
        self.cria_lote()
        data = {'file': (BytesIO(open('test.json', 'rb').read()), 'test.json')}
        r = self.client.post('set_eventos_novos', data=data)
        assert r.status_code == 201
        query = {'IDEvento': 0,
                 'tipoevento': 'PesagemMaritimo'}
        r = self.client.get('get_eventos_novos',
                            data=query)
        assert r.status_code == 200

        print(r.data)
        assert r.is_json is True
        assert len(r.json) == 10
        self.compara_eventos(self.pesagens[0], r.json[0])

    # TODO: Testar fluxo de Cadastro Representacao
