from unittest import TestCase

from cryptography.exceptions import InvalidSignature

import apiserver.authentication as authentication
import assinador
from basetest import BaseTestCase
from apiserver.use_cases.usecases import UseCases

RECINTOS = {
    '00001': '123',
    '00002': '456'
}

class Request:
    def __init__(self, headers: dict, json:dict):
        self.headers = headers
        self.json = json

class AuthenticationTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def test_recinto1(self):
        """Cria chave para recinto, manda chave

        """
        # login
        # manda recinto, senha
        # recebe chaveprivada, assina recinto
        recinto = '00001'
        private_key_pem = UseCases.gera_chaves_recinto(self.db_session, recinto)
        private_key = assinador.load_private_key(private_key_pem)
        assinado = assinador.sign(recinto.encode('utf-8'),
                                  private_key)
        # manda recinto encriptado com chave
        # recebe OK com chave correta
        payload = {'assinado': assinado, 'recinto': recinto}
        token = authentication.generate_token(payload)
        request = Request({'Authorization':  'Bearer %s' % token},
                          payload)
        assert authentication.valida_assinatura(request, self.db_session) is True
        # manda recinto sem encriptar, recebe erro
        payload = {'assinado': recinto, 'recinto': recinto}
        token = authentication.generate_token(payload)
        request = Request({'Authorization':  'Bearer %s' % token},
                          payload)
        assert authentication.valida_assinatura(request, self.db_session) is False



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
