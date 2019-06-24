import os
import sys
from base64 import b85encode

from cryptography.exceptions import InvalidSignature

import apiserver.authentication as authentication
import assinador
from apiserver.main import create_app
from apiserver.use_cases.usecases import UseCases
from basetest import BaseTestCase

sys.path.insert(0, 'apiserver')

RECINTOS = {
    '00001': '123',
    '00002': '456'
}


class Request:
    def __init__(self, headers: dict, json: dict):
        self.headers = headers
        self.json = json


class AuthenticationTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        os.environ['AUTHENTICATE'] = "YES"
        self.app = create_app(self.db_session, self.engine)
        self.client = self.app.app.test_client()
        self.posicaolote = {
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

    def tearDown(self) -> None:
        super().tearDown()
        os.environ['VERIFY_SIGN'] = "NO"

    def test_token(self):
        self.get_token()
        rv = self.client.post('posicaolote',
                              json=self.posicaolote,
                              headers=self.headers)
        print(rv.json)
        assert rv.status_code == 201
        assert rv.is_json is True

    def test_1api_is_blocked(self):
        # Não pega o token, headers vazios....
        rv = self.client.post('posicaolote',
                              json=self.posicaolote,
                              headers=self.headers)
        assert rv.status_code == 401
        assert rv.is_json is True

    def test_2view_is_blocked(self):
        # Não pega o token, headers vazios....
        query = {'IDEvento': 0,
                 'tipoevento': 'PosicaoLote'}
        rv = self.client.get('eventosnovos/get',
                             data=query,
                             headers=self.headers)
        assert rv.status_code == 401
        assert rv.is_json is True

    def test_recinto1(self):
        """Cria chave para recinto, manda chave

        """
        # login
        # manda recinto, senha
        # recebe chaveprivada, assina recinto
        os.environ['VERIFY_SIGN'] = "YES"
        with self.app.app.app_context():
            recinto = '00001'
            private_key_pem, assinado = UseCases.gera_chaves_recinto(
                self.db_session, recinto)
            private_key = assinador.load_private_key(private_key_pem)
            assinado = assinador.sign(recinto.encode('utf-8'),
                                      private_key)
            assinado = b85encode(assinado).decode('utf-8')
            # manda recinto encriptado com chave
            # recebe OK com chave correta
            payload = {'assinado': assinado, 'recinto': recinto}
            token = authentication.generate_token(payload)
            request = Request({'Authorization': 'Bearer %s' % token},
                              payload)
            assert authentication.valida_token_e_assinatura(request, self.db_session)[0] is True
            # manda recinto sem encriptar, recebe erro
            payload = {'assinado': recinto, 'recinto': recinto}
            token = authentication.generate_token(payload)
            request = Request({'Authorization': 'Bearer %s' % token},
                              payload)
            assert authentication.valida_token_e_assinatura(request, self.db_session)[0] is False
            # manda assinado com outra chave, recebe erro
            private_key2, _ = assinador.generate_keys()
            assinado2 = assinador.sign(recinto.encode('utf-8'),
                                       private_key2)
            payload2 = {'assinado': assinado2, 'recinto': recinto}
            token2 = authentication.generate_token(payload2)
            request2 = Request({'Authorization': 'Bearer %s' % token2},
                               payload2)
            assert authentication.valida_token_e_assinatura(request2, self.db_session)[0] is False


if __name__ == '__main__':
    private_key_pem = assinador.read_private_key()
    recinto = '00001'
    private_key = assinador.load_private_key(private_key_pem)
    assinado = assinador.sign(recinto.encode('utf8'),
                              private_key)
    print('recinto: %s' % recinto)
    print('assinado: %s' % assinado)
    # manda recinto encriptado com chave
    # recebe OK com chave correta
    payload = {'assinado': assinado, 'recinto': recinto}
    token = authentication.generate_token(payload)
    request = Request({'Authorization': 'Bearer %s' % token},
                      payload)
    authentication.valida_assinatura(request)
    # manda recinto sem encriptar, recebe erro
    payload = {'assinado': recinto, 'recinto': recinto}
    token = authentication.generate_token(payload)
    request = Request({'Authorization': 'Bearer %s' % token},
                      payload)
    try:
        authentication.valida_assinatura(request)
    except (InvalidSignature, TypeError) as err:
        print(err, 'CONFORME ESPERADO!!!')
