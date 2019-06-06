import datetime
import json
import random
import sys
from copy import deepcopy
from io import BytesIO

from apiserver.main import create_app
from basetest import BaseTestCase

sys.path.insert(0, 'apiserver')


def random_str(num, fila):
    result = ''
    for i in range(num):
        result += random.choice(fila)
    return result


def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])


"""
print('Creating memory database')
session, engine = orm.init_db('sqlite:///:memory:')
orm.Base.metadata.create_all(bind=engine)
with open(os.path.join(os.path.dirname(__file__),
                       'testes.json'), 'r') as json_in:
    testes = json.load(json_in)
"""


class APITestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        app = create_app(self.session, self.engine)
        self.client = app.app.test_client()

    def tearDown(self) -> None:
        super().tearDown()

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
        for data in ['dataevento', 'dataregistro', 'dataoperacao', 'dataliberacao',
                     'dataagendamento', 'datamodificacao', 'datacriacao', 'inicio', 'fim',
                     'datanascimento', 'fimvalidade', 'iniciovalidade']:
            if teste.get(data) is not None:
                teste.pop(data)
            if response_json.get(data) is not None:
                response_json.pop(data)
        sub_response = extractDictAFromB(teste, response_json)
        self.maxDiff = None
        eliminar = []
        for k, v in teste.items():
            if isinstance(v, list):
                self.compara_eventos(v[0], sub_response[k][0])
                eliminar.append(k)
        for k in eliminar:
            sub_response.pop(k)
            teste.pop(k)
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
            self.compara_eventos(deepcopy(teste), rv.json)

    def test4_evento_duplicado_409(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(), json=teste)
            rv = self.client.post(classe.lower(), json=teste)
            assert rv.status_code == 409
            assert rv.is_json is True

    def _api_insert(self, classe, cadastro):
        print(classe)
        rv = self.client.post(classe.lower(), json=cadastro)
        assert rv.status_code == 201
        assert rv.is_json is True

    def _api_load(self, classe, cadastro):
        print(classe)
        rv = self.client.get(classe.lower() + '/' + str(cadastro['IDEvento']))
        assert rv.status_code == 200
        assert rv.is_json is True
        self.compara_eventos(deepcopy(cadastro), rv.json)

    def _api_cadastro_fluxo(self, classe, acao):
        cadastro = self.cadastros[classe]
        url = classe.lower() + '/' + acao + '/' + str(cadastro['IDEvento'])
        print(url)
        rv = self.client.get(url)
        assert rv.status_code == 201
        assert rv.is_json is True
        rvjson = rv.json
        print(rvjson)
        assert rvjson['ativo'] is False
        assert rvjson['fim'] is not None

    def _cadastro(self, classe):
        cadastro = self.cadastros[classe]
        self._api_insert(classe, cadastro)
        self._api_load(classe, cadastro)

    def test_cadastrorepresentacao(self):
        classe = 'CadastroRepresentacao'
        self._cadastro(classe)
        self._api_cadastro_fluxo(classe, 'encerra')

    def test_InformacaoBloqueio(self):
        classe = 'InformacaoBloqueio'
        self._cadastro(classe)
        self._api_cadastro_fluxo(classe, 'desbloqueia')

    def test_AgendamentoConferencia(self):
        classe = 'AgendamentoConferencia'
        self._cadastro(classe)
        self._api_cadastro_fluxo(classe, 'cancela')

    def test_ArtefatoRecinto(self):
        classe = 'ArtefatoRecinto'
        self._cadastro(classe)


    def test_CredenciamentoPessoa(self):
        classe = 'CredenciamentoPessoa'
        self._cadastro(classe)
        self._api_cadastro_fluxo(classe, 'inativar')

    def test_CredenciamentoVeiculo(self):
        classe = 'CredenciamentoVeiculo'
        self._cadastro(classe)
        self._api_cadastro_fluxo(classe, 'inativar')

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
