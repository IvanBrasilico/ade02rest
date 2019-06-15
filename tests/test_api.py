import datetime
import sys
from base64 import b85encode
from copy import deepcopy
from io import BytesIO

import assinador
from apiserver.main import create_app
from basetest import BaseTestCase

sys.path.insert(0, 'apiserver')


def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])


class APITestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        app = create_app(self.db_session, self.engine)
        self.client = app.app.test_client()
        self.get_token()

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
            rv = self.client.post(classe.lower(),
                                  json=teste,
                                  headers=self.headers)
            assert rv.status_code == 201
            assert rv.is_json is True
            response_token = rv.json
            rv = self.client.get(classe.lower() + '/' + str(teste['IDEvento']),
                                 headers=self.headers)
            assert rv.status_code == 200
            assert rv.is_json is True
            self.compara_eventos(deepcopy(teste), rv.json)

    def test4_evento_duplicado_409(self):
        for classe, teste in self.testes.items():
            print(classe)
            rv = self.client.post(classe.lower(),
                                  json=teste,
                                  headers=self.headers)
            rv = self.client.post(classe.lower(),
                                  json=teste,
                                  headers=self.headers)
            assert rv.status_code == 409
            assert rv.is_json is True

    def _api_insert(self, classe, cadastro):
        print(classe)
        rv = self.client.post(classe.lower(),
                              json=cadastro,
                              headers=self.headers)
        assert rv.status_code == 201
        assert rv.is_json is True

    def _api_load(self, classe, cadastro):
        print(classe)
        rv = self.client.get(classe.lower() + '/' + str(cadastro['IDEvento']),
                             headers=self.headers)
        assert rv.status_code == 200
        assert rv.is_json is True
        self.compara_eventos(deepcopy(cadastro), rv.json)

    def _api_cadastro_fluxo(self, classe, acao):
        cadastro = self.cadastros[classe]
        url = classe.lower() + '/' + acao + '/' + str(cadastro['IDEvento'])

        print(url)
        rv = self.client.get(url, headers=self.headers)
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

    def test_AgendamentoAcessoVeiculo(self):
        classe = 'AgendamentoAcessoVeiculo'
        self._cadastro(classe)

    def test_eventos_lote(self):
        self.cria_lote()
        data = {'file': (BytesIO(open('test.json', 'rb').read()), 'test.json')}
        r = self.client.post('eventosnovos/upload', data=data,
                             headers=self.headers)
        assert r.status_code == 201
        query = {'IDEvento': 0,
                 'tipoevento': 'PesagemMaritimo'}
        r = self.client.post('eventosnovos/list',
                             json=query)
        assert r.status_code == 200

        print(r.data)
        assert r.is_json is True
        assert len(r.json) == 10
        self.compara_eventos(self.pesagens[0], r.json[0])

    def test_eventos_filter(self):
        self.cria_lote()
        data = {'file': (BytesIO(open('test.json', 'rb').read()), 'test.json')}
        r = self.client.post('eventosnovos/upload', data=data,
                             headers=self.headers)
        assert r.status_code == 201
        datainicial = datetime.datetime.now() - datetime.timedelta(days=1)
        query = {'datainicial': datainicial.isoformat(),
                 'datafinal': datetime.datetime.now().isoformat(),
                 'tipoevento': 'PesagemMaritimo'}
        r = self.client.post('eventos/filter',
                             json=query)
        assert r.status_code == 200

        print(r.data)
        assert r.is_json is True
        assert len(r.json) == 10

    def test_auth(self):
        recinto_senha = {'recinto': self.recinto,
                         'senha': 'certificado'}
        rv = self.client.post('/auth', json=recinto_senha)
        assert rv is not None
        assert rv.status_code == 200
        token = rv.data
        assert token is not None
        assert isinstance(token, bytes)
        assert len(token) > 40

    def test_signed_payload(self):
        # TODO: Este é um exemplo da sequência de TWO WAY authentication
        # Em outra aplicação ou nesta, o Representante Legal deve efetuar
        # logon para definir a senha do recinto, gerar as chaves e baixar
        # a chave privada
        recinto = '00001'
        recinto_senha = {'recinto': recinto,
                         'senha': 'senha'}
        posicaolote = {
            "IDEvento": 42,
            "dataevento": "2019-06-14T11:18:43.287Z",
            "dataregistro": "2019-06-14T11:18:43.287Z",
            "operadorevento": "string",
            "operadorregistro": "string",
            "retificador": False,
            "numerolote": 0,
            "posicao": "string",
            "qtdevolumes": "string"
        }
        # 1. Faz dowload da chave privada, assina codigo recinto com ela
        # Este endpoint deverá ser acessado pelo Representante Legal com e-CPF,
        # preferencialmente
        rv = self.client.post('/privatekey', json={'recinto': recinto})
        assert rv.json
        pem = rv.json.get('pem')
        private_key = assinador.load_private_key(pem.encode('utf-8'))
        assinado = assinador.sign(recinto.encode('utf-8'),
                                  private_key)
        # 2. Faz autenticação na aplicação local e pega token
        rv = self.client.post('/auth', json=recinto_senha)
        token = rv.data
        headers = {'Authorization': 'Bearer %s' % token.decode('utf8')}
        # 3. Manda recinto encriptado com chave junto com Evento. Codigo recinto vai no token
        # Assim, a validação é pelo token e pelo certificado digital(chave privada)
        posicaolote['assinado'] = b85encode(assinado).decode('utf-8')
        rv = self.client.post('/posicaolote', json=posicaolote,
                              headers=headers)
        assert rv.status_code == 201
