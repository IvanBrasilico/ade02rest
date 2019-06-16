import logging
import os
import pickle
import time
from base64 import b85decode

import six
from flask import request, jsonify, g, current_app
from jose import JWTError, jwt
from werkzeug.exceptions import Unauthorized

import assinador
from apiserver.api import _response
from apiserver.models.orm import ChavePublicaRecinto


def make_secret():
    try:
        with open('SECRET', 'rb') as secret:
            secret = pickle.load(secret)
    except (FileNotFoundError, pickle.PickleError):
        secret = os.urandom(24)
        with open('SECRET', 'wb') as out:
            pickle.dump(secret, out, pickle.HIGHEST_PROTOCOL)
    return secret


JWT_ISSUER = 'api-recintos'
JWT_SECRET = str(make_secret())
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'


def generate_token(recinto):
    # TODO: Validar usuario e senha
    timestamp = _current_timestamp()
    payload = {
        'iss': JWT_ISSUER,
        'iat': int(timestamp),
        'exp': int(timestamp + JWT_LIFETIME_SECONDS),
        'recinto': str(recinto['recinto']),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        logging.error(e, exc_info=True)
        six.raise_from(Unauthorized, e)
    except Exception as err:
        logging.error(err, exc_info=True)
        raise Exception('Erro ao analisar token: %s Mensagem de erro: %s' %
                        (token, (str(err))))


def get_secret(user, token_info) -> str:
    return """
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    """.format(user=user, token_info=token_info)


def _current_timestamp() -> int:
    return int(time.time())


def recorta_token_header(headers):
    token = headers.get('Authorization')
    if token:
        token = token.split()
        if len(token) == 2:
            token = token[1]
    return token


def valida_assinatura(request, db_session=None) -> [bool, str]:
    """Analisa request e retorna True ou False

    1. Retira token do header
    2. Decodifica token
    3. Pega campo recinto e recupera chave publica do recinto do banco
    4. Valida assinatura (campo assinado tem que estar no request e corresponder
    ao codigo do recinto assinado com sua chave privada)

    :param request: Objeto request
    :param db_session: Conexão ao BD
    :return: Sucesso(True, False), mensagem

    """
    token = recorta_token_header(request.headers)
    # TODO: A linha abaixo "faz bypass" caso não seja passado o token
    # Definir como e onde ativar a autenticacao por duas etapas
    if token is None:
        return False, 'Token não fornecido'
    try:
        if db_session is None:
            db_session = current_app.config['db_session']
        # print(token)
        decoded_token = decode_token(token)
        if request.json and decoded_token and isinstance(decoded_token, dict):
            recinto = decoded_token.get('recinto')
            if g:
                g.recinto = recinto
            assinado = request.json.get('assinado')
            if assinado:
                assinado = b85decode(assinado.encode('utf-8'))
                print('recinto: %s' % recinto)
                print('assinado: %s' % assinado)
                public_key_pem = ChavePublicaRecinto.get_public_key(db_session, recinto)
                public_key = assinador.load_public_key(public_key_pem)
                assinador.verify(assinado, recinto.encode('utf8'), public_key)
    except Exception as err:
        logging.error(err, exc_info=True)
        return False, str(err)
    return True, None


def configure_signature(app):
    @app.before_request
    def before_request():
        print(request.path)
        if request.path in ['/auth', '/privatekey']:
            return
        sucesso, err_msg = valida_assinatura(request)
        if sucesso is False:
            return jsonify(
                _response('Token inválido ou Assinatura inválida: %s' % err_msg, 401)
            ), 401
